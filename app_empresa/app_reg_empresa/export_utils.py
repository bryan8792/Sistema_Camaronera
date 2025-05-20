import xlsxwriter
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO


def export_to_excel(data, filename, sheet_name='Hoja1'):
    """
    Exporta datos a un archivo Excel

    Args:
        data: Diccionario con los datos a exportar (headers, rows, money_columns, percent_columns, column_widths, subtitle)
        filename: Nombre del archivo sin extensión
        sheet_name: Nombre de la hoja de Excel

    Returns:
        HttpResponse con el archivo Excel
    """
    # Crear respuesta HTTP con el tipo MIME correcto
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"'

    # Crear libro de Excel en memoria
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet(sheet_name)

    # Formatos
    header_format = workbook.add_format({
        'bold': True,
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': '#D7E4BC',
        'border': 1
    })

    money_format = workbook.add_format({
        'num_format': '$#,##0.00',
        'border': 1
    })

    percent_format = workbook.add_format({
        'num_format': '0.00%',
        'border': 1
    })

    date_format = workbook.add_format({
        'num_format': 'dd/mm/yyyy',
        'border': 1
    })

    cell_format = workbook.add_format({
        'border': 1
    })

    title_format = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center'
    })

    subtitle_format = workbook.add_format({
        'italic': True,
        'align': 'center'
    })

    # Título y subtítulo
    worksheet.merge_range('A1:I1', f'Reporte: {filename}', title_format)

    if 'subtitle' in data:
        worksheet.merge_range('A2:I2', data['subtitle'], subtitle_format)
        row_offset = 3
    else:
        row_offset = 2

    # Escribir encabezados
    for col, header in enumerate(data['headers']):
        worksheet.write(row_offset - 1, col, header, header_format)

    # Escribir datos
    for row_idx, row_data in enumerate(data['rows']):
        for col_idx, cell_value in enumerate(row_data):
            # Aplicar formato según el tipo de columna
            if 'money_columns' in data and col_idx in data['money_columns']:
                worksheet.write(row_idx + row_offset, col_idx, cell_value, money_format)
            elif 'percent_columns' in data and col_idx in data['percent_columns']:
                worksheet.write(row_idx + row_offset, col_idx, cell_value / 100, percent_format)
            elif isinstance(cell_value, (int, float)):
                worksheet.write(row_idx + row_offset, col_idx, cell_value, cell_format)
            else:
                worksheet.write(row_idx + row_offset, col_idx, cell_value, cell_format)

    # Ajustar anchos de columna
    if 'column_widths' in data:
        for col, width in enumerate(data['column_widths']):
            worksheet.set_column(col, col, width)
    else:
        for col, header in enumerate(data['headers']):
            worksheet.set_column(col, col, len(header) + 2)

    # Cerrar libro y obtener datos
    workbook.close()
    output.seek(0)

    # Escribir datos al response
    response.write(output.getvalue())
    return response


def export_to_pdf(data, filename, title, landscape_orientation=False):
    """
    Exporta datos a un archivo PDF

    Args:
        data: Diccionario con los datos a exportar (headers, rows, money_columns, percent_columns, subtitle)
        filename: Nombre del archivo sin extensión
        title: Título del reporte
        landscape_orientation: Si es True, el PDF se genera en orientación horizontal

    Returns:
        HttpResponse con el archivo PDF
    """
    # Crear respuesta HTTP con el tipo MIME correcto
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'

    # Configurar tamaño de página
    page_size = landscape(letter) if landscape_orientation else letter

    # Crear documento PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=page_size, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)

    # Estilos
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    subtitle_style = styles['Italic']

    # Elementos del PDF
    elements = []

    # Título
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 0.25 * inch))

    # Subtítulo
    if 'subtitle' in data:
        elements.append(Paragraph(data['subtitle'], subtitle_style))
        elements.append(Spacer(1, 0.25 * inch))

    # Preparar datos para la tabla
    table_data = [data['headers']]

    # Formatear datos
    for row in data['rows']:
        formatted_row = []
        for col_idx, cell_value in enumerate(row):
            if 'money_columns' in data and col_idx in data['money_columns']:
                formatted_row.append(f"${cell_value:,.2f}")
            elif 'percent_columns' in data and col_idx in data['percent_columns']:
                formatted_row.append(f"{cell_value:.2f}%")
            else:
                formatted_row.append(str(cell_value))
        table_data.append(formatted_row)

    # Crear tabla
    table = Table(table_data)

    # Estilo de tabla
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])

    # Aplicar estilo a la última fila (totales)
    style.add('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey)
    style.add('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold')

    table.setStyle(style)
    elements.append(table)

    # Construir PDF
    doc.build(elements)

    # Obtener valor del PDF
    pdf = buffer.getvalue()
    buffer.close()

    # Escribir PDF al response
    response.write(pdf)
    return response

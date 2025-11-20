let tabla_kardex, tabla_consumo;

document.addEventListener('DOMContentLoaded', function() {
    console.log('[v0] Inicializando Kardex Bodega');
    inicializarDateRange();
    inicializarTablas();
    cargarDatos();

    // Botones
    document.getElementById('btn_buscar').addEventListener('click', cargarDatos);
    document.getElementById('btn_excel').addEventListener('click', exportarExcel);
    document.getElementById('btn_pdf').addEventListener('click', exportarPDF);
    document.getElementById('btn_imprimir').addEventListener('click', imprimirReporte);
});

function inicializarDateRange() {
    console.log('[v0] Inicializando DateRangePicker');

    const hoy = moment();
    const hace30dias = moment().subtract(30, 'days');

    $('#daterange').daterangepicker({
        startDate: hace30dias,
        endDate: hoy,
        locale: {
            format: 'YYYY-MM-DD',
            applyLabel: 'Aplicar',
            cancelLabel: 'Cancelar',
            customRangeLabel: 'Personalizado',
            daysOfWeek: ['Do', 'Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sa'],
            monthNames: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        }
    });

    console.log('[v0] DateRangePicker inicializado');
}

function inicializarTablas() {
    console.log('[v0] Inicializando DataTables');

    tabla_kardex = $('#tb_kardex_bodega').DataTable({
        language: {
            url: '//cdn.datatables.net/plug-ins/1.10.15/i18n/Spanish.json'
        },
        paging: false,
        searching: true,
        ordering: true,
        info: false,
        dom: '<"top">rt<"bottom"><"clear">'
    });

    tabla_consumo = $('#tb_consumo_piscinas').DataTable({
        language: {
            url: '//cdn.datatables.net/plug-ins/1.10.15/i18n/Spanish.json'
        },
        pageLength: 20,
        paging: true,
        searching: true,
        ordering: true,
        dom: 'lrtip'
    });

    console.log('[v0] DataTables inicializadas');
}

function cargarDatos() {
    const daterange = $('#daterange').val().split(' - ');
    const start_date = daterange[0];
    const end_date = daterange[1];

    console.log('[v0] Cargando datos kardex - Rango:', start_date, 'a', end_date);

    // Cargar Kardex Bodega
    $.ajax({
        type: 'POST',
        url: window.location.pathname,
        data: {
            action: 'get_kardex_data',
            start_date: start_date,
            end_date: end_date,
            csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
        },
        dataType: 'json',
        success: function(data) {
            console.log('[v0] Datos kardex recibidos:', data);
            tabla_kardex.clear();

            let totalStockGlobal = 0;
            let totalConsumoGlobal = 0;

            $.each(data, function(i, row) {
                tabla_kardex.row.add([
                    row.nombre_producto,
                    row.presentacion || '-',
                    row.unidad || '-',
                    parseFloat(row.stock_psm).toFixed(2),
                    parseFloat(row.stock_bio).toFixed(2),
                    parseFloat(row.stock_total).toFixed(2),
                    parseFloat(row.consumo_total).toFixed(2)
                ]).draw();

                totalStockGlobal += parseFloat(row.stock_total);
                totalConsumoGlobal += parseFloat(row.consumo_total);
            });

            // Fila de totales
            tabla_kardex.row.add([
                '<strong>TOTAL GENERAL</strong>',
                '',
                '',
                '',
                '',
                '<strong>' + totalStockGlobal.toFixed(2) + '</strong>',
                '<strong>' + totalConsumoGlobal.toFixed(2) + '</strong>'
            ]).draw();

            tabla_kardex.draw();
        },
        error: function(xhr) {
            console.error('[v0] Error al cargar kardex:', xhr);
            alert('Error al cargar datos del kardex');
        }
    });

    // Cargar Consumo por Piscinas
    $.ajax({
        type: 'POST',
        url: window.location.pathname,
        data: {
            action: 'get_consumo_piscinas',
            start_date: start_date,
            end_date: end_date,
            csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
        },
        dataType: 'json',
        success: function(data) {
            console.log('[v0] Consumo piscinas recibidos:', data);
            tabla_consumo.clear();

            $.each(data, function(i, row) {
                tabla_consumo.row.add([
                    row.empresa,
                    row.piscina,
                    row.fecha,
                    row.producto,
                    parseFloat(row.cantidad).toFixed(2),
                    row.unidad,
                    row.responsable || '-',
                    row.numero_guia || '-'
                ]).draw();
            });

            tabla_consumo.draw();
        },
        error: function(xhr) {
            console.error('[v0] Error al cargar consumo:', xhr);
        }
    });
}

function exportarExcel() {
    const daterange = $('#daterange').val();

    console.log('[v0] Exportando Excel - Rango:', daterange);

    // Crear un libro de Excel
    let html = '';
    html += '<table border="1">';
    html += '<tr><td colspan="7"><strong>KARDEX BODEGA DE INSUMOS</strong></td></tr>';
    html += '<tr><td colspan="7"><strong>Período: ' + daterange + '</strong></td></tr>';
    html += '<tr><td colspan="7"></td></tr>';
    html += '<tr><td colspan="7"><strong>CONSOLIDADO DE STOCK</strong></td></tr>';
    html += tabla_kardex.$('tr').parent().html();
    html += '<tr><td colspan="7"></td></tr>';
    html += '<tr><td colspan="7"><strong>DETALLE DE CONSUMO POR PISCINAS</strong></td></tr>';
    html += tabla_consumo.$('tr').parent().html();
    html += '</table>';

    descargarExcel(html, 'Kardex_Insumos_' + moment().format('YYYY-MM-DD') + '.xls');
}

function exportarPDF() {
    const daterange = $('#daterange').val();

    console.log('[v0] Exportando PDF - Rango:', daterange);

    const ventana = window.open('', '', 'height=600,width=900');

    ventana.document.write('<html><head><title>Kardex Bodega Insumos</title>');
    ventana.document.write('<style>');
    ventana.document.write('body { font-family: Arial; margin: 20px; }');
    ventana.document.write('table { width: 100%; border-collapse: collapse; margin-top: 20px; }');
    ventana.document.write('th { background-color: #3498DB; color: white; padding: 8px; text-align: center; }');
    ventana.document.write('td { border: 1px solid #999; padding: 6px; text-align: center; }');
    ventana.document.write('td:first-child { text-align: left; }');
    ventana.document.write('.section-title { background-color: #34495E; color: white; padding: 10px; margin-top: 20px; font-weight: bold; }');
    ventana.document.write('h2 { text-align: center; color: #34495E; }');
    ventana.document.write('.header-info { text-align: center; margin-bottom: 20px; }');
    ventana.document.write('</style></head><body>');

    ventana.document.write('<h2>KARDEX BODEGA DE INSUMOS</h2>');
    ventana.document.write('<div class="header-info">');
    ventana.document.write('<p><strong>Período:</strong> ' + daterange + '</p>');
    ventana.document.write('<p><strong>Fecha de Generación:</strong> ' + moment().format('DD/MM/YYYY HH:mm') + '</p>');
    ventana.document.write('</div>');

    ventana.document.write('<div class="section-title">CONSOLIDADO DE STOCK Y CONSUMO</div>');
    ventana.document.write(tabla_kardex.table().container().innerHTML);

    ventana.document.write('<div class="section-title" style="page-break-before: always;">DETALLE DE CONSUMO POR PISCINAS</div>');
    ventana.document.write(tabla_consumo.table().container().innerHTML);

    ventana.document.write('</body></html>');
    ventana.document.close();
    ventana.print();
}

function imprimirReporte() {
    console.log('[v0] Imprimiendo reporte');
    window.print();
}

function descargarExcel(html, nombreArchivo) {
    const uri = 'data:application/vnd.ms-excel;base64,';
    const template = `
        <html xmlns:x="urn:schemas-microsoft-com:office:excel">
            <head>
                <meta charset="UTF-8">
                <style>
                    table { border-collapse: collapse; width: 100%; }
                    th { background-color: #3498DB; color: white; text-align: center; padding: 8px; border: 1px solid #999; }
                    td { border: 1px solid #999; padding: 6px; }
                    .section-title { background-color: #34495E; color: white; font-weight: bold; padding: 8px; }
                </style>
            </head>
            <body>
                {table}
            </body>
        </html>
    `;

    const tabla = template.replace('{table}', html);
    const base64 = btoa(unescape(encodeURIComponent(tabla)));

    const link = document.createElement('a');
    link.href = uri + base64;
    link.download = nombreArchivo;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

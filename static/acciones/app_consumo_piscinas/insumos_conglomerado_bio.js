/* global moment, XLSX, pdfMake, $ */
var date_range = null;
var multiplicadora = 0, total_stock = 0;
var tb_piscinas_por_insumos;
var total, group_assoc, group_total, total_seg;
var groupColumn = 1;
var total_ing = 0;
var total_eg = 0;
var cant_tot = 0, tot = 0;
var date_now = moment().format('YYYY-MM-DD');
var datos_procesados = []; // Variable global para almacenar datos procesados

function format(d) {
    console.log('d');
    console.log(d);
    var html = '<table class="table">';
    html += '<thead class="thead-dark">';
    html += '<tr><th scope="col">Piscina</th>';
    html += '<th scope="col">Fecha</th>';
    html += '<th scope="col">Cantidad</th>';
    html += '<th scope="col">Costo</th>';
    html += '<th scope="col">Total</th></tr>';
    html += '</thead>';
    html += '<tbody>';
    html+='<tr>'
    html+='<td>'+d.piscinas+'</td>'
    html+='<td>'+d.fecha_ingreso+'</td>'
    html+='<td>'+d.cantidad_egreso+'</td>'
    html+='<td>'+d.producto_empresa.nombre_prod.costo+'</td>'
    html+='<td>'+eval(d.cantidad_egreso*d.producto_empresa.nombre_prod.costo)+'</td>'
    html+='</tr>';
    html += '</tbody>';
    return html;
}

// Funcion para obtener el periodo formateado
function getPeriodo() {
    var start_date = date_now;
    var end_date = date_now;
    if (date_range !== null) {
        start_date = date_range.startDate.format('YYYY-MM-DD');
        end_date = date_range.endDate.format('YYYY-MM-DD');
    }
    return start_date + ' a ' + end_date;
}

// Funcion para exportar a Excel manualmente
function exportarExcel() {
    if (datos_procesados.length === 0) {
        alert('No hay datos para exportar');
        return;
    }

    var fecha_hora = 'Fecha: ' + moment().format('DD/MM/YYYY') + ' - Hora: ' + moment().format('HH:mm:ss');
    var periodo = getPeriodo();
    
    // Crear datos para Excel
    var ws_data = [];
    
    // Fila 1: Fecha y hora
    ws_data.push([fecha_hora, '', '', '', '']);
    // Filas vacias
    ws_data.push(['', '', '', '', '']);
    ws_data.push(['', '', '', '', '']);
    // Titulo centrado
    ws_data.push(['', '', 'RESUMEN CONSUMO BIO', '', '']);
    // Periodo
    ws_data.push(['', '', 'Periodo: ' + periodo, '', '']);
    // Fila vacia
    ws_data.push(['', '', '', '', '']);
    // Encabezados
    ws_data.push(['LINEA', 'SUB-LINEA', 'CANTIDAD', 'COSTO', 'TOTAL']);
    
    // Datos
    var total_cantidad = 0;
    var total_total = 0;
    
    datos_procesados.forEach(function(item) {
        ws_data.push([
            'INSUMOS',
            item.nombre,
            item.cantidad,
            item.costo,
            item.total
        ]);
        total_cantidad += item.cantidad;
        total_total += item.total;
    });
    
    // Fila de totales
    ws_data.push(['Cantidad Total', 'Cantidad Total', total_cantidad.toFixed(2), '', total_total.toFixed(2)]);
    
    // Crear libro de Excel
    var wb = XLSX.utils.book_new();
    var ws = XLSX.utils.aoa_to_sheet(ws_data);
    
    // Ajustar anchos de columna
    ws['!cols'] = [
        {wch: 20}, // LINEA
        {wch: 30}, // SUB-LINEA
        {wch: 15}, // CANTIDAD
        {wch: 18}, // COSTO
        {wch: 15}  // TOTAL
    ];
    
    // Merge cells para titulo
    ws['!merges'] = [
        {s: {r: 3, c: 0}, e: {r: 3, c: 4}}, // Titulo
        {s: {r: 4, c: 0}, e: {r: 4, c: 4}}  // Periodo
    ];
    
    XLSX.utils.book_append_sheet(wb, ws, 'Resumen Consumo Bio');
    XLSX.writeFile(wb, 'resumen_consumo_bio_' + moment().format('YYYY-MM-DD') + '.xlsx');
}

// Funcion para exportar a PDF manualmente
function exportarPDF() {
    if (datos_procesados.length === 0) {
        alert('No hay datos para exportar');
        return;
    }

    var periodo = getPeriodo();
    
    // Calcular totales
    var total_cantidad = 0;
    var total_total = 0;
    
    var body = [];
    
    // Encabezados
    body.push([
        {text: 'LINEA', style: 'tableHeader'},
        {text: 'SUB-LINEA', style: 'tableHeader'},
        {text: 'CANTIDAD', style: 'tableHeader'},
        {text: 'COSTO', style: 'tableHeader'},
        {text: 'TOTAL', style: 'tableHeader'}
    ]);
    
    // Datos
    datos_procesados.forEach(function(item) {
        body.push([
            {text: 'INSUMOS', style: 'tableCell'},
            {text: item.nombre, style: 'tableCell'},
            {text: item.cantidad.toFixed(2), style: 'tableCellRight'},
            {text: item.costo.toFixed(10), style: 'tableCellRight'},
            {text: item.total.toFixed(2), style: 'tableCellRight'}
        ]);
        total_cantidad += item.cantidad;
        total_total += item.total;
    });
    
    // Fila de totales
    body.push([
        {text: 'Cantidad Total', style: 'tableFooter'},
        {text: 'Cantidad Total', style: 'tableFooter'},
        {text: total_cantidad.toFixed(2), style: 'tableFooterRight'},
        {text: '', style: 'tableFooter'},
        {text: total_total.toFixed(2), style: 'tableFooterRight'}
    ]);
    
    var docDefinition = {
        pageSize: 'LETTER',
        pageOrientation: 'portrait',
        pageMargins: [40, 60, 40, 60],
        content: [
            {
                text: 'RESUMEN CONSUMO BIO',
                style: 'header'
            },
            {
                text: 'Periodo: ' + periodo,
                style: 'subheader'
            },
            {
                text: ' ',
                margin: [0, 10, 0, 10]
            },
            {
                table: {
                    headerRows: 1,
                    widths: [80, 150, 70, 90, 70],
                    body: body
                },
                layout: {
                    hLineWidth: function(i, node) {
                        return (i === 0 || i === 1 || i === node.table.body.length) ? 1 : 0.5;
                    },
                    vLineWidth: function(i) {
                        return 0;
                    },
                    hLineColor: function(i, node) {
                        return (i === 0 || i === 1) ? '#337AB7' : '#dddddd';
                    },
                    fillColor: function(rowIndex) {
                        if (rowIndex === 0) return '#337AB7';
                        return null;
                    }
                }
            }
        ],
        styles: {
            header: {
                fontSize: 18,
                bold: true,
                alignment: 'center',
                color: '#337AB7',
                margin: [0, 0, 0, 10]
            },
            subheader: {
                fontSize: 11,
                alignment: 'center',
                color: '#666666',
                margin: [0, 0, 0, 20]
            },
            tableHeader: {
                bold: true,
                fontSize: 10,
                color: 'white',
                alignment: 'center'
            },
            tableCell: {
                fontSize: 9,
                color: '#333333',
                margin: [0, 5, 0, 5]
            },
            tableCellRight: {
                fontSize: 9,
                color: '#333333',
                alignment: 'right',
                margin: [0, 5, 0, 5]
            },
            tableFooter: {
                bold: true,
                fontSize: 9,
                color: '#337AB7',
                fillColor: '#ecf0f1',
                margin: [0, 5, 0, 5]
            },
            tableFooterRight: {
                bold: true,
                fontSize: 9,
                color: '#337AB7',
                alignment: 'right',
                margin: [0, 5, 0, 5]
            }
        },
        footer: function(currentPage, pageCount) {
            return {
                columns: [
                    {
                        text: 'Fecha de creacion: ' + moment().format('DD/MM/YYYY HH:mm:ss'),
                        alignment: 'left',
                        fontSize: 8,
                        margin: [40, 0]
                    },
                    {
                        text: 'Pagina ' + currentPage.toString() + ' de ' + pageCount,
                        alignment: 'right',
                        fontSize: 8,
                        margin: [0, 0, 40, 0]
                    }
                ]
            };
        }
    };
    
    pdfMake.createPdf(docDefinition).open();
}

// Funcion para imprimir
function imprimirReporte() {
    if (datos_procesados.length === 0) {
        alert('No hay datos para imprimir');
        return;
    }

    var periodo = getPeriodo();
    
    // Calcular totales
    var total_cantidad = 0;
    var total_total = 0;
    
    var filas = '';
    datos_procesados.forEach(function(item) {
        filas += '<tr>';
        filas += '<td style="padding: 8px; border-bottom: 1px solid #ddd;">INSUMOS</td>';
        filas += '<td style="padding: 8px; border-bottom: 1px solid #ddd;">' + item.nombre + '</td>';
        filas += '<td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: right;">' + item.cantidad.toFixed(2) + '</td>';
        filas += '<td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: right;">' + item.costo.toFixed(10) + '</td>';
        filas += '<td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: right;">' + item.total.toFixed(2) + '</td>';
        filas += '</tr>';
        total_cantidad += item.cantidad;
        total_total += item.total;
    });
    
    var printContent = `
        <!DOCTYPE html>
        <html>
        <head>
            <title>Resumen Consumo Bio</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { text-align: center; margin-bottom: 20px; }
                .header h1 { color: #337AB7; margin: 0; font-size: 24px; }
                .header p { color: #666; margin: 5px 0; }
                table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                th { background-color: #337AB7; color: white; padding: 10px; text-align: center; }
                td { padding: 8px; }
                .total-row { background-color: #ecf0f1; font-weight: bold; color: #337AB7; }
                .footer { margin-top: 20px; font-size: 10px; color: #666; }
                @media print {
                    body { margin: 0; }
                    .no-print { display: none; }
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>RESUMEN CONSUMO BIO</h1>
                <p>Periodo: ${periodo}</p>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>LINEA</th>
                        <th>SUB-LINEA</th>
                        <th>CANTIDAD</th>
                        <th>COSTO</th>
                        <th>TOTAL</th>
                    </tr>
                </thead>
                <tbody>
                    ${filas}
                    <tr class="total-row">
                        <td style="padding: 8px;">Cantidad Total</td>
                        <td style="padding: 8px;">Cantidad Total</td>
                        <td style="padding: 8px; text-align: right;">${total_cantidad.toFixed(2)}</td>
                        <td style="padding: 8px;"></td>
                        <td style="padding: 8px; text-align: right;">${total_total.toFixed(2)}</td>
                    </tr>
                </tbody>
            </table>
            <div class="footer">
                <p>Fecha de creacion: ${moment().format('DD/MM/YYYY HH:mm:ss')}</p>
            </div>
        </body>
        </html>
    `;
    
    var printWindow = window.open('', '_blank');
    printWindow.document.write(printContent);
    printWindow.document.close();
    printWindow.focus();
    setTimeout(function() {
        printWindow.print();
    }, 500);
}

function generate_report_piscinas() {
    var parameters = {
        'action': 'search_insumos_conglomerado_bio',
        'start_date': date_now,
        'end_date': date_now,
    };

    if (date_range !== null) {
        parameters['start_date'] = date_range.startDate.format('YYYY-MM-DD');
        parameters['end_date'] = date_range.endDate.format('YYYY-MM-DD');
    }

    tb_piscinas_por_insumos = $('#insumos_conglomerado_bio').DataTable({
        destroy: true,
        lengthChange: false,
        fixedHeader: true,
        language: {
            "lengthMenu": "Mostrar _MENU_ registros",
            "zeroRecords": "No se encontraron resultados",
            "info": "Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros",
            "infoEmpty": "Mostrando registros del 0 al 0 de un total de 0 registros",
            "infoFiltered": "(filtrado de un total de _MAX_ registros)",
            "sSearch": "Buscar:",
            "oPaginate": {
                "sFirst": "Primero",
                "sLast": "Ultimo",
                "sNext": "Siguiente",
                "sPrevious": "Anterior"
            },
            "sProcessing": "Procesando...",
        },
        autoWidth: false,
        deferRender: true,
        ajax: {
            url: window.location.pathname,
            type: 'POST',
            data: parameters,
            dataSrc: ""
        },
        scrollY: "550px",
        scrollX: true,
        paging: false,
        info: false,
        dom: 'Bfrtip',
        buttons: [
            {
                text: '<i class="fas fa-file-excel"></i> ',
                titleAttr: 'Exportar a Excel',
                className: 'btn btn-success',
                action: function (e, dt, node, config) {
                    exportarExcel();
                }
            },
            {
                text: '<i class="fa fa-print"></i> ',
                titleAttr: 'Imprimir',
                className: 'btn btn-info',
                action: function (e, dt, node, config) {
                    imprimirReporte();
                }
            },
            {
                text: '<i class="fas fa-file-pdf"></i> ',
                titleAttr: 'Exportar a PDF',
                className: 'btn btn-danger',
                action: function (e, dt, node, config) {
                    exportarPDF();
                }
            }
        ],
        columns: [
            {"data": "producto_empresa.nombre_prod.nombre","width": "50%"},
            {"data": "cantidad_egreso","width": "10%"},
            {"data": "producto_empresa.nombre_prod.costo_aplicacion","width": "20%"},
            {"data": "producto_empresa.nombre_prod.costo_aplicacion","width": "20%"},
        ],
        columnDefs: [
            {
                targets: [0],
                class: 'text-center',
                orderable: true,
                render: function (data, type, row) {
                    return data !== null ? data : '';
                }
            },
            {
                targets: [1,2],
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    return data;
                }
            },
            {
                targets: [-1],
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    var multipli = parseFloat(row.cantidad_egreso) * parseFloat(row.producto_empresa.nombre_prod.costo);
                    return multipli.toFixed(3) > 0 ? multipli.toFixed(3): 0;
                }
            }
        ],
        initComplete: function (settings, json) {

            var movimientos_encontrados = new Array();
            var nuevo_ArrayObject = new Array();

            json.map(function (valor, indice) {
                if (movimientos_encontrados.indexOf(valor.producto_empresa.nombre_prod.nombre) === -1) {
                    movimientos_encontrados.push(valor.producto_empresa.nombre_prod.nombre);
                    nuevo_ArrayObject.push(valor);
                } else {
                    var recuperado = movimientos_encontrados.indexOf(valor.producto_empresa.nombre_prod.nombre);
                    var objetoRecuperado = nuevo_ArrayObject[recuperado];
                    objetoRecuperado.cantidad_egreso = parseFloat(objetoRecuperado.cantidad_egreso) + parseFloat(valor.cantidad_egreso);
                }
            });

            // Guardar datos procesados en variable global para exportacion
            datos_procesados = [];
            var total_consumos=0, cantidad=0.00, costo=0.000000000, acum1=0, acum2=0;
            var table = '<table class="table">';
            nuevo_ArrayObject.map(function (valor, indice) {
                cantidad = parseFloat(valor.cantidad_egreso);
                costo = parseFloat(valor.producto_empresa.nombre_prod.costo_aplicacion);
                total_consumos = parseFloat(cantidad * costo);
                
                // Guardar para exportacion
                datos_procesados.push({
                    nombre: valor.producto_empresa.nombre_prod.nombre,
                    cantidad: cantidad,
                    costo: costo,
                    total: total_consumos
                });
                
                table+='<tr>'
                table+='<td style="width: 50%; text-align: left"">'+valor.producto_empresa.nombre_prod.nombre+'</td>'
                table+='<td scope="col" style="width: 10%; text-align: center">'+ cantidad.toFixed(2) +'</td>'
                table+='<td scope="col" style="width: 20%; text-align: center">'+ costo.toFixed(10) +'</td>'
                table+='<td scope="col" style="width: 20%; text-align: center">'+ total_consumos.toFixed(2) +'</td>'
                table+='</tr>';
                acum1 += cantidad;  acum2 += total_consumos;

            });
                table+='<tr>'
                table+='<th scope="col" style="width: 50%; text-align: center"> Total</th>'
                table+='<th scope="col" style="width: 10%; text-align: center">'+acum1.toFixed(2)+'</th>'
                table+='<th scope="col" style="width: 20%"></th>'
                table+='<th scope="col" style="width: 20%; text-align: center">'+acum2.toFixed(2)+'</th>'
                table+='</tr>';

            table += '</table>';

            document.getElementById("insumos_conglomerado_bio").innerHTML = table;
            console.log(table)
        }
    });
}

$(function () {

    $('input[name="date_range2"]').daterangepicker({
        locale: {
            format: 'YYYY-MM-DD',
            applyLabel: '<i class="fas fa-chart-pie"></i> Aplicar',
            cancelLabel: '<i class="fas fa-times"></i> Cancelar',
        }
    }).on('apply.daterangepicker', function (ev, picker) {
        date_range = picker;
        console.log('Entro a Resumen Piscinas por los Insumos Conglomerado');
        generate_report_piscinas();
    }).on('cancel.daterangepicker', function (ev, picker) {
        $(this).data('daterangepicker').setStartDate(date_now);
        $(this).data('daterangepicker').setEndDate(date_now);
        date_range = picker;
        generate_report_piscinas();
    });
    console.log('Entro a Resumen Piscinas por los Insumos Conglomerado');
    generate_report_piscinas();

});

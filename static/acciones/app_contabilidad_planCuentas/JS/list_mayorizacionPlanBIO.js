var date_range = null;
var multiplicadora = 0, total_stock = 0;
var tb_mayor_list, saldo_contador = 0;
var plan_det = [];
var resultado;
var total, group_assoc, group_total, total_seg;
var tot_deb = 0, tot_hab = 0, tot_sal = 0, deb = 0, hab = 0, acum = 0;
var date_now = new moment().format('YYYY-MM-DD');
var hour_now = new moment().format('HH-MM-SS');
var json_glob = 0;
var all_data_cache = []; // Cache para almacenar todos los datos para calculos

function mayor_list() {
    var groupColumn = 0;
    tb_mayor_list = $('#tb_mayorizacion_plan').DataTable({
        language: {
            "oPaginate": {
                "sFirst": "Primero",
                "sLast": "Ultimo",
                "sNext": "Siguiente",
                "sPrevious": "Anterior"
            },
            "zeroRecords": "Ningun dato disponible en esta tabla",
            "sInfo": "Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros",
            "infoEmpty": "Tabla vacia por favor inserte datos",
            "lengthMenu": "Listando _MENU_ registros",
            "sSearch": "Buscar:",
            "infoFiltered": "(filtrado de _MAX_ registros totales)",
            "processing": "Procesando..."
        },
        responsive: true,
        // ========== PAGINACION SERVER-SIDE ==========
        serverSide: true,
        processing: true,
        bPaginate: true,
        pageLength: 50, // Registros por pagina
        lengthMenu: [[25, 50, 100, 200], [25, 50, 100, 200]],
        // ============================================
        autoWidth: false,
        destroy: true,
        deferRender: true,
        scrollY: "700px",
        scrollX: true,
        bInfo: true,
        dom: 'Blfrtip',
        ajax: {
            url: window.location.pathname,
            type: 'POST',
            data: function(d) {
                d.action = 'searchdata';
                d.empresa = 'BIO';
                return d;
            },
            // dataSrc ya no es necesario porque el servidor devuelve el formato correcto
        },
        buttons: [
            {
                extend: 'excelHtml5',
                text: '<i class="fas fa-file-csv"></i> ',
                titleAttr: 'Exportar a Excel',
                className: 'btn btn-success',
                action: function (e, dt, button, config) {
                    // Exportar todos los datos, no solo la pagina actual
                    exportAllData('excel');
                }
            },
            {
                extend: 'print',
                text: '<i class="fa fa-print"></i> ',
                titleAttr: 'Imprimir',
                className: 'btn btn-info',
                action: function (e, dt, button, config) {
                    exportAllData('print');
                }
            },
            {
                extend: 'pdfHtml5',
                text: '<i class="fas fa-file-pdf"></i> ',
                titleAttr: 'Exportar a PDF',
                className: 'btn btn-danger',
                action: function (e, dt, button, config) {
                    exportAllData('pdf');
                }
            }
        ],
        columns: [
            {"data": "codigo_cuenta_plan", 'width':'15%'},
            {"data": "nombre_cuenta_plan", 'width':'15%'},
            {"data": "detalle", 'width':'40%'},
            {"data": "fecha_asiento_transaccion", 'width':'8%'},
            {"data": "nombre_asiento_transaccion", 'width':'5%'},
            {"data": "codigo_asiento_transaccion", 'width':'5%'},
            {"data": "debe", 'width':'5%'},
            {"data": "haber", 'width':'5%'},
            {"data": "encabezadocuentaplan", 'width':'5%'},
        ],
        columnDefs: [
            {
                targets: [0],
                class: 'text-center',
                orderable: false,
                visible: false,
                render: function (data, type, row) {
                    return data;
                }
            },
            {
                targets: [1],
                class: 'text-left',
                visible: false,
                orderable: false,
                render: function (data, type, row) {
                    return data;
                }
            },
            {
                targets: [2],
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    return data;
                }
            },
            {
                targets: [3],
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    return '<b>' + data + '</b>';
                }
            },
            {
                targets: [4],
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    if (row.nombre_asiento_transaccion === "1") {
                        return 'DIARIO CONTABLE';
                    } else if (row.nombre_asiento_transaccion === "2") {
                        return 'COMPROBANTE DE PAGO';
                    } else if (row.nombre_asiento_transaccion === "3") {
                        return 'INGRESO A CAJA';
                    } else {
                        return 'EGRESO DE CAJA';
                    }
                }
            },
            {
                targets: [5],
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    return data;
                }
            },
            {
                targets: [-3, -2],
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
                render: function (data, type, row, index) {
                    total = '';
                    deb = row.debe;
                    hab = row.haber;
                    if (row.debe > 0)
                        total += row.debe;
                    else
                        total -= row.haber;
                    acum = total;
                    return parseFloat(acum).toFixed(2);
                }
            },
        ],
        rowCallback: function (row, data, index) {
            var tr = $(row).closest('tr');
            var pageInfo = tb_mayor_list.page.info();
            var globalIndex = pageInfo.start + index;

            // Calcular saldo basado en los datos de la pagina actual
            var pageData = tb_mayor_list.rows({page: 'current'}).data().toArray();

            for (let i = 0; i <= index; i++) {
                if (i === index) {
                    if ((i > 0 && pageData[i]['codigo_cuenta_plan'] === pageData[i - 1]["codigo_cuenta_plan"])) {
                        pageData[i]["saldo"] = (parseFloat(pageData[i]['debe']) - parseFloat(pageData[i]['haber'])) + parseFloat(pageData[i - 1]['saldo'] || 0);
                    } else {
                        pageData[i]["saldo"] = parseFloat(pageData[i]['debe']) - parseFloat(pageData[i]['haber']);
                    }
                    $('td:eq(-1)', tb_mayor_list.row(tr).node()).html('<b>' + parseFloat(pageData[i]["saldo"]).toFixed(2) + '</b>');
                }
            }
        },
        drawCallback: function (settings, json) {
            var api = this.api();
            var rows = api.rows({page: 'current'}).nodes();
            var last = null;
            var total = 0, total2 = 0, total3 = 0;
            var filas = api.column(0, {page: 'current'}).data();

            filas.each(function (group, i, pos, dict) {
                if (last !== group) {
                    if (last !== null) {
                        $(rows).eq(i - 1).after(
                            `<tr class="total">
                                <td colspan="3" style="width: 55%;"></td>
                                <td class="text-center" style="width: 10%;font-weight:700;background-color:rgb(255, 255, 255)">Saldo de la Cuenta:</td>
                                <td class="text-center" style="width: 10%;font-weight:700;background-color:rgb(255, 255, 255)">${total.toFixed(2)}</td>   
                                <td class="text-center" style="width: 10%;font-weight:700;background-color:rgb(255, 255, 255)">${total2.toFixed(2)}</td>  
                                <td class="text-center" style="width: 15%;font-weight:700;background-color:rgb(255, 255, 255)">${total3.toFixed(2)}</td>   
                            </tr>`
                        );
                        total = 0;
                        total2 = 0;
                        total3 = 0;
                    }
                    $.each(settings.aoData, function (pos, dict) {
                        if(dict._aFilterData && dict._aFilterData[0] === group){
                            resultado = dict._aFilterData[1]
                        }
                    })

                    $(rows).eq(i).before(
                        '<tr class="group text-left" style="background-color:rgb(255, 255, 255);font-weight:700;">' +
                        '<td colspan="6" style="width: 100%">' + "Cuenta de Mayor: &nbsp;" + group + ' &nbsp; / &nbsp; ' + (resultado || '') + '</td>' +
                        '</tr>'
                    );
                    last = group;
                }
                total += +$(rows).eq(i).children()[4].textContent;
                total2 += +$(rows).eq(i).children()[5].textContent;
                total3 += +$(rows).eq(i).children()[4].textContent - +$(rows).eq(i).children()[5].textContent;
                if (i === filas.length - 1) {
                    $(rows).eq(i).after(
                        `<tr class="total">
                            <td colspan="3" style="width: 55%;"></td>
                            <td class="text-center" style="width: 10%;font-weight:700;background-color:rgb(255, 255, 255)">Saldo de la Cuenta:</td>
                            <td class="text-center" style="width: 10%;font-weight:700;background-color:rgb(255, 255, 255)">${total.toFixed(2)}</td>   
                            <td class="text-center" style="width: 10%;font-weight:700;background-color:rgb(255, 255, 255)">${total2.toFixed(2)}</td>  
                            <td class="text-center" style="width: 15%;font-weight:700;background-color:rgb(255, 255, 255)">${total3.toFixed(2)}</td>   
                        </tr>`
                    );
                }
            });
        },
        initComplete: function (settings, json) {
            console.log('Tabla cargada correctamente');
        }
    });
}

// Funcion para exportar todos los datos (no solo la pagina actual)
function exportAllData(type) {
    // Mostrar loading
    Swal.fire({
        title: 'Cargando datos...',
        text: 'Por favor espere mientras se cargan todos los registros',
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        }
    });

    $.ajax({
        url: window.location.pathname,
        type: 'POST',
        data: {
            'action': 'searchdata_all',
            'empresa': 'BIO'
        },
        success: function(data) {
            Swal.close();

            if (type === 'excel') {
                exportToExcel(data);
            } else if (type === 'pdf') {
                exportToPDF(data);
            } else if (type === 'print') {
                printData(data);
            }
        },
        error: function(xhr, status, error) {
            Swal.fire('Error', 'No se pudieron cargar los datos', 'error');
        }
    });
}

// Funcion para exportar a Excel
function exportToExcel(data) {
    var wb = XLSX.utils.book_new();
    var ws_data = [['Codigo', 'Nombre Cuenta', 'Descripcion', 'Fecha', 'Transaccion', 'Asiento', 'Debe', 'Haber', 'Saldo']];

    data.forEach(function(row) {
        ws_data.push([
            row.codigo_cuenta_plan,
            row.nombre_cuenta_plan,
            row.detalle,
            row.fecha_asiento_transaccion,
            row.nombre_asiento_transaccion,
            row.codigo_asiento_transaccion,
            row.debe,
            row.haber,
            row.encabezadocuentaplan
        ]);
    });

    var ws = XLSX.utils.aoa_to_sheet(ws_data);
    XLSX.utils.book_append_sheet(wb, ws, "Libro Mayor");
    XLSX.writeFile(wb, "libro_mayor_BIO_" + date_now + ".xlsx");
}

// Funcion para exportar a PDF (simplificada)
function exportToPDF(data) {
    // Crear ventana de impresion con formato PDF
    var printWindow = window.open('', '_blank');
    var html = '<html><head><title>Libro Mayor BIO</title>';
    html += '<style>table{width:100%;border-collapse:collapse;}th,td{border:1px solid #000;padding:5px;font-size:10px;}th{background:#2d4154;color:#fff;}</style>';
    html += '</head><body>';
    html += '<h2 style="text-align:center;">ANALITICO AUXILIAR DE CUENTAS - DETALLE</h2>';
    html += '<table><thead><tr><th>Codigo</th><th>Nombre</th><th>Descripcion</th><th>Fecha</th><th>Debe</th><th>Haber</th><th>Saldo</th></tr></thead><tbody>';

    data.forEach(function(row) {
        html += '<tr>';
        html += '<td>' + row.codigo_cuenta_plan + '</td>';
        html += '<td>' + row.nombre_cuenta_plan + '</td>';
        html += '<td>' + row.detalle + '</td>';
        html += '<td>' + row.fecha_asiento_transaccion + '</td>';
        html += '<td>' + row.debe + '</td>';
        html += '<td>' + row.haber + '</td>';
        html += '<td>' + (parseFloat(row.debe) - parseFloat(row.haber)).toFixed(2) + '</td>';
        html += '</tr>';
    });

    html += '</tbody></table>';
    html += '<p>Fecha de creacion: ' + date_now + '</p>';
    html += '</body></html>';

    printWindow.document.write(html);
    printWindow.document.close();
    printWindow.print();
}

// Funcion para imprimir
function printData(data) {
    exportToPDF(data);
}

function isEqual(a, b) {
    if (a instanceof Array && b instanceof Array) {
        if (a.length !== b.length) {
            return false;
        }
        for (var i = 0; i < a.length; i++) {
            if (!isEqual(a[i], b[i])) {
                return false;
            }
        }
        return true;
    }
    return a === b;
}

$(function () {
    mayor_list();
});
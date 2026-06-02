var date_range = null;
var tb_mayor_list_range;

var date_now = moment().format('YYYY-MM-DD');
var hour_now = moment().format('HH-mm-ss');

var plan_det = [];
var desde_rang = '';
var hasta_rang = '';
var contador_ult = '';

/* ==========================================================
   FORMATO NUMERICO
========================================================== */

function formatNumber(num) {

    num = parseFloat(num || 0);

    return num.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

/* ==========================================================
   GENERAR REPORTE
========================================================== */

function generate_report() {

    var parameters = {

        'action': 'search_report',
        'empresa': 'BIO',
        'desde_rang': desde_rang,
        'hasta_rang': hasta_rang,
        'start_date': date_now,
        'end_date': date_now
    };

    if (date_range !== null) {

        parameters['start_date'] = date_range.startDate.format('YYYY-MM-DD');
        parameters['end_date'] = date_range.endDate.format('YYYY-MM-DD');
    }

    tb_mayor_list_range = $('#date_range').DataTable({

        destroy: true,
        responsive: true,
        autoWidth: false,
        deferRender: true,

        processing: true,
        serverSide: false,

        paging: false,
        ordering: false,
        searching: true,
        info: true,

        scrollY: '700px',
        scrollCollapse: true,
        scrollX: true,

        dom: 'Bfrtip',

        language: {

            "oPaginate": {
                "sFirst": "Primero",
                "sLast": "Último",
                "sNext": "Siguiente",
                "sPrevious": "Anterior"
            },

            "zeroRecords": "No existen registros",
            "info": "Mostrando _START_ a _END_ de _TOTAL_ registros",
            "infoEmpty": "Sin registros",
            "lengthMenu": "Mostrar _MENU_ registros",
            "search": "Buscar:",
            "infoFiltered": "(filtrado de _MAX_ registros)",
            "processing": "Procesando..."
        },

        ajax: {

            url: window.location.pathname,
            type: 'POST',
            data: parameters,

            dataSrc: function (json) {

                if (json.error) {

                    console.error(json.error);

                    return [];
                }

                return json.data;
            }
        },

        /* ======================================================
           BOTONES
        ====================================================== */

        buttons: [

            {
                extend: 'excelHtml5',
                text: 'Excel <i class="fas fa-file-excel"></i>',
                className: 'btn btn-success btn-sm',
                footer: true
            },

            {
                extend: 'pdfHtml5',
                text: 'PDF <i class="fas fa-file-pdf"></i>',
                className: 'btn btn-danger btn-sm',

                download: 'open',
                orientation: 'landscape',
                pageSize: 'LEGAL',
                footer: true,

                customize: function (doc) {

                    doc.styles.tableHeader = {

                        bold: true,
                        fontSize: 10,
                        color: 'white',
                        fillColor: '#343a40',
                        alignment: 'center'
                    };

                    doc.styles.defaultStyle = {
                        fontSize: 8
                    };

                    doc.footer = function (page, pages) {

                        return {

                            columns: [

                                {
                                    alignment: 'left',
                                    text: 'Fecha: ' + date_now + ' Hora: ' + hour_now
                                },

                                {
                                    alignment: 'right',
                                    text: [
                                        'Página ',
                                        page.toString(),
                                        ' de ',
                                        pages.toString()
                                    ]
                                }
                            ],

                            margin: 20
                        };
                    };

                    doc.header = function () {

                        return {

                            columns: [

                                {
                                    alignment: 'center',
                                    text: 'LIBRO MAYOR ANALÍTICO',
                                    bold: true,
                                    fontSize: 16,
                                    margin: [0, 10]
                                }
                            ]
                        };
                    };
                }
            }
        ],

        /* ======================================================
           COLUMNAS
        ====================================================== */

        columns: [

            {"data": "codigo"},
            {"data": "nombre"},
            {"data": "descripcion"},
            {"data": "fecha"},
            {"data": "transaccion"},
            {"data": "asiento"},
            {"data": "debe"},
            {"data": "haber"},
            {"data": "saldo"}
        ],

        /* ======================================================
           CONFIG COLUMNAS
        ====================================================== */

        columnDefs: [

            /* CODIGO */

            {
                targets: [0],
                visible: false
            },

            /* NOMBRE */

            {
                targets: [1],
                visible: false
            },

            /* DESCRIPCION */

            {
                targets: [2],
                className: 'text-left',

                render: function (data) {

                    return data || '';
                }
            },

            /* FECHA */

            {
                targets: [3],
                className: 'text-center',

                render: function (data) {

                    return '<b>' + data + '</b>';
                }
            },

            /* TRANSACCION */

            {
                targets: [4],
                className: 'text-center',

                render: function (data) {

                    if (data == "1") {
                        return 'DIARIO CONTABLE';
                    }

                    if (data == "2") {
                        return 'COMPROBANTE DE PAGO';
                    }

                    if (data == "3") {
                        return 'INGRESO A CAJA';
                    }

                    return 'EGRESO DE CAJA';
                }
            },

            /* ASIENTO */

            {
                targets: [5],
                className: 'text-center'
            },

            /* DEBE */

            {
                targets: [6],
                className: 'text-right',

                render: function (data) {

                    return '<b>' + formatNumber(data) + '</b>';
                }
            },

            /* HABER */

            {
                targets: [7],
                className: 'text-right',

                render: function (data) {

                    return '<b>' + formatNumber(data) + '</b>';
                }
            },

            /* SALDO */

            {
                targets: [8],
                className: 'text-right',

                render: function (data) {

                    return '<b style="color:#0d6efd;">' +
                        formatNumber(data) +
                        '</b>';
                }
            }
        ],

        /* ======================================================
           AGRUPAR POR CUENTA
        ====================================================== */

        drawCallback: function () {

            var api = this.api();

            var rows = api.rows({page: 'current'}).nodes();

            var data = api.rows({page: 'current'}).data();

            var last = null;

            var totalDebe = 0;
            var totalHaber = 0;
            var totalSaldo = 0;

            data.each(function (row, i) {

                /* ==============================================
                   CAMBIO DE CUENTA
                ============================================== */

                if (last !== row.codigo) {

                    /* ==========================================
                       INSERTAR TOTALES ANTERIORES
                    ========================================== */

                    if (last !== null) {

                        $(rows).eq(i - 1).after(`

                            <tr style="
                                background:#f1f1f1;
                                font-weight:bold;
                            ">

                                <td colspan="4"
                                    class="text-right">

                                    TOTALES DE LA CUENTA

                                </td>

                                <td class="text-right">
                                    ${formatNumber(totalDebe)}
                                </td>

                                <td class="text-right">
                                    ${formatNumber(totalHaber)}
                                </td>

                                <td class="text-right text-primary">
                                    ${formatNumber(totalSaldo)}
                                </td>

                            </tr>
                        `);

                        totalDebe = 0;
                        totalHaber = 0;
                        totalSaldo = 0;
                    }

                    /* ==========================================
                       CABECERA CUENTA
                    ========================================== */

                    $(rows).eq(i).before(`

                        <tr style="
                            background:#343a40;
                            color:white;
                            font-weight:bold;
                        ">

                            <td colspan="7">

                                CUENTA:
                                ${row.codigo}
                                /
                                ${row.nombre}

                            </td>

                        </tr>
                    `);

                    last = row.codigo;
                }

                /* ==============================================
                   ACUMULADOS
                ============================================== */

                totalDebe += parseFloat(row.debe || 0);
                totalHaber += parseFloat(row.haber || 0);

                totalSaldo = totalDebe - totalHaber;

                /* ==============================================
                   ULTIMA FILA
                ============================================== */

                if (i === data.length - 1) {

                    $(rows).eq(i).after(`

                        <tr style="
                            background:#f1f1f1;
                            font-weight:bold;
                        ">

                            <td colspan="4"
                                class="text-right">

                                TOTALES DE LA CUENTA

                            </td>

                            <td class="text-right">
                                ${formatNumber(totalDebe)}
                            </td>

                            <td class="text-right">
                                ${formatNumber(totalHaber)}
                            </td>

                            <td class="text-right text-primary">
                                ${formatNumber(totalSaldo)}
                            </td>

                        </tr>
                    `);
                }
            });
        }
    });
}

/* ==========================================================
   LOAD
========================================================== */

$(function () {

    /* ======================================================
       SELECT2
    ====================================================== */

    $('.select2').select2({

        theme: 'bootstrap4',
        language: 'es'
    });

    /* ======================================================
       RANGO FECHAS
    ====================================================== */

    $('input[name="date_range"]').daterangepicker({

        locale: {

            format: 'YYYY-MM-DD',
            applyLabel: 'Aplicar',
            cancelLabel: 'Cancelar'
        }

    }).on('apply.daterangepicker', function (ev, picker) {

        date_range = picker;

        generate_report();

    }).on('cancel.daterangepicker', function () {

        date_range = null;

        generate_report();
    });

    /* ======================================================
       CARGAR PLAN CUENTAS
    ====================================================== */

    $.ajax({

        url: window.location.pathname,
        type: 'POST',

        data: {
            'action': 'searchdataplan'
        },

        dataType: 'json'

    }).done(function (data) {

        plan_det = [];

        $.each(data, function (key, value) {

            plan_det.push({

                id: value.codigo,
                text: value.text
            });

            contador_ult = value.codigo;
        });

        /* ==============================================
           DESDE
        ============================================== */

        $('select[name="rango_desde"]').select2({

            theme: 'bootstrap4',
            language: 'es',
            data: plan_det,
            placeholder: 'Seleccione cuenta'
        });

        $('select[name="rango_desde"]').on(
            'select2:select',
            function (e) {

                desde_rang = e.params.data.id;

                generate_report();
            }
        );

        /* ==============================================
           HASTA
        ============================================== */

        $('select[name="rango_hasta"]').select2({

            theme: 'bootstrap4',
            language: 'es',
            data: plan_det,
            placeholder: 'Seleccione cuenta'
        });

        $('select[name="rango_hasta"]').on(
            'select2:select',
            function (e) {

                hasta_rang = e.params.data.id;

                generate_report();
            }
        );
    });

    /* ======================================================
       LIMPIAR FILTROS
    ====================================================== */

    $('.btnRemoveAll').on('click', function () {

        $('select[name="rango_desde"]')
            .val(null)
            .trigger('change');

        $('select[name="rango_hasta"]')
            .val(null)
            .trigger('change');

        desde_rang = '';
        hasta_rang = '';

        date_range = null;

        generate_report();
    });

    /* ======================================================
       INICIAR
    ====================================================== */

    generate_report();
});
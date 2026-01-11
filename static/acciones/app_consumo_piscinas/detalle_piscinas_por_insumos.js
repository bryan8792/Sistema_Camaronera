var tb_piscinas_por_insumos;
var date_range = null;
var date_now = moment().format('YYYY-MM-DD');

function generate_report_piscinas() {

    var parameters = {
        action: 'search_piscinas_insumos',
        start_date: date_now,
        end_date: date_now
    };

    if (date_range !== null) {
        parameters.start_date = date_range.startDate.format('YYYY-MM-DD');
        parameters.end_date = date_range.endDate.format('YYYY-MM-DD');
    }

    if ($.fn.DataTable.isDataTable('#tb_piscinas_por_insumos')) {
        tb_piscinas_por_insumos.destroy();
        $('#dt-buttons-piscinas').empty();
    }

    tb_piscinas_por_insumos = $('#tb_piscinas_por_insumos').DataTable({

        paging: false,
        info: false,
        ordering: false,
        searching: false,
        autoWidth: false,

        // Solo tabla sin botones en el DOM
        dom: 'Brt',

        buttons: [
            {
                extend: 'excelHtml5',
                text: 'Excel',
                className: 'btn btn-success btn-sm',
                title: 'Resumen de Piscinas por Insumos',
                exportOptions: {
                    columns: ':visible'
                }
            },
            {
                extend: 'pdfHtml5',
                text: 'PDF',
                className: 'btn btn-danger btn-sm',
                title: 'Resumen de Piscinas por Insumos',
                orientation: 'landscape',
                pageSize: 'A4',
                exportOptions: {
                    columns: ':visible'
                }
            },
            {
                extend: 'print',
                text: 'Imprimir',
                className: 'btn btn-info btn-sm',
                title: 'Resumen de Piscinas por Insumos',
                exportOptions: {
                    columns: ':visible'
                }
            }
        ],

        ajax: {
            url: window.location.pathname,
            type: 'POST',
            data: parameters,
            dataSrc: function (json) {

                let consolidado = {};
                let resultado = [];

                json.forEach(row => {

                    let producto = row.producto_empresa.nombre_prod.nombre;
                    let piscina = row.piscinas;
                    let key = producto + '|' + piscina;

                    if (!consolidado[key]) {
                        consolidado[key] = {
                            producto: producto,
                            piscina: piscina,
                            cantidad: 0,
                            costo: parseFloat(row.producto_empresa.nombre_prod.costo_aplicacion || 0),
                            total: 0,
                            is_total: false
                        };
                    }

                    consolidado[key].cantidad += parseFloat(row.cantidad_egreso);
                    consolidado[key].total = consolidado[key].cantidad * consolidado[key].costo;
                });

                Object.values(consolidado).forEach(item => resultado.push(item));

                let totalCantidad = 0;
                let totalFinal = 0;

                resultado.forEach(r => {
                    totalCantidad += r.cantidad;
                    totalFinal += r.total;
                });

                resultado.push({
                    producto: 'Total',
                    piscina: '',
                    cantidad: totalCantidad,
                    costo: '',
                    total: totalFinal,
                    is_total: true
                });

                return resultado;
            }
        },

        columns: [
            { data: 'producto' },
            { data: 'piscina', className: 'text-center' },
            {
                data: 'cantidad',
                className: 'text-center',
                render: d => d !== '' ? parseFloat(d).toFixed(2) : ''
            },
            {
                data: 'costo',
                className: 'text-center',
                render: d => d !== '' ? parseFloat(d).toFixed(10) : ''
            },
            {
                data: 'total',
                className: 'text-center',
                render: d => d !== '' ? parseFloat(d).toFixed(2) : ''
            }
        ],

        rowCallback: function (row, data) {
            if (data.is_total) {
                $(row).css({
                    'font-weight': 'bold',
                    'background-color': '#f2f2f2'
                });
            }
        },

        initComplete: function() {
            // Mover botones al contenedor
            tb_piscinas_por_insumos.buttons().container().appendTo('#dt-buttons-piscinas');
        }
    });
}

/* DATE RANGE */
$(function () {

    $('input[name="date_range2"]').daterangepicker({
        locale: {
            format: 'YYYY-MM-DD',
            applyLabel: 'Aplicar',
            cancelLabel: 'Cancelar'
        }
    })
    .on('apply.daterangepicker', function (ev, picker) {
        date_range = picker;
        generate_report_piscinas();
    })
    .on('cancel.daterangepicker', function () {
        date_range = null;
        generate_report_piscinas();
    });

    generate_report_piscinas();
});
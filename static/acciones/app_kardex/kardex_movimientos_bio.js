var tblProducts;
var date_now = new moment().format('YYYY-MM-DD');

function generate_report_stock() {
    if ($.fn.DataTable.isDataTable('#tb_kardex_movimientos_bio')) {
        $('#tb_kardex_movimientos_bio').DataTable().destroy();
    }

    tblProducts = $('#tb_kardex_movimientos_bio').DataTable({
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
            "processing": "<div class='spinner-border text-primary' role='status'><span class='sr-only'>Cargando...</span></div>"
        },

        processing: true,
        serverSide: true,

        paging: true,
        pageLength: 50,
        lengthMenu: [[25, 50, 100, 200], [25, 50, 100, 200]],

        responsive: true,
        autoWidth: false,
        deferRender: true,
        scrollY: "500px",
        scrollX: true,
        scrollCollapse: true,
        ordering: false,

        dom: 'Blfrtip',

        ajax: {
            url: window.location.pathname,
            type: 'POST',
            data: function(d) {
                d.action = 'searchdata';
                return d;
            }
        },

        columns: [
            {"data": "producto_empresa.nombre_empresa.siglas"},
            {"data": "fecha_ingreso"},
            {"data": "piscinas"},
            {"data": "cantidad_ingreso"},
            {"data": "cantidad_egreso"},
            {"data": "id"},
            {"data": "numero_guia"},
            {"data": "producto_empresa.nombre_prod.nombre"},
            {"data": "responsable_ingreso"},
        ],

        columnDefs: [
            {
                targets: [0, 1, 2, 3, 4, 6, 7, 8],
                className: 'text-center',
                orderable: false
            },
            {
                targets: [5],
                className: 'text-center',
                orderable: false,
                render: function(data, type, row) {
                    var ingreso = parseFloat(row.cantidad_ingreso) || 0;
                    var egreso = parseFloat(row.cantidad_egreso) || 0;
                    var saldo = ingreso - egreso;

                    if (row.tipo === 'INGRESO') {
                        return '<span style="background-color:#5f9ea0;color:white;padding:2px 8px;border-radius:3px;"><b>' + saldo.toFixed(0) + '</b></span>';
                    } else {
                        return '<span style="background-color:#f08080;color:white;padding:2px 8px;border-radius:3px;"><b>' + saldo.toFixed(0) + '</b></span>';
                    }
                }
            }
        ],

        buttons: [
            {
                extend: 'print',
                text: '<i class="fa fa-print"></i> ',
                titleAttr: 'Imprimir',
                className: 'btn btn-info',
                exportOptions: { modifier: { page: 'current' } }
            },
            {
                extend: 'copyHtml5',
                text: '<i class="fas fa-copy"></i> ',
                titleAttr: 'Copiar Datos',
                className: 'btn btn-secondary'
            },
            {
                extend: 'csvHtml5',
                text: '<i class="fas fa-file-csv"></i> ',
                titleAttr: 'Exportar a CSV',
                className: 'btn btn-success'
            },
            {
                extend: 'pdfHtml5',
                text: '<i class="fas fa-file-pdf"></i>',
                titleAttr: 'PDF',
                title: 'KARDEX DE MOVIMIENTO EMPRESA BIO',
                className: 'btn btn-danger btn-flat btn-xs',
                download: 'open',
                orientation: 'landscape',
                pageSize: 'LEGAL',
                exportOptions: { modifier: { page: 'current' } },
                customize: function(doc) {
                    doc.content[1].table.widths = ['6%', '7%', '10%', '7%', '7%', '7%', '24%', '17%', '15%'];
                    doc.content[1].margin = [0, 35, 0, 0];
                    doc['footer'] = function(page, pages) {
                        return {
                            columns: [
                                { alignment: 'left', text: ['Fecha de creacion: ', {text: date_now}] },
                                { alignment: 'right', text: ['pagina ', {text: page.toString()}, ' de ', {text: pages.toString()}] }
                            ],
                            margin: 20
                        }
                    };
                }
            }
        ],

        footerCallback: function(row, data, start, end, display) {
            var api = this.api();

            var total_ing = api.column(3, {page: 'current'}).data().reduce(function(a, b) {
                return parseFloat(a) + parseFloat(b || 0);
            }, 0);

            var total_eg = api.column(4, {page: 'current'}).data().reduce(function(a, b) {
                return parseFloat(a) + parseFloat(b || 0);
            }, 0);

            $(api.column(3).footer()).html(total_ing.toFixed(0));
            $(api.column(4).footer()).html(total_eg.toFixed(0));
            $(api.column(5).footer()).html((total_ing - total_eg).toFixed(0));
        }
    });
}

$(function() {
    generate_report_stock();
});
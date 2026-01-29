var tblProducts;
var date_now = new moment().format('YYYY-MM-DD');

function generate_report() {
    if ($.fn.DataTable.isDataTable('#tb_productos_empresa')) {
        $('#tb_productos_empresa').DataTable().destroy();
    }

    tblProducts = $('#tb_productos_empresa').DataTable({
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
        lengthMenu: [[25, 50, 100, 200, -1], [25, 50, 100, 200, "Todos"]],

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
            {"data": "nombre"},
            {"data": "codigo"},
            {"data": "stock_psm"},
            {"data": "stock_bio"},
            {"data": "stock_total"},
            {"data": "unid_medida"},
            {"data": "unidad_presentacion"},
        ],

        columnDefs: [
            {
                targets: [0],
                className: 'text-left',
                orderable: false
            },
            {
                targets: [1],
                className: 'text-center',
                orderable: false
            },
            {
                targets: [2],
                className: 'text-center stock-psm',
                orderable: false,
                render: function(data, type, row) {
                    return parseFloat(data).toFixed(1);
                }
            },
            {
                targets: [3],
                className: 'text-center stock-bio',
                orderable: false,
                render: function(data, type, row) {
                    return parseFloat(data).toFixed(1);
                }
            },
            {
                targets: [4],
                className: 'text-center stock-total',
                orderable: false,
                render: function(data, type, row) {
                    return parseFloat(data).toFixed(2);
                }
            },
            {
                targets: [5, 6],
                className: 'text-center',
                orderable: false
            }
        ],

        buttons: [
            {
                extend: 'print',
                text: '<i class="fa fa-print"></i> Imprimir',
                titleAttr: 'Imprimir',
                className: 'btn btn-info btn-sm',
                exportOptions: { modifier: { page: 'current' } }
            },
            {
                extend: 'csvHtml5',
                text: '<i class="fas fa-file-csv"></i> CSV',
                titleAttr: 'Exportar a CSV',
                className: 'btn btn-success btn-sm'
            },
            {
                extend: 'excelHtml5',
                text: '<i class="fas fa-file-excel"></i> Excel',
                titleAttr: 'Exportar a Excel',
                className: 'btn btn-success btn-sm'
            },
            {
                extend: 'pdfHtml5',
                text: '<i class="fas fa-file-pdf"></i> PDF',
                titleAttr: 'PDF',
                title: 'PRODUCTOS POR EMPRESA - STOCK TOTAL',
                className: 'btn btn-danger btn-sm',
                download: 'open',
                orientation: 'landscape',
                pageSize: 'LEGAL',
                exportOptions: { modifier: { page: 'current' } },
                customize: function(doc) {
                    doc.content[1].table.widths = ['25%', '8%', '12%', '12%', '12%', '10%', '21%'];
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

            var total_psm = api.column(2, {page: 'current'}).data().reduce(function(a, b) {
                return parseFloat(a) + parseFloat(b || 0);
            }, 0);

            var total_bio = api.column(3, {page: 'current'}).data().reduce(function(a, b) {
                return parseFloat(a) + parseFloat(b || 0);
            }, 0);

            var total_general = api.column(4, {page: 'current'}).data().reduce(function(a, b) {
                return parseFloat(a) + parseFloat(b || 0);
            }, 0);

            $(api.column(2).footer()).html(total_psm.toFixed(1));
            $(api.column(3).footer()).html(total_bio.toFixed(1));
            $(api.column(4).footer()).html(total_general.toFixed(2));
        }
    });
}

$(function() {
    generate_report();
});
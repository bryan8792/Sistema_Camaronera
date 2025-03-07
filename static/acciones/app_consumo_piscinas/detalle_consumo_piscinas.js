
var date_now = new moment().format('YYYY-MM-DD  -  hh:mm:ss');
var table;

var data = {
    list: function () {
        table = $('#tb_consumo_piscinas').DataTable({
            language: {
                "oPaginate": {
                    "sFirst": "Primero",
                    "sLast": "Último",
                    "sNext": "Siguiente",
                    "sPrevious": "Anterior"
                },
                "zeroRecords": "No se encontró nada, lo siento",
                "sInfo": "Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros",
                "infoEmpty": "Tabla vacia por favor inserte datos",
                "sSearch": "Buscar:",
                "infoFiltered": "(filtrado de _MAX_ registros totales)"
            },
            dom: 'Bfrtip',
            bPaginate: false,
            scrollY: "700px",
            destroy: true,
            deferRender: true,
            scrollX: true,
            ajax: {
                url: window.location.pathname,
                type: 'POST',
                data: {
                    'action': 'search_detalle_consumo'
                },
                dataSrc: ""
            },
            columns: [
                {"data": "producto_empresa.nombre_empresa.siglas"},
                {"data": "piscinas"},
                {"data": "fecha_ingreso"},
                {"data": "cantidad_egreso"},
                {"data": "numero_guia"},
                {"data": "producto_empresa.nombre_prod.nombre"},
                {"data": "responsable_ingreso"},
            ],
            buttons: [
                {
                    extend: 'excelHtml5',
                    text: '<i class="fas fa-file-csv"></i> ',
                    titleAttr: 'Exportar a Excell',
                    className: 'btn btn-success'
                },
                {
                    extend: 'print',
                    text: '<i class="fa fa-print"></i> ',
                    titleAttr: 'Imprimir',
                    className: 'btn btn-info',
                    title: 'CONSUMO POR PISCINAS "EMPRESAS PSM & BIO"',
                    orientation: 'landscape',
                    pageSize: 'LEGAL',
                },
                {
                    extend: 'pdfHtml5',
                    text: '<i class="fas fa-file-pdf"></i> ',
                    titleAttr: 'Exportar a PDF',
                    className: 'btn btn-danger',
                    title: 'CONSUMO POR PISCINAS "EMPRESAS PSM & BIO"',
                    download: 'open',
                    orientation: 'landscape',
                    pageSize: 'LEGAL',
                    customize: function (doc) {
                        doc.styles = {
                            title: {
                                fontSize: 22,
                                bold: true,
                                alignment: 'center'
                            },
                            header: {
                                fontSize: 18,
                                bold: true,
                                alignment: 'center'
                            },
                            subheader: {
                                fontSize: 13,
                                bold: true,
                                alignment: 'center'
                            },
                            quote: {
                                italics: true
                            },
                            small: {
                                fontSize: 8
                            },
                            tableHeader: {
                                bold: true,
                                fontSize: 11,
                                color: 'white',
                                fillColor: '#2d4154',
                                alignment: 'center'
                            },
                            body: {
                                bold: true,
                                fontSize: 11,
                                color: 'white'
                            },
                            tableBody: {
                                bold: true,
                                fontSize: 11,
                                color: 'white'
                            }
                        };
                        doc.content[1].table.widths = ['6%', '10%', '10%', '10%', '20%', '22%', '22%'];
                        doc.content[1].margin = [0, 35, 0, 0];
                        doc.content[1].layout = {};
                        doc['footer'] = (function (page, pages) {
                            return {
                                columns: [
                                    {
                                        alignment: 'left',
                                        text: ['Fecha de creación: ', {text: date_now}]
                                    },
                                    {
                                        alignment: 'right',
                                        text: ['página ', {text: page.toString()}, ' de ', {text: pages.toString()}]
                                    }
                                ],
                                margin: 20
                            }
                        });
                    }
                },
                {
                    extend: 'csvHtml5',
                    text: '<i class="fas fa-file-csv"></i> ',
                    titleAttr: 'Exportar a CSV',
                    className: 'btn btn-success'
                },

            ],
            columnDefs: [
                {
                    targets: [0],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '<b>' + data + '</b>';
                    }
                },
                {
                    targets: [1, 2, 3, 6],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return data;
                    }
                },
                {
                    targets: [-2],
                    class: 'text-left',
                    orderable: false,
                    render: function (data, type, row) {
                        return data;
                    }
                },
                {
                    targets: [-3],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return data;
                    }
                }
            ],
            initComplete: function (settings, json) {

            }
        });
    }
}

$(function () {

    data.list();

    // Crea la figura con los datos iniciales
    var container = $('<div/>').insertBefore(table.table().container());
    var chart = Highcharts.chart(container[0], {
        chart: {
            type: 'column',
        },
        title: {
            text: 'CONSUMO POR PISCINAS EMPRESAS PSM & BIO',
        },
        series: [
            {
                data: chartData(table),
            },
        ],
    });
    // En cada sorteo, actualice los datos en el gráfico
    table.on('draw', function () {
        chart.series[0].setData(chartData(table));
    });
});

function chartData(table) {
    var counts = {};
    // Cuenta el número de entradas para cada puesto
    table
        .column(5, {search: 'applied'})
        .data()
        .each(function (val) {
            if (counts[val]) {
                counts[val] += 1;
            } else {
                counts[val] = 1;
            }
        });
    // Y mapearlo al formato que usa en gráficos altos
    return $.map(counts, function (val, key) {
        return {
            name: key,
            y: val,
        };
    });
}
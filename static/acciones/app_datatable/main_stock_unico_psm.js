var tblProducts;
var date_range = null;
var date_now = new moment().format('YYYY-MM-DD');
var total = 0.00;
var total_stock = 0;
var cant_tot = 0, tot = 0;

function generate_report_stock() {
    var parameters = {
        'action': 'search_report',
        'start_date': date_now,
        'end_date': date_now,
    };

    if (date_range !== null) {
        parameters['start_date'] = date_range.startDate.format('YYYY-MM-DD');
        parameters['end_date'] = date_range.endDate.format('YYYY-MM-DD');
    }

    tblProducts = $('#tb_stock_unico_psm').DataTable({
        language: {
            "oPaginate": {
                "sFirst": "Primero",
                "sLast": "Último",
                "sNext": "Siguiente",
                "sPrevious": "Anterior"
            },
            "zeroRecords": "Ningun dato disponible en esta tabla",
            "sInfo": "Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros",
            "infoEmpty": "Tabla vacia por favor inserte datos",
            "lengthMenu": "Listando _MENU_ registros",
            "sSearch": "Buscar:",
            "infoFiltered": "(filtrado de _MAX_ registros totales)"
        },
        bPaginate: false,
        responsive: true,
        autoWidth: false,
        destroy: true,
        deferRender: true,
        scrollY: "600px",
        scrollX: true,
        //dom: 'Bfrtilp',
        bJQueryUI: true,
        order: false,
        paging: false,
        ordering: false,
        info: false,
        dom: 'Bfrtip',
        ajax: {
            url: window.location.pathname,
            type: 'POST',
            data: {
                'action': 'searchdata'
            },
            dataSrc: ""
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
                targets: [0, 1, 2, 3, 4],
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    return data;
                }
            },
            {
                targets: [-4],
                class: 'text-center',
                orderable: false,
                render: function (row, type, data) {
                    /*console.log('data')
                    console.log(data)
                    console.log('----------------------------------------------------------------------------------------------')
                    total = '';
                    ingreso = data.cantidad_ingreso;
                    egreso = data.cantidad_egreso;
                    if (data.cantidad_ingreso > 0)
                        total += data.cantidad_ingreso;
                    else
                        total -= data.cantidad_egreso;
                    return `$('td:eq(4)', row).html(total)`;*/
                    // return data;
                    // return data.cantidad_ingreso > 0 ? total += data.cantidad_ingreso : total -= data.cantidad_egreso;
                    return 'Total';
                }
            },
            {
                targets: [-1, -2, -3],
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    return data;
                }
            }
        ],
        initComplete: function (settings, json) {
            /*console.log(json);
            $.each(json,function (pos, dict){
                console.log('pos   '+pos);
                console.log('dict   '+dict.cantidad_ingreso);
                ingreso = dict.cantidad_ingreso;
                egreso = dict.cantidad_egreso;
                if(ingreso > 0){
                    total_stock += ingreso;
                }else{
                    total_stock -= egreso;
                }
                console.log('total_stock')
                console.log(total_stock)
            });*/
        },
        buttons: [
            /*{
                extend: 'print',
                text: '<i class="fa fa-print"></i> ',
                titleAttr: 'Imprimir',
                className: 'btn btn-info'
            },*/
            {
                extend: 'copyHtml5',
                text: '<i class="fas fa-copy"></i> ',
                titleAttr: 'Copiar Datos',
                className: 'btn btn-secondary'
            },
            /*{
                extend: 'csvHtml5',
                text: '<i class="fas fa-file-csv"></i> ',
                titleAttr: 'Exportar a CSV',
                className: 'btn btn-success'
            },*/
            {
                extend: 'pdfHtml5',
                text: '<i class="fas fa-file-pdf"></i>',
                titleAttr: 'PDF',
                title: 'KARDEX DE MOVIMIENTO DE PRODUCTO "EMPRESA PESQUERA SAN MIGUEL"',
                className: 'btn btn-danger btn-flat btn-xs',
                download: 'open',
                orientation: 'landscape',
                pageSize: 'LEGAL',
                customize: function (doc) {
                    var lastColX = null;
                    var lastColY = null;
                    var bod = [];
                    doc.content[1].table.body.forEach(function (line, i) {
                        console.log('line')
                        console.log(line)
                        if(lastColX !== line[0].text && line[0].text !== ''){
                            bod.push([
                                {text:'', style:'tableHeader'},
                                {text:'', style:'tableHeader'},
                                {text:'', style:'tableHeader'},
                                {text:'', style:'tableHeader'},
                                {text:'', style:'tableHeader'},
                                {text:'', style:'tableHeader'},
                                {text:'', style:'tableHeader'},
                                {text:'', style:'tableHeader'},
                                {text:'', style:'tableHeader'}
                            ]);
                            lastColX = line[0].text;
                            cant_tot = 0;
                            tot = 0;
                        }
                        if (i < doc.content[1].table.body.length - 1) {
                                cant_tot += parseFloat(line[3].text);
                                tot += parseFloat(line[4].text);
                            bod.push([
                                {text:line[0].text, style:'defaultStyle'},
                                {text:line[1].text, style:'defaultStyle'},
                                {text:line[2].text, style:'defaultStyle'},
                                {text:line[3].text, style:'defaultStyle'},
                                {text:line[4].text, style:'defaultStyle'},
                                {text:parseFloat(cant_tot-tot).toFixed(2), style:'defaultStyle'},
                                {text:line[6].text, style:'defaultStyle'},
                                {text:line[7].text, style:'defaultStyle'},
                                {text:line[8].text, style:'defaultStyle'}
                            ]);
                        } else {
                                cant_tot += parseFloat(line[3].text);
                                tot += parseFloat(line[4].text);
                            bod.push([
                                {text:line[0].text, style:'defaultStyle'},
                                {text:line[1].text, style:'defaultStyle'},
                                {text:line[2].text, style:'defaultStyle'},
                                {text:line[3].text, style:'defaultStyle'},
                                {text:line[4].text, style:'defaultStyle'},
                                {text: parseFloat(cant_tot-tot).toFixed(2), style:'defaultStyle'},
                                {text:line[6].text, style:'defaultStyle'},
                                {text:line[7].text, style:'defaultStyle'},
                                {text:line[8].text, style:'defaultStyle'}
                            ]);
                        }
                    });
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
                    doc.content[1].table.widths = ['7%', '15%', '10%', '5%', '5%', '7%', '16%', '20%', '15%'];
                    doc.content[1].margin = [0, 35, 0, 0];
                    // doc.content[1].layout = {};
                    doc.content[1].table.body = bod;
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
            }
        ],
        footerCallback: function (row, data, index) {

            total_ing = this.api()
                .column(3)
                //.column(3, {page: 'current'})//para sumar solo la pagina actual
                .data()
                .reduce(function (a, b) {
                    return parseInt(a) + parseInt(b);
                }, 0);
            $(this.api().column(3).footer()).html('' + parseFloat(total_ing).toFixed(2));

            total_eg = this.api()
                .column(4)
                //.column(4, {page: 'current'})//para sumar solo la pagina actual
                .data()
                .reduce(function (a, b) {
                    return parseInt(a) + parseInt(b);
                }, 0);
            $(this.api().column(4).footer()).html('' + parseFloat(total_eg).toFixed(2));
            $(this.api().column(5).footer()).html('' + parseFloat(total_ing - total_eg).toFixed(2));
        },
        rowCallback: function (row, data, index) {
            let contador = 0;
            for (let i = index; i <= index; i++) {
                contador = (i - 1);
                if (index > contador) {
                    cantidad_ingreso = parseFloat(data.cantidad_ingreso)
                    cantidad_egreso = parseFloat(data.cantidad_egreso)
                    if (cantidad_ingreso > 0) {
                        total_stock += cantidad_ingreso;
                        $('td', row).eq(5).css({'background-color': '#5f9ea0', 'color': 'black'});
                    } else {
                        total_stock -= cantidad_egreso;
                        $('td', row).eq(5).css({'background-color': '#f08080', 'color': 'black'});
                    }
                    $('td', row).eq(5).html('<b>' + total_stock.toFixed(2) + '</b>');

                }
            }
        }
    });
}

$(function () {

    generate_report_stock();

});
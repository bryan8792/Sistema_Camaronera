
var tblProducts;
var date_range = null;
var date_now = new moment().format('YYYY-MM-DD');
var total = 0;
var total_stock = 0;

function generate_report_stock() {

    tblProducts = $('#tb_stock_unico_directo_psm').DataTable({
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
                    console.log('data')
                    console.log(data)
                    console.log('----------------------------------------------------------------------------------------------')
                    total = '';
                    ingreso = data.cantidad_ingreso;
                    egreso = data.cantidad_egreso;
                    if (data.cantidad_ingreso > 0)
                        total += data.cantidad_ingreso;
                    else
                        total -= data.cantidad_egreso;
                    console.log(total)
                    return total;
                    // return data;
                    // return `<div id="resulta"></div>`;
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
            {
                extend: 'print',
                text: '<i class="fa fa-print"></i> ',
                titleAttr: 'Imprimir',
                className: 'btn btn-info'
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
                title: 'KARDEX DE MOVIMIENTO DE PRODUCTO "EMPRESA PESQUERA SAN MIGUEL"',
                className: 'btn btn-danger btn-flat btn-xs',
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
                    doc.content[1].table.widths = ['7%', '15%', '10%', '5%', '5%', '7%', '16%', '20%', '15%'];
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
            $(this.api().column(3).footer()).html('' + total_ing);

            total_eg = this.api()
                .column(4)
                //.column(4, {page: 'current'})//para sumar solo la pagina actual
                .data()
                .reduce(function (a, b) {
                    return parseInt(a) + parseInt(b);
                }, 0);
            $(this.api().column(4).footer()).html('' + total_eg);
            $(this.api().column(5).footer()).html('' + total_ing - total_eg);
        },
        rowCallback: function (row, data, index) {
            // aqui si sale bien pero añl imprimir no en cambio por este metodo de aca si sale al imprimir
            console.log('----------------------------------------------------------------------------------------------')
            let contador = 0;
            for (let i = index; i <= index; i++) {
                contador = (i - 1);
                if (index > contador) {
                    cantidad_ingreso = parseFloat(data.cantidad_ingreso)
                    cantidad_egreso = parseFloat(data.cantidad_egreso)
                    console.log('total : ' + total_stock);
                    if (cantidad_ingreso > 0) {
                        console.log('entro a ingreso');
                        total_stock += cantidad_ingreso;
                        $('td', row).eq(5).css({'background-color': '#5f9ea0', 'color': 'black'});
                    } else {
                        console.log('entro a egreso');
                        total_stock -= cantidad_egreso;
                        $('td', row).eq(5).css({'background-color': '#f08080', 'color': 'black'});
                    }
                    console.log('nuevo total ' + total_stock);
                    //$('td', row).eq(5).html('<b>' + total_stock.toFixed(0) + '</b>');
                    $('td', row).eq(5).html('<b>' + total_stock.toFixed(2) + '</b>');
                    // document.getElementById("resulta").innerHTML = total_stock;
                }
            }
        }
    });
}


$(function () {

    generate_report_stock();

});
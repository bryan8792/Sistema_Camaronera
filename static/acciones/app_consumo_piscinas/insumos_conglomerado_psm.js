
var date_range = null;
var multiplicadora = 0, total_stock = 0;
var tb_piscinas_por_insumos;
var total, group_assoc, group_total, total_seg;
var groupColumn = 1;
var total_ing = 0;
var total_eg = 0;
var cant_tot = 0, tot = 0;
var date_now = new moment().format('YYYY-MM-DD');

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


function generate_report_piscinas() {
    var parameters = {
        'action': 'search_insumos_conglomerado_psm',
        'start_date': date_now,
        'end_date': date_now,
    };

    if (date_range !== null) {
        parameters['start_date'] = date_range.startDate.format('YYYY-MM-DD');
        parameters['end_date'] = date_range.endDate.format('YYYY-MM-DD');
    }

    tb_piscinas_por_insumos = $('#insumos_conglomerado_psm').DataTable({
        destroy: true,
        lengthChange: false,
        fixedHeader: true,
        //responsive: true,
        language: {
            "lengthMenu": "Mostrar _MENU_ registros",
            "zeroRecords": "No se encontraron resultados",
            "info": "Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros",
            "infoEmpty": "Mostrando registros del 0 al 0 de un total de 0 registros",
            "infoFiltered": "(filtrado de un total de _MAX_ registros)",
            "sSearch": "Buscar:",
            "oPaginate": {
                "sFirst": "Primero",
                "sLast": "Último",
                "sNext": "Siguiente",
                "sPrevious": "Anterior"
            },
            "sProcessing": "Procesando...",
        },
        //order: [[0, 'asc']],
        autoWidth: false,
        deferRender: true,
        ajax: {
            url: window.location.pathname,
            type: 'POST',
            data: parameters,
            dataSrc: ""
        },
        // order: true,
        // ordering: true,
        scrollY: "550px",
        scrollX: true,
        paging: false,
        info: false,
        dom: 'Bfrtip',
        buttons: [
            {
                extend: 'excelHtml5',
                text: '<i class="fas fa-file-excel"></i> ',
                titleAttr: 'Exportar a Excell',
                className: 'btn btn-success',
                customize: function (doc) {
                    console.log("PRESENTANDO doc")
                    console.log(doc)
                    console.log("doc.data")
                    console.log(doc.data)
                    /*doc.content[1].table.body.forEach(function (line, i) {
                        console.log("line")
                        console.log(line)
                        console.log("i")
                        console.log(i)
                    })*/
                }
            },
            {
                extend: 'print',
                text: '<i class="fa fa-print"></i> ',
                titleAttr: 'Imprimir',
                className: 'btn btn-info'
            },
            {
                extend: 'pdfHtml5',
                text: '<i class="fas fa-file-pdf"></i> ',
                titleAttr: 'Exportar a PDF',
                className: 'btn btn-danger',
                download: 'open',
                //orientation: 'landscape',
                orientation: 'portrait',
                pageSize: 'LEGAL',
                footer : true,
                header: true,
                customize: function (doc) {
                    var lastColX = null;
                    var lastColY = null;
                    var bod = [];
                    doc.content[1].table.body.forEach(function (line, i) {
                        if(lastColX !== line[0].text && line[0].text !== ''){
                            bod.push([
                                {text: '', style:'tableHeader'},
                                {text: '', style:'tableHeader'},
                                {text: '', style:'tableHeader'},
                                {text: cant_tot.toFixed(2) > 0 ? cant_tot.toFixed(2) : '', style:'tableHeader'},
                                {text: '', style:'tableHeader'},
                                {text: tot.toFixed(2) > 0 ? tot.toFixed(2) : '', style:'tableHeader'}
                            ]);

                            bod.push([
                                {text:line[0].text, style:'tableHeader'},
                                {text: '', style:'tableHeader'},
                                {text: '', style:'tableHeader'},
                                {text: '', style:'tableHeader'},
                                {text: '', style:'tableHeader'},
                                {text: '', style:'tableHeader'}
                            ]);
                            //Update last
                            lastColX = line[0].text;
                            cant_tot = 0;
                            tot = 0;
                        }
                        if (i < doc.content[1].table.body.length - 1) {
                                cant_tot += parseFloat(line[2].text);
                                tot += parseFloat(line[4].text);
                            bod.push([
                                '', //{text: line[0].text, style: 'defaultStyle'},
                                '',
                                {text: line[1].text, style: 'defaultStyle'},
                                {text: line[2].text, style: 'defaultStyle'},
                                {text: line[3].text, style: 'defaultStyle'},
                                {text: line[4].text, style: 'defaultStyle'},
                                ]
                            );
                        } else {
                                cant_tot += parseFloat(line[2].text);
                                tot += parseFloat(line[4].text);
                            bod.push([
                                '', //{text: line[0].text, style: 'defaultStyle'},
                                '',
                                {text: line[1].text, style: 'defaultStyle'},
                                {text: line[2].text, style: 'defaultStyle'},
                                {text: line[3].text, style: 'defaultStyle'},
                                {text: line[4].text, style: 'defaultStyle'},
                                ]
                            );
                            bod.push([
                                {text: '', style:'tableHeader'},
                                {text: '', style:'tableHeader'},
                                {text: '', style:'tableHeader'},
                                {text: cant_tot.toFixed(2) > 0 ? cant_tot.toFixed(2) : '', style:'tableHeader'},
                                {text: '', style:'tableHeader'},
                                {text: tot.toFixed(2) > 0 ? tot.toFixed(2) : '', style:'tableHeader'}
                            ]);
                        }
                    });
                    doc.content[1].table.headerRows = 1;
                    doc.content[1].table.widths = [130, 1, 60, 100, 50, 50, 50];
                    doc.content[1].table.body = bod;
                    doc.content[1].layout = 'lightHorizontalLines';
                    doc.styles = {
                        header: {
                            fontSize: 22,
                            bold: true,
                            alignment: 'center'
                        },
                        subheader: {
                            fontSize: 10,
                            bold: true,
                            color: 'black'
                        },
                        tableHeader: {
                            bold: true,
                            fontSize: 11,
                            color: 'white',
                            fillColor: '#2d4154',
                            alignment: 'center'
                        },
                        lastLine: {
                            bold: true,
                            fontSize: 11,
                            color: 'black'
                        },
                        defaultStyle: {
                            fontSize: 10,
                            color: 'black'
                        }
                    }
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
                    doc['header'] = (function (page, pages) {
                        return {
                            columns: [
                                {
                                    alignment: 'center',
                                    text: ['DETALLE DE INSUMOS POR PISCINAS',' PSM & BIO'],
                                    margin: [0, 10]
                                }
                            ],
                            margin: [30, 0]
                        }
                    });
                }
                /*customize: function (doc) {
                    var lastColX = null;
                    var lastColY = null;
                    var acum1=0, acum2=0, acum3=0;
                    var bod = [];
                    doc.content[1].table.body.forEach(function (line, i) {
                        /!*if(lastColX !== line[0].text && line[0].text !== ''){

                            /!*bod.push([
                                {text:line[0].text, style:'tableHeader'},
                                {text: '', style:'tableHeader'},
                                {text: '', style:'tableHeader'},
                                {text: '', style:'tableHeader'},
                                {text: '', style:'tableHeader'},
                                {text: '', style:'tableHeader'}
                            ]);*!/
                            //Update last
                            lastColX = line[0].text;
                            cant_tot = 0;
                            tot = 0;
                        }*!/
                        acum1 += line[0].text;
                        bod.push([
                            {text: acum1 , style: i},
                            '',
                            {text: line[1].text, style: 'defaultStyle'},
                            {text: line[2].text, style: 'defaultStyle'},
                            {text: line[3].text, style: 'defaultStyle'},
                            {text: line[4].text, style: 'defaultStyle'},]
                        );
                        /!*if (i < doc.content[1].table.body.length - 1) {
                            bod.push([
                                {text: line[0].text, style: 'defaultStyle'},
                                '',
                                {text: line[1].text, style: 'defaultStyle'},
                                {text: line[2].text, style: 'defaultStyle'},
                                {text: line[3].text, style: 'defaultStyle'},
                                {text: line[4].text, style: 'defaultStyle'},]
                            );
                        } else {
                            bod.push([
                                {text: line[0].text, style: 'defaultStyle'},
                                '',
                                {text: line[1].text, style: 'defaultStyle'},
                                {text: line[2].text, style: 'defaultStyle'},
                                {text: line[3].text, style: 'defaultStyle'},
                                {text: line[4].text, style: 'defaultStyle'},]
                            );
                            bod.push([
                                {text: '', style:'tableHeader'},
                                {text: '', style:'tableHeader'},
                                {text: '', style:'tableHeader'},
                                {text: cant_tot.toFixed(2) > 0 ? cant_tot.toFixed(2) : '', style:'tableHeader'},
                                {text: '', style:'tableHeader'},
                                {text: tot.toFixed(2) > 0 ? tot.toFixed(2) : '', style:'tableHeader'}
                            ]);
                        }*!/
                    });
                    doc.content[1].table.headerRows = 1;
                    doc.content[1].table.widths = [150, 16, 100, 50, 50, 50];
                    doc.content[1].table.body = bod;
                    doc.content[1].layout = 'lightHorizontalLines';
                    doc.styles = {
                        header: {
                            fontSize: 22,
                            bold: true,
                            alignment: 'center'
                        },
                        subheader: {
                            fontSize: 10,
                            bold: true,
                            color: 'black'
                        },
                        tableHeader: {
                            bold: true,
                            fontSize: 11,
                            color: 'white',
                            fillColor: '#2d4154',
                            alignment: 'center'
                        },
                        lastLine: {
                            bold: true,
                            fontSize: 11,
                            color: 'black'
                        },
                        defaultStyle: {
                            fontSize: 10,
                            color: 'black'
                        }
                    }
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
                    doc['header'] = (function (page, pages) {
                        return {
                            columns: [
                                {
                                    alignment: 'center',
                                    text: ['DETALLE DE PISCINAS POR INSUMOS',' PSM & BIO'],
                                    margin: [0, 10]
                                }
                            ],
                            margin: [30, 0]
                        }
                    });
                }*/
            }
        ],
        columns: [
            {"data": "producto_empresa.nombre_prod.nombre","width": "50%"},
            // {"data": "piscinas","width": "20%"},
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
            // {
            //     targets: [3],
            //     class: 'text-center',
            //     orderable: false,
            //     render: function (data, type, row) {
            //         /*console.log("PRESENTANDO A ROW");
            //         console.log(row);*/
            //         return data;
            //     }
            // },
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
                console.log('valor', valor)
                console.log('indice', indice)
                if (movimientos_encontrados.indexOf(valor.producto_empresa.nombre_prod.nombre) === -1) {
                    movimientos_encontrados.push(valor.producto_empresa.nombre_prod.nombre);
                    nuevo_ArrayObject.push(valor);
                } else {
                    var recuperado = movimientos_encontrados.indexOf(valor.producto_empresa.nombre_prod.nombre);
                    var objetoRecuperado = nuevo_ArrayObject[recuperado];
                    objetoRecuperado.cantidad_egreso = parseFloat(objetoRecuperado.cantidad_egreso) + parseFloat(valor.cantidad_egreso);
                }
            });

            var total_consumos=0, cantidad=0.00, costo=0.000000000, acum1=0, acum2=0;
            var table = '<table class="table">';
            nuevo_ArrayObject.map(function (valor, indice) {
                cantidad = parseFloat(valor.cantidad_egreso);
                costo = parseFloat(valor.producto_empresa.nombre_prod.costo_aplicacion);
                total_consumos = parseFloat(cantidad * costo);
                table+='<tr>'
                table+='<td style="width: 50%; text-align: left"">'+valor.producto_empresa.nombre_prod.nombre+'</td>'
                // table+='<td scope="col" style="width: 20%; text-align: center" >'+ valor.piscinas +'</td>'
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

            document.getElementById("insumos_conglomerado_psm").innerHTML = table;
            //$(table).appendTo("#tb_piscinas_por_insumos");
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
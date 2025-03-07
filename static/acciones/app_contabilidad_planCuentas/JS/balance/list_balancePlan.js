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

function mayor_list() {
    var groupColumn = 0;
    tb_mayor_list = $('#tb_mayorizacion_plan').DataTable({
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
        responsive: true,
        bPaginate: false,
        autoWidth: false,
        destroy: true,
        deferRender: true,
        scrollY: "700px",
        scrollX: true,
        // bFilter: false,
        bInfo: false,
        dom: 'Bfrtip',
        ajax: {
            url: window.location.pathname,
            type: 'POST',
            data: {
                'action': 'searchdata'
            },
            dataSrc: ""
        },
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
                className: 'btn btn-info'
            },
            {
                extend: 'pdfHtml5',
                text: '<i class="fas fa-file-pdf"></i> ',
                titleAttr: 'Exportar a PDF',
                className: 'btn btn-danger',
                download: 'open',
                orientation: 'landscape',
                //orientation: 'portrait',
                pageSize: 'LEGAL',
                footer: true,
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
                                {text: '', style:'tableHeader'},
                                {text: '', style:'tableHeader'},
                                {text: '', style:'tableHeader'},
                                {text: '', style:'tableHeader'},
                                // {text: cant_tot.toFixed(2) > 0 ? cant_tot.toFixed(2) : '', style:'tableHeader'},
                                {text: '', style:'tableHeader'},
                                // {text: tot.toFixed(2) > 0 ? tot.toFixed(2) : '', style:'tableHeader'}
                            ]);

                            bod.push([
                                {text:line[0].text, style:'tableHeader'},
                                {text:line[1].text, style:'tableHeader'},
                                {text: '', style:'tableHeader'},
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
                                cant_tot += parseFloat(line[3].text);
                                tot += parseFloat(line[5].text);
                            bod.push([
                                {text: line[0].text, style: 'defaultStyle'},
                                {text: line[1].text, style: 'defaultStyle'},
                                {text: line[2].text, style: 'defaultStyle'},
                                {text: line[3].text, style: 'defaultStyle'},
                                {text: line[4].text, style: 'defaultStyle'},
                                {text: line[5].text, style: 'defaultStyle'},
                                {text: line[6].text, style: 'defaultStyle'},
                                {text: line[7].text, style: 'defaultStyle'}]
                            );
                        } else {
                                cant_tot += parseFloat(line[3].text);
                                tot += parseFloat(line[5].text);
                            bod.push([
                                {text: line[0].text, style: 'defaultStyle'},
                                {text: line[1].text, style: 'defaultStyle'},
                                {text: line[2].text, style: 'defaultStyle'},
                                {text: line[3].text, style: 'defaultStyle'},
                                {text: line[4].text, style: 'defaultStyle'},
                                {text: line[5].text, style: 'defaultStyle'},
                                {text: line[6].text, style: 'defaultStyle'},
                                {text: line[7].text, style: 'defaultStyle'}]
                            );
                            bod.push([
                                {text: '', style:'tableHeader'},
                                {text: '', style:'tableHeader'},
                                {text: '', style:'tableHeader'},
                                {text: '', style:'tableHeader'},
                                {text: '', style:'tableHeader'},
                                {text: '', style:'tableHeader'},
                                {text: '', style:'tableHeader'},
                                // {text: cant_tot.toFixed(2) > 0 ? cant_tot.toFixed(2) : '', style:'tableHeader'},
                                {text: '', style:'tableHeader'},
                                // {text: tot.toFixed(2) > 0 ? tot.toFixed(2) : '', style:'tableHeader'}
                            ]);
                        }
                    });
                    doc.content[1].table.headerRows = 1;
                    doc.content[1].table.widths = [130, 290, 60, 60, 60, 60, 60, 60];
                    doc.content[1].table.body = bod;
                    doc.content[1].layout = 'lightHorizontalLines';
                    doc.styles = {
                        header: {
                            fontSize: 35,
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
                            fontSize: 12,
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
                                    text: ['Balance de Comprobación',' Empresa PSM'],
                                    margin: [0, 10]
                                }
                            ],
                            margin: [30, 0]
                        }
                    });
                }
            }
        ],
        columns: [
            {"data": "codigo_cuenta_plan"},
            {"data": "nombre_cuenta_plan"},
            {"data": "debe"},
            {"data": "haber"},
            {"data": "debe"},
            {"data": "haber"},
            {"data": "debe"},
            {"data": "haber"},
            // {"data": "encabezadocuentaplan"},
        ],
        columnDefs: [
            {
                targets: [0],
                class: 'text-center',
                orderable: false,
                // visible: false,
                render: function (data, type, row) {

                    return data;
                }
            },
            {
                targets: [1],
                class: 'text-left',
                orderable: false,
                // visible: false,
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
                    return data;
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
                    acum = total
                    /*console.log('acum')
                    console.log(acum)*/
                    return parseFloat(acum).toFixed(2);
                }
            },
        ],

        initComplete: function (settings, json) {
            console.log('AQUI INICIA EL PROCESO')
            var movimientos_encontrados = new Array();
            var nuevo_ArrayObject = new Array();

            json.map(function (valor, indice) {
                console.log('valor del json', valor)
                console.log('indice del json', indice)
                if (movimientos_encontrados.indexOf(valor.codigo_cuenta_plan) === -1) {
                    movimientos_encontrados.push(valor.codigo_cuenta_plan);
                    nuevo_ArrayObject.push(valor);
                } else {
                    var recuperado = movimientos_encontrados.indexOf(valor.codigo_cuenta_plan);
                    var objetoRecuperado = nuevo_ArrayObject[recuperado];
                    objetoRecuperado.debe = parseFloat(objetoRecuperado.debe) + parseFloat(valor.debe);
                }
            });

            var total_consumos = 0, cantidad = 0.00, costo = 0.000000000, acum1 = 0, acum2 = 0;
            var table = '<table class="table">';
            nuevo_ArrayObject.map(function (valor, indice) {
                /*console.log('valor del nuevo_ArrayObject', valor)
                console.log('indice del nuevo_ArrayObject', indice)*/
                console.log('valor.nombre_cuenta_plan: ', valor.nombre_cuenta_plan, ' valor.debe :', valor.debe, ' valor.haber: ', valor.haber)
                total_consumos = parseFloat(cantidad - costo);
                table += '<tr>'
                table += '<td scope="col" style="text-align: center"">' + valor.codigo_cuenta_plan + '</td>'
                // table+='<td scope="col" style="text-align: left" >'+ valor.nombre_cuenta_plan + '<br><hr>' + valor.nombre_cuenta_plan +'</td>'
                table += '<td scope="col" style="text-align: left" >' + valor.nombre_cuenta_plan + '</td>'
                table += '<td scope="col" style="text-align: center">' + valor.debe + '</td>'
                table += '<td scope="col" style="text-align: center">' + valor.haber + '</td>'
                table += '<td scope="col" style="text-align: center">' + valor.debe + '</td>'
                table += '<td scope="col" style="text-align: center">' + valor.haber + '</td>'
                table += '<td scope="col" style="text-align: center">' + valor.debe + '</td>'
                table += '<td scope="col" style="text-align: center">' + valor.haber + '</td>'
                table += '</tr>';
                acum1 += cantidad;
                acum2 += total_consumos;

            });
            table += '<tr>'
            table += '<th colspan="2" scope="col" style="text-align: center"> Total</th>'
            table += '<th scope="col" style="text-align: center">' + acum1.toFixed(2) + '</th>'
            table += '<th scope="col"></th>'
            table += '<th scope="col" style="text-align: center">' + acum2.toFixed(2) + '</th>'
            table += '<th scope="col"></th>'
            table += '<th scope="col"></th>'
            table += '<th scope="col"></th>'
            table += '</tr>';

            table += '</table>';

            document.getElementById("tb_mayorizacion_plan").innerHTML = table;
            //$(table).appendTo("#tb_piscinas_por_insumos");
            // console.log(table)
        },
        rowGroup: {
            "dataSrc": "codigo_cuenta_plan",
            "startRender": function (rows, group) {
                var concatOffice = rows
                    .data()
                    .pluck('nombre_cuenta_plan')
                    .toArray()
                    .join(', ');
                return group + ' - ' + concatOffice;
            }
        },
        hierarchy: {
            display: 'group'
        }
    });
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
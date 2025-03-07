var date_range = null;
var tb_mayor_list_range;
var date_now = new moment().format('YYYY-MM-DD');
var plan_det = [];
var desde_rang, hasta_rang, contador_ult;

var params = {

    list: function () {

        var parameters = {
            'action': 'search_report',
            'start_date': date_now,
            'end_date': date_now,
            'desde_rang': desde_rang,
            'hasta_rang': hasta_rang,
        };

        if (date_range !== null && (desde_rang > 0 && hasta_rang > 0)) {
            parameters['start_date'] = date_now
            parameters['end_date'] = date_now
            parameters['desde_rang'] = desde_rang;
            parameters['hasta_rang'] = hasta_rang;
        }

        var groupColumn = 0;
        tb_mayor_list_range = $('#date_range').DataTable({
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
            //responsive: true,
            autoWidth: false,
            destroy: true,
            deferRender: true,
            scrollY: "700px",
            scrollX: true,
            paging: false,
            info: true,
            dom: 'Bfrtip',
            ajax: {
                url: window.location.pathname,
                type: 'POST',
                data: parameters,
                dataSrc: ""
            },
            buttons: [
                {
                    extend: 'excelHtml5',
                    text: 'Descargar Excel <i class="fas fa-file-excel"></i>',
                    titleAttr: 'Excel',
                    className: 'btn btn-success btn-flat btn-xs'
                },
                {
                    extend: 'pdfHtml5',
                    text: 'Descargar Pdf <i class="fas fa-file-pdf"></i>',
                    titleAttr: 'PDF',
                    className: 'btn btn-danger btn-flat btn-xs',
                    download: 'open',
                    orientation: 'landscape',
                    pageSize: 'LEGAL',
                    footer: true,
                    header: true,
                    customize: function (doc) {
                        var lastColX = null;
                        var lastColY = null;
                        var bod = [];
                        doc.content[1].table.body.forEach(function (line, i) {
                            if (lastColX !== line[0].text && line[0].text !== '') {
                                bod.push([
                                    {text: '', style: 'tableHeader'},
                                    {text: '', style: 'tableHeader'},
                                    {text: '', style: 'tableHeader'},
                                    {
                                        text: tot_deb.toFixed(2) > 0.00 ? tot_deb.toFixed(2) : tot_deb.toFixed(2) === '0.00' ? '0.00' : ' ',
                                        style: 'tableHeader'
                                    },
                                    {
                                        text: tot_hab.toFixed(2) > 0.00 ? tot_hab.toFixed(2) : tot_hab.toFixed(2) === '0.00' ? '0.00' : ' ',
                                        style: 'tableHeader'
                                    },
                                    {
                                        text: tot_sal.toFixed(2) !== 'NaN' ? tot_sal.toFixed(2) : '',
                                        style: 'tableHeader'
                                    },
                                ]);

                                bod.push([
                                    {text: line[0].text, style: 'tableHeader'},
                                    {text: line[1].text, style: 'tableHeader'},
                                    {text: '', style: 'tableHeader'},
                                    {text: '', style: 'tableHeader'},
                                    {text: '', style: 'tableHeader'},
                                    {text: '', style: 'tableHeader'}
                                ]);
                                //Update last
                                lastColX = line[0].text;
                                tot_deb = 0.00;
                                tot_hab = 0.00;
                                tot_sal = 0.00;
                            }
                            if (i < doc.content[1].table.body.length - 1) {
                                tot_deb += parseFloat(line[6].text);
                                tot_hab += parseFloat(line[7].text);
                                tot_sal += parseFloat(line[8].text);
                                bod.push([
                                    {text: line[4].text, style: 'defaultStyle'},
                                    {text: line[5].text, style: 'defaultStyle'},
                                    {text: line[2].text, style: 'defaultStyle'},
                                    {text: line[6].text, style: 'defaultStyle'},
                                    {text: line[7].text, style: 'defaultStyle'},
                                    {text: line[8].text, style: 'defaultStyle'}]
                                );
                            } else {
                                tot_deb += parseFloat(line[6].text);
                                tot_hab += parseFloat(line[7].text);
                                tot_sal += parseFloat(line[8].text);
                                bod.push([
                                    {text: line[4].text, style: 'defaultStyle'},
                                    {text: line[5].text, style: 'defaultStyle'},
                                    {text: line[2].text, style: 'defaultStyle'},
                                    {text: line[6].text, style: 'defaultStyle'},
                                    {text: line[7].text, style: 'defaultStyle'},
                                    {text: line[8].text, style: 'defaultStyle'}]
                                );
                                bod.push([
                                    {text: '', style: 'tableHeader'},
                                    {text: '', style: 'tableHeader'},
                                    {text: '', style: 'tableHeader'},
                                    {
                                        text: tot_deb.toFixed(2) > 0.00 ? tot_deb.toFixed(2) : tot_deb.toFixed(2) === '0.00' ? '0.00' : ' ',
                                        style: 'tableHeader'
                                    },
                                    {
                                        text: tot_hab.toFixed(2) > 0.00 ? tot_hab.toFixed(2) : tot_hab.toFixed(2) === '0.00' ? '0.00' : ' ',
                                        style: 'tableHeader'
                                    },
                                    {
                                        text: tot_sal.toFixed(2) !== 'NaN' ? tot_sal.toFixed(2) : '',
                                        style: 'tableHeader'
                                    },
                                ]);
                            }
                        });
                        doc.content[1].table.headerRows = 1;
                        doc.content[1].table.widths = [90, 440, 75, 80, 80, 80];
                        doc.content[1].table.body = bod;
                        doc.content[1].layout = 'lightHorizontalLines';
                        doc.styles = {
                            header: {
                                fontSize: 32,
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
                                        text: ['Fecha de creación: ', {text: date_now}, ' Hora: ', {text: hour_now}]
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
                                        text: ['ANALITICO AUXILIAR DE CUENTAS ', ' - DETALLE'],
                                        margin: [0, 10]
                                    }
                                ],
                                margin: [30, 0]
                            }
                        });
                    }
                }
            ],
            /*columns: [
                {"data": "codigo_cuenta_plan", 'width': '15%'},
                {"data": "nombre_cuenta_plan", 'width': '15%'},
                {"data": "detalle", 'width': '40%'},
                {"data": "fecha_asiento_transaccion", 'width': '8%'},
                {"data": "nombre_asiento_transaccion", 'width': '5%'},
                {"data": "codigo_asiento_transaccion", 'width': '5%'},
                {"data": "debe", 'width': '5%'},
                {"data": "haber", 'width': '5%'},
                {"data": "encabezadocuentaplan", 'width': '5%'},
            ],*/
            columns: [
                {"data": "codigo_cuenta_plan"},
                {"data": "nombre_cuenta_plan"},
                {"data": "debe"},
                {"data": "haber"},
                {"data": "debe"},
                {"data": "haber"},
                {"data": "debe"},
                {"data": "haber"},
                {"data": "encabezadocuentaplan"},
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
                        acum = total
                        return parseFloat(acum).toFixed(2);
                    }
                },
            ],
            rowCallback: function (row, data, index) {
                var tr = $(row).closest('tr');
                const json = tb_mayor_list_range.rows().data().toArray();

                for (let i = 0; i < json.length; i++) {
                    for (let j = i; j <= index; j++) {
                        if (i === j) {
                            if ((i > 0 && json[i]['codigo_cuenta_plan'] === json[i - 1]["codigo_cuenta_plan"])) {
                                json[i]["saldo"] = (parseFloat(json[i]['debe']) - parseFloat(json[i]['haber'])) + parseFloat(json[i - 1]['saldo']);
                            } else {
                                json[i]["saldo"] = parseFloat(json[i]['debe']) - parseFloat(json[i]['haber']);
                            }
                            $('td:eq(-1)', tb_mayor_list_range.row(tr).node()).html('<b>' + parseFloat(json[i]["saldo"]).toFixed(2) + '</b>');
                        }
                    }
                }
            },
            /*drawCallback: function (settings) {

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
                            if (dict._aFilterData[0] === group) {
                                resultado = dict._aFilterData[1]
                            }
                        })

                        $(rows).eq(i).before(
                            '<tr class="group text-left" style="background-color:rgb(255, 255, 255);font-weight:700;">' +
                            '<td colspan="6" style="width: 100%">' + "Cuenta de Mayor: &nbsp;" + group + ' &nbsp; / &nbsp; ' + resultado + '</td>' +
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
            },*/
            initComplete: function (settings, json) {
            }
        });

    }

}

function generate_report() {

    var parameters = {
        'action': 'search_report',
        'start_date': date_now,
        'end_date': date_now,
        'desde_rang': desde_rang,
        'hasta_rang': hasta_rang,
    };

    if (date_range !== null && (desde_rang > 0 && hasta_rang > 0)) {
        parameters['start_date'] = date_range.startDate.format('YYYY-MM-DD');
        parameters['end_date'] = date_range.endDate.format('YYYY-MM-DD');
        parameters['desde_rang'] = desde_rang;
        parameters['hasta_rang'] = hasta_rang;
    } else if (date_range !== null || (desde_rang <= 0 && hasta_rang <= 0)) {
        parameters['start_date'] = date_range.startDate.format('YYYY-MM-DD');
        parameters['end_date'] = date_range.endDate.format('YYYY-MM-DD');
        parameters['desde_rang'] = 1;
        parameters['hasta_rang'] = contador_ult;
    }

    var groupColumn = 0;
    tb_mayor_list_range = $('#date_range').DataTable({
        //responsive: true,
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
        //responsive: true,
        autoWidth: false,
        destroy: true,
        deferRender: true,
        scrollY: "700px",
        scrollX: true,
        paging: false,
        info: true,
        dom: 'Bfrtip',
        ajax: {
            url: window.location.pathname,
            type: 'POST',
            data: parameters,
            dataSrc: ""
        },
        buttons: [
            {
                extend: 'excelHtml5',
                text: 'Descargar Excel <i class="fas fa-file-excel"></i>',
                titleAttr: 'Excel',
                className: 'btn btn-success btn-flat btn-xs'
            },
            {
                extend: 'pdfHtml5',
                text: 'Descargar Pdf <i class="fas fa-file-pdf"></i>',
                titleAttr: 'PDF',
                className: 'btn btn-danger btn-flat btn-xs',
                download: 'open',
                orientation: 'landscape',
                pageSize: 'LEGAL',
                footer: true,
                header: true,
                customize: function (doc) {
                    var lastColX = null;
                    var lastColY = null;
                    var bod = [];
                    doc.content[1].table.body.forEach(function (line, i) {
                        if (lastColX !== line[0].text && line[0].text !== '') {
                            bod.push([
                                {text: '', style: 'tableHeader'},
                                {text: '', style: 'tableHeader'},
                                {text: '', style: 'tableHeader'},
                                {
                                    text: tot_deb.toFixed(2) > 0.00 ? tot_deb.toFixed(2) : tot_deb.toFixed(2) === '0.00' ? '0.00' : ' ',
                                    style: 'tableHeader'
                                },
                                {
                                    text: tot_hab.toFixed(2) > 0.00 ? tot_hab.toFixed(2) : tot_hab.toFixed(2) === '0.00' ? '0.00' : ' ',
                                    style: 'tableHeader'
                                },
                                {
                                    text: tot_sal.toFixed(2) !== 'NaN' ? tot_sal.toFixed(2) : '',
                                    style: 'tableHeader'
                                },
                            ]);

                            bod.push([
                                {text: line[0].text, style: 'tableHeader'},
                                {text: line[1].text, style: 'tableHeader'},
                                {text: '', style: 'tableHeader'},
                                {text: '', style: 'tableHeader'},
                                {text: '', style: 'tableHeader'},
                                {text: '', style: 'tableHeader'}
                            ]);
                            //Update last
                            lastColX = line[0].text;
                            tot_deb = 0.00;
                            tot_hab = 0.00;
                            tot_sal = 0.00;
                        }
                        if (i < doc.content[1].table.body.length - 1) {
                            tot_deb += parseFloat(line[6].text);
                            tot_hab += parseFloat(line[7].text);
                            tot_sal += parseFloat(line[8].text);
                            bod.push([
                                {text: line[4].text, style: 'defaultStyle'},
                                {text: line[5].text, style: 'defaultStyle'},
                                {text: line[2].text, style: 'defaultStyle'},
                                {text: line[6].text, style: 'defaultStyle'},
                                {text: line[7].text, style: 'defaultStyle'},
                                {text: line[8].text, style: 'defaultStyle'}]
                            );
                        } else {
                            tot_deb += parseFloat(line[6].text);
                            tot_hab += parseFloat(line[7].text);
                            tot_sal += parseFloat(line[8].text);
                            bod.push([
                                {text: line[4].text, style: 'defaultStyle'},
                                {text: line[5].text, style: 'defaultStyle'},
                                {text: line[2].text, style: 'defaultStyle'},
                                {text: line[6].text, style: 'defaultStyle'},
                                {text: line[7].text, style: 'defaultStyle'},
                                {text: line[8].text, style: 'defaultStyle'}]
                            );
                            bod.push([
                                {text: '', style: 'tableHeader'},
                                {text: '', style: 'tableHeader'},
                                {text: '', style: 'tableHeader'},
                                {
                                    text: tot_deb.toFixed(2) > 0.00 ? tot_deb.toFixed(2) : tot_deb.toFixed(2) === '0.00' ? '0.00' : ' ',
                                    style: 'tableHeader'
                                },
                                {
                                    text: tot_hab.toFixed(2) > 0.00 ? tot_hab.toFixed(2) : tot_hab.toFixed(2) === '0.00' ? '0.00' : ' ',
                                    style: 'tableHeader'
                                },
                                {
                                    text: tot_sal.toFixed(2) !== 'NaN' ? tot_sal.toFixed(2) : '',
                                    style: 'tableHeader'
                                },
                            ]);
                        }
                    });
                    doc.content[1].table.headerRows = 1;
                    doc.content[1].table.widths = [90, 440, 75, 80, 80, 80];
                    doc.content[1].table.body = bod;
                    doc.content[1].layout = 'lightHorizontalLines';
                    doc.styles = {
                        header: {
                            fontSize: 32,
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
                                    text: ['Fecha de creación: ', {text: date_now}, ' Hora: ', {text: hour_now}]
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
                                    text: ['ANALITICO AUXILIAR DE CUENTAS ', ' - DETALLE'],
                                    margin: [0, 10]
                                }
                            ],
                            margin: [30, 0]
                        }
                    });
                }
            }
        ],
        /*columns: [
            {"data": "codigo_cuenta_plan"},
            {"data": "nombre_cuenta_plan"},
            {"data": "fecha_asiento_transaccion"},
            {"data": "nombre_asiento_transaccion"},
            {"data": "codigo_asiento_transaccion"},
            {"data": "detalle"},
            {"data": "debe"},
            {"data": "haber"},
            {"data": "encabezadocuentaplan"},
        ],*/
        /*columnDefs: [
            {
                targets: [0],
                class: 'text-center',
                orderable: false,
                // visible: false,
                render: function (data, type, row) {
                    return '<b>' + data + '</b>';
                }
            },
            {
                targets: [1],
                class: 'text-left',
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
                    if (row.nombre_asiento_transaccion === "1") {
                        return 'DIARIO CONTABLE';
                    } else if (row.nombre_asiento_transaccion === "2") {
                        return 'INGRESO A CAJA';
                    } else {
                        return ' ';
                    }
                }
            },
            {
                targets: [4],
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    return '<b>' + data + '</b>';
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
                    /!*console.log('acum')
                    console.log(acum)*!/
                    return parseFloat(acum).toFixed(2);
                    // return data;
                }
            },
        ],*/
        /*columns: [
            {"data": "codigo_cuenta_plan", 'width': '15%'},
            {"data": "nombre_cuenta_plan", 'width': '15%'},
            {"data": "detalle", 'width': '40%'},
            {"data": "fecha_asiento_transaccion", 'width': '8%'},
            {"data": "nombre_asiento_transaccion", 'width': '5%'},
            {"data": "codigo_asiento_transaccion", 'width': '5%'},
            {"data": "debe", 'width': '5%'},
            {"data": "haber", 'width': '5%'},
            {"data": "encabezadocuentaplan", 'width': '5%'},
        ],*/
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
                    /*if (row.nombre_asiento_transaccion === "1") {
                        return 'DIARIO CONTABLE';
                    } else if (row.nombre_asiento_transaccion === "2") {
                        return 'COMPROBANTE DE PAGO';
                    } else if (row.nombre_asiento_transaccion === "3") {
                        return 'INGRESO A CAJA';
                    } else {
                        return 'EGRESO DE CAJA';
                    }*/
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

                    return parseFloat(acum).toFixed(2);
                    // return data;
                }
            },
        ],
        /*rowCallback: function (row, data, index) {
            var tr = $(row).closest('tr');

            const json = tb_mayor_list_range.rows().data().toArray();

            /!*let contador = 0;
            cuenta = data.codigo_cuenta_plan;
            for (let j = index; j <= index; j++) {
                contador = (j - 1)
                if (index > contador) {
                    cantidad_ingreso = parseFloat(data.debe)
                    cantidad_egreso = parseFloat(data.haber)

                    /!*if (cantidad_ingreso > 0 && cuenta === data.codigo_cuenta_plan) {
                        total_stock += cantidad_ingreso;
                        $('td', row).eq(-1).css({'background-color': '#5f9ea0', 'color': 'black'});
                    } else if(cantidad_egreso > 0 && cuenta === data.codigo_cuenta_plan) {
                        total_stock -= cantidad_egreso;
                        $('td', row).eq(-1).css({'background-color': '#f08080', 'color': 'black'});
                    }
                    // console.log('nuevo total ' + total_stock);
                    //$('td', row).eq(5).html('<b>' + total_stock.toFixed(0) + '</b>');
                    // $('td', row).eq(-1).html('<b>' + total_stock.toFixed(2) + '</b>');
                    $('td:eq(-1)', tb_mayor_list.row(tr).node()).html('<b>' + total_stock.toFixed(2) + '</b>');*!/
                }
            }*!/

            for (let i = 0; i < json.length; i++) {
                for (let j = i; j <= index; j++) {
                    if (i === j) {
                        if ((i > 0 && json[i]['codigo_cuenta_plan'] === json[i - 1]["codigo_cuenta_plan"])) {
                            json[i]["saldo"] = (parseFloat(json[i]['debe']) - parseFloat(json[i]['haber'])) + parseFloat(json[i - 1]['saldo']);
                        } else {
                            json[i]["saldo"] = parseFloat(json[i]['debe']) - parseFloat(json[i]['haber'])
                        }
                        $('td:eq(-1)', tb_mayor_list_range.row(tr).node()).html('<b>' + parseFloat(json[i]["saldo"]).toFixed(2) + '</b>');
                    }
                }
            }
        },*/
        /*drawCallback: function (settings) {

            var api = this.api();
            var rows = api.rows({page: 'current'}).nodes();
            var last = null;
            var total = 0, total2 = 0, total3 = 0;
            var filas = api.column(0, {page: 'current'}).data();

            filas.each(function (group, i) {

                /!*console.log('group')
                console.log(group)
                console.log('i')
                console.log(i)*!/

                if (last !== group) {
                    if (last !== null) {
                        $(rows).eq(i - 1).after(
                            `<tr class="total">
                                <td colspan="5" style="width: 55%;"></td>
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
                    $(rows).eq(i).before(
                        '<tr class="group text-left" style="background-color:rgb(255, 255, 255);font-weight:700;">' +
                        '<td colspan="9" style="width: 100%">' + "Cuenta de Mayor: &nbsp;" + group + ' &nbsp;/&nbsp;' + $(rows).eq(i).children()[1].textContent + '</td>' +
                        '</tr>'
                    );
                    last = group;
                }
                total += +$(rows).eq(i).children()[6].textContent;
                total2 += +$(rows).eq(i).children()[7].textContent;
                total3 += +$(rows).eq(i).children()[6].textContent - +$(rows).eq(i).children()[7].textContent;
                if (i === filas.length - 1) {
                    $(rows).eq(i).after(
                        `<tr class="total">
                            <td colspan="5" style="width: 55%;"></td>
                            <td class="text-center" style="width: 10%;font-weight:700;background-color:rgb(255, 255, 255)">Saldo de la Cuenta:</td>
                            <td class="text-center" style="width: 10%;font-weight:700;background-color:rgb(255, 255, 255)">${total.toFixed(2)}</td>   
                            <td class="text-center" style="width: 10%;font-weight:700;background-color:rgb(255, 255, 255)">${total2.toFixed(2)}</td>  
                            <td class="text-center" style="width: 15%;font-weight:700;background-color:rgb(255, 255, 255)">${total3.toFixed(2)}</td>   
                        </tr>`
                    );
                }

            });
        },*/
        /*drawCallback: function (settings) {

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
                        if (dict._aFilterData[0] === group) {
                            resultado = dict._aFilterData[1]
                        }
                    })

                    $(rows).eq(i).before(
                        '<tr class="group text-left" style="background-color:rgb(255, 255, 255);font-weight:700;">' +
                        '<td colspan="6" style="width: 100%">' + "Cuenta de Mayor: &nbsp;" + group + ' &nbsp; / &nbsp; ' + resultado + '</td>' +
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
        },*/
        initComplete: function (settings, json) {

            // var tr = $(this).parents("tr")[0]
            /* var tr = tb_mayor_list.cell($(this).closest('td, li')).index();
             var data = tb_mayor_list.row(tr).data();
             console.log('AAAAAAAAAAAAAAAAAAAAAAAA');
             console.log(data);
             for (let i = 0; i < json.length; i++) {
                 const cuenta = json[i];
                 // console.log("entra for")
                 if (i > 0 && json[i]['codigo_cuenta_plan'] === json[i - 1]["codigo_cuenta_plan"]) {
                     // console.log("entra en if")
                     json[i]["saldo"] = (parseFloat(json[i]['debe']) - parseFloat(json[i]['haber'])) + parseFloat(json[i - 1]['saldo']);
                     saldo_contador = parseFloat(json[i]["saldo"]);
                     console.log('json["saldo"] DE IF')
                     console.log(parseFloat(json[i]["saldo"]), ' - saldo_contador - ', saldo_contador)
                     $('td:eq(-1)', tb_mayor_list.row(tr).node()).html('<b>' + saldo_contador.toFixed(2) + '</b>')
                     // $("td:eq(-1)", tr).text('<b>' + saldo_contador.toFixed(2) + '</b>');
                 } else {
                     json[i]["saldo"] = parseFloat(json[i]['debe']) - parseFloat(json[i]['haber'])
                     saldo_contador = parseFloat(json[i]["saldo"]);
                     console.log('json["saldo"] DE ELSE')
                     console.log(parseFloat(json[i]["saldo"]), ' - saldo_contador - ', saldo_contador)
                     $('td:eq(-1)', tb_mayor_list.row(tr).node()).html('<b>' + saldo_contador.toFixed(2) + '</b>');
                     // $("td:eq(-1)", tr).text('<b>' + saldo_contador.toFixed(2) + '</b>');
                 }
             }*/
        }
    });
}

$(function () {

    $('.select2').select2({
        theme: "bootstrap4",
        language: 'es'
    });

    $('input[name="date_range"]').daterangepicker({
        locale: {
            format: 'YYYY-MM-DD',
            applyLabel: '<i class="fas fa-chart-pie"></i> Aplicar',
            cancelLabel: '<i class="fas fa-times"></i> Cancelar',
        }
    }).on('apply.daterangepicker', function (ev, picker) {
        date_range = picker
        generate_report();
    }).on('cancel.daterangepicker', function (ev, picker) {
        $(this).data('daterangepicker').setStartDate(date_now);
        $(this).data('daterangepicker').setEndDate(date_now);
        $('select[name="rango_desde"]').val('').trigger('change.select2');
        $('select[name="rango_hasta"]').val('').trigger('change.select2');
        date_range = picker;
        // params.list();
        generate_report();
    });

    // params.list();
    generate_report();

    let obterner = () => {
        $.ajax({
            url: window.location.pathname,
            type: 'POST',
            data: {
                'action': 'searchdataplan'
            },
            dataType: 'json',

        }).done(function (data) {

            $.each(data, function (key, value) {
                plan_det.push({'id': value.codigo, 'text': (value.codigo + '   |   ' + value.nombre)});
                contador_ult = value.codigo;
            });

            $('select[name="rango_desde"]').select2({
                theme: 'bootstrap4',
                language: "es",
                data: plan_det
            }).on('select2:select', function (e) {
                var data = e.params.data;
                /*console.log("$('select[name=\"rango_desde\"]').find(':selected').val()")
                console.log($('select[name="rango_desde"]').find(':selected').val())
                desde_rang = $('select[name="rango_desde"]').find(':selected').val();*/
                desde_rang = data.id;
            });

            $('select[name="rango_hasta"]').select2({
                theme: 'bootstrap4',
                language: "es",
                data: plan_det
            }).on('select2:select', function (e) {
                var data = e.params.data;
                /*console.log('HASTA EL SELECT BUSQUEDA')
                console.log('El ID es: ', data.id)
                console.log('El TEXT es: ', data.text)
                Console.log("$('select[name=\"rango_hasta\"]').find(':selected').val()")
                console.log($('select[name="rango_hasta"]').find(':selected').val())
                hasta_rang = $('select[name="rango_hasta"]').find(':selected').val();*/
                hasta_rang = data.id;
            });

        });
    }

    obterner();

    $('.btnRemoveAll').on('click', function () {
        $('input[name="date_range"]').data('daterangepicker').setStartDate(date_now);
        $('input[name="date_range"]').data('daterangepicker').setEndDate(date_now);
        $('select[name="rango_desde"]').val('').trigger('change.select2');
        $('select[name="rango_hasta"]').val('').trigger('change.select2');
        params.list();
    });

});
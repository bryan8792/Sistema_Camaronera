
var tb_siembra_valorizable;
var tabledev;

var siembra_valorizable = {
    list: function () {
        tb_siembra_valorizable = $('#tb_siembra_valorizable').DataTable({
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
            scrollX: true,
            autoWidth: false,
            destroy: true,
            deferRender: true,
            ajax: {
                url: window.location.pathname,
                type: 'POST',
                data: {
                    'action': 'searchdata_val'
                },
                dataSrc: ""
            },
            columns: [
                {"data": "number","width":"7%"},
                {"data": "fecha_registro","width":"10%"},
                {"data": "fecha_compra","width":"10%"},
                {"data": "fecha_transferencia","width":"10%"},
                {"data": "observacion","width":"48%"},
                {"data": "tot_comp","width":"10%"},
                {"data": "id","width":"5%"},
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
                    targets: [1, 2, 3],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return data;
                    }
                },
                {
                    targets: [-3],
                    class: 'text-left',
                    orderable: false,
                    render: function (data, type, row) {
                        return data;
                    }
                },
                {
                    targets: [-2],
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
                    render: function (data, type, row) {
                        var buttons = '<a rel="details" class="btn btn-success btn-xs" style="color: white;"><i class="fas fa-search"></i></a> ';
                        buttons += '&nbsp;';
                        buttons += '<a href="/corrida/reporte_siembra/' + data + '/" target="_blank" class="btn btn-info btn-xs btn-flat"><i class="fas fa-file-pdf"></i></a>';
                        return buttons;
                    }
                },
            ],
            initComplete: function (settings, json) {

            }
        });
    }
}


$(function () {

    siembra_valorizable.list();

    $('#tb_siembra_valorizable tbody').on('click', 'a[rel="details"]', function () {
        var tr = tb_siembra_valorizable.cell($(this).closest('td, li')).index();
        var data = tb_siembra_valorizable.row(tr.row).data();

        $('#demo').html('<table class="table table-sm table-bordered table-striped tb" id="example" width="100%"></table>')
        $('#example').DataTable({
            responsive: true,
            autoWidth: false,
            destroy: true,
            deferRender: true,
            ajax: {
                url: window.location.pathname,
                type: 'POST',
                data: {
                    'action': 'search_details_enc',
                    'id': data.id
                },
                dataSrc: ""
            },
            order: false,
            ordering: false,
            dom: 'rt',
            columns: [
                {"title":"Productos Escogidos","data": "prod_cantidad","width":"50%"},
                {"title":"Resultado: Proceso de Movimientos (Ajustes entre piscinas)","data": "resul_oper","width":"50%"},
            ],
            columnDefs: [
                {
                    targets: [0],
                    class: 'text-center',
                    render: function (data, type, row) {
                        return data;
                    }
                },
                {
                    targets: [-1],
                    class: 'text-center',
                    render: function (data, type, row) {
                        /*console.log('row.resul_oper.items()')
                        console.log(row.resul_oper)
                        var func = row.resul_oper
                        tabledev = '<table class="table">';
                        foot_dev = '<tr>';
                        for (var empresa in func) {
                            for (var producto in func[empresa]) {
                                tabledev += '<tr>'
                                tabledev += '<td style="text-align: center">' + func[empresa] + '</td>'
                                tabledev += '<td style="text-align: center">' + func[producto] + '</td>'
                                tabledev += '<td style="text-align: center">' + func[empresa][producto] + '</td>'
                                tabledev += '</tr>';
                            }
                        }
                        return tabledev += '</table>';*/

                        // console.log('PROCESANDO AL EACH')
                        // $.each([row.resul_oper], function (el, index) {
                        //     console.log('index')
                        //     console.log(index)
                        // });

                        /*[row.resul_oper].forEach(function (valor, indice, array) {
                            console.log('valor')
                            console.log(valor)
                            console.log('array')
                            console.log(array)
                            for (var empresa in array) {
                                console.log('empresa')
                                console.log(array[empresa])
                            }
                        })*/

                        // Object.keys([row.resul_oper]).forEach(function (key) {
                        //     console.log('key, [row.resul_oper][key]')
                        //     console.log(key, [row.resul_oper][key])
                        // })

                        return row.resul_oper;
                    }
                },
            ],
        });

        $('#tblSearchPiscinas').DataTable({
            language: {
                "oPaginate": {
                    "sFirst": "Primero",
                    "sLast": "Último",
                    "sNext": "Siguiente",
                    "sPrevious": "Anterior"
                },
                "zeroRecords": "Ningun dato disponible en esta tabla",
                "sInfo": "Registros del _START_ al _END_ de un total de _TOTAL_ registros",
                "infoEmpty": "Tabla vacia por favor inserte datos",
                "lengthMenu": "Listando _MENU_ registros",
                "sSearch": "Buscar:",
                "infoFiltered": "(filtrado de _MAX_ registros totales)"
            },
            responsive: true,
            autoWidth: false,
            destroy: true,
            deferRender: true,
            ajax: {
                url: window.location.pathname,
                type: 'POST',
                data: {
                    'action': 'search_details_cuerp',
                    'id': data.id
                },
                dataSrc: ""
            },
            order: false,
            ordering: false,
            info: false,
            dom: 'rtip',
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
            ],
            columns: [
                {"data": "piscina","width":"10%"},
                {"data": "dias","width":"8%"},
                {"data": "siembra","width":"10%"},
                {"data": "costo_larva","width":"10%"},
                {"data": "dia_por_hect","width":"10%"},
                {"data": "prod_cantidad_proceso","width":"44%"},
                {"data": "total","width":"8%"},
            ],
            columnDefs: [
                {
                    targets: [0],
                    class: 'text-center',
                    render: function (data, type, row) {
                        return '<b>' + 'PISCINA '+ data + '</b>';
                    }
                },
                {
                    targets: [1,2,3,4],
                    class: 'text-center',
                    render: function (data, type, row) {
                        return '<b>' + data + '</b>';
                    }
                },
                {
                    targets: [-3],
                    class: 'text-center',
                    render: function (data, type, row) {
                        return data;
                    }
                },
                {
                    targets: [-2],
                    class: 'text-center',
                    render: function (data, type, row) {
                        /*console.log(data)
                        tabledev = '<table class="table">';
                        for (var empresa in data) {
                            // for (var producto in data[empresa]) {
                                tabledev += '<tr>'
                                tabledev += '<td style="text-align: center">' + data[empresa] + '</td>'
                                // tabledev += '<td style="text-align: center">' + data[producto] + '</td>'
                                //tabledev += '<td style="text-align: center">' + parseFloat(data[empresa][producto]).toFixed(2) + '</td>'
                                tabledev += '</tr>';
                            // }
                        }*/
                        return data;
                    },
                },
                {
                    targets: [-1],
                    class: 'text-center',
                    render: function (data, type, row) {
                        return parseFloat(data).toFixed(2);
                    }
                },
            ],
            footerCallback: function (row, data, index) {

                var total_siembra = this.api()
                    .column(2)
                    //.column(4, {page: 'current'})//para sumar solo la pagina actual
                    .data()
                    .reduce(function (a, b) {
                        return parseFloat(a) + parseFloat(b);
                    }, 0);
                $(this.api().column(2).footer()).html('' + parseFloat(total_siembra).toFixed(3));

                var total_costo_larva = this.api()
                    .column(3)
                    //.column(3, {page: 'current'})//para sumar solo la pagina actual
                    .data()
                    .reduce(function (a, b) {
                        return parseFloat(a) + parseFloat(b);
                    }, 0);
                $(this.api().column(3).footer()).html('' + parseFloat(total_costo_larva).toFixed(2));

                var total_dia_hect = this.api()
                    .column(4)
                    //.column(3, {page: 'current'})//para sumar solo la pagina actual
                    .data()
                    .reduce(function (a, b) {
                        return parseFloat(a) + parseFloat(b);
                    }, 0);
                $(this.api().column(4).footer()).html('' + parseFloat(total_dia_hect).toFixed(2));

                var total_general = this.api()
                    .column(6)
                    //.column(3, {page: 'current'})//para sumar solo la pagina actual
                    .data()
                    .reduce(function (a, b) {
                        return parseFloat(a) + parseFloat(b);
                    }, 0);
                $(this.api().column(6).footer()).html('' + parseFloat(total_general).toFixed(2));

            },
            initComplete: function (settings, json) {

            }
            });

        $('#myModalSearchPiscinas').modal('show');
    });

});
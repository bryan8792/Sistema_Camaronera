$(function () {
    $('#tb_transaccion_plan').DataTable({
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
        scrollX: true,
        autoWidth: false,
        destroy: true,
        deferRender: true,
        ajax: {
            url: window.location.pathname,
            type: 'POST',
            data: {
                'action': 'searchdata'
            },
            dataSrc: ""
        },
        columns: [
            {"data": "codigo"},
            {"data": "tip_cuenta"},
            {"data": "fecha"},
            {"data": "comprobante"},
            {"data": "descripcion"},
            {"data": "direccion"},
            {"data": "id"},
        ],
        columnDefs: [
            {
                targets: [0],
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                     return '<b>'+ data +'</b>';
                }
            },
            {
                targets: [1],
                class: 'text-left',
                orderable: false,
                render: function (data, type, row) {
                    console.log('data')
                    console.log(data)
                    console.log('row')
                    console.log(row)
                    if (row.tip_cuenta == 1) {
                        return 'DIARIO CONTABLE';
                    } else {
                        return 'INGRESO A CAJA';
                    }
                }
            },
            {
                targets: [-5, -4],
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    return data;
                }
            },
            {
                targets: [-3],
                //class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    return '<b>'+ data +'</b>';
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
                targets: [-1],
                class: 'text-center',
                render: function (data, type, row) {
                    console.log('data')
                    console.log(data)
                    console.log('row')
                    console.log(row)
                    console.log('type')
                    console.log(type)
                    var buttons = '';
                    buttons += '<a href="/planCuentas/transaccion/editar/'+ row.id + '/" class="btn btn-warning btn-xs btn-flat"><i class="fas fa-edit"></i></a> ';
                    /*buttons += '&nbsp';
                    buttons += '<a href="#" target="_blank" class="btn btn-info btn-xs"><i class="fas fa-file-pdf"></i></a>';
                    buttons += '&nbsp';
                    buttons += '<a href="#" class="btn btn-danger btn-xs"><i class="fas fa-trash"></i></a>';*/
                    return buttons;
                }
            },
        ],
        initComplete: function (settings, json) {

        }
    });
});
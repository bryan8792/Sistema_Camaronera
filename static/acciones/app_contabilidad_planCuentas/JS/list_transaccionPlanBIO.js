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
                'action': 'searchdata_bio'
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
                    return '<b>' + data + '</b>';
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
                    return '<b>' + data + '</b>';
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
                    var buttons = '<div class="dropdown">';
                    buttons += '<button class="btn btn-info btn-sm dropdown-toggle" type="button" data-toggle="dropdown" aria-expanded="false">';
                    buttons += '<i class="fas fa-list"></i> Opciones</button>';
                    buttons += '<div class="dropdown-menu dropdown-menu-right">';
                    buttons += '<a class="dropdown-item" href="/planCuentas/fact_gasto/editar/' + row.id + '/"><i class="fas fa-edit"></i> Actualizar</a>';
                    buttons += '<a class="dropdown-item" href="/planCuentas/reporte/pdf/' + row.id + '/" target="_blank"><i class="fas fa-file-pdf"></i> Imprimir Diario</a>';
                    // Botones ATS (PDF y XML si existen)
                    if (row.detATS && row.detATS.length > 0) {
                        let ats = row.detATS[0];
                        if (ats.pdf_authorized) {
                            buttons += '<a class="dropdown-item" href="' + ats.pdf_authorized + '" target="_blank" download>';
                            buttons += '<i class="fas fa-file-pdf"></i> Imprimir ATS (PDF)</a>';
                        }
                        if (ats.xml_authorized) {
                            buttons += '<a class="dropdown-item" href="' + ats.xml_authorized + '" target="_blank" download>';
                            buttons += '<i class="fas fa-file-code"></i> Descargar ATS (XML)</a>';
                        }
                    }
                    buttons += '</div></div>';
                    return buttons;

                    /*var buttons = '';
                    buttons += '<a href="/planCuentas/fact_gasto/editar/'+ row.id + '/" class="btn btn-warning btn-xs btn-flat"><i class="fas fa-edit"></i></a> ';
                    buttons += '&nbsp';
                    buttons += '<a href="/planCuentas/reporte/pdf/' + row.id + '/" target="_blank" class="btn btn-info btn-xs"><i class="fas fa-file-pdf"></i></a>';
                    return buttons;*/
                }
            },
        ],
        initComplete: function (settings, json) {

        }
    });
});
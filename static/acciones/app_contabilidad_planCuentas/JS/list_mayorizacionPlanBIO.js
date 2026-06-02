var date_range = null;
var tb_mayor_list;

function mayor_list() {

    tb_mayor_list = $('#tb_mayorizacion_plan').DataTable({

        language: {
            "oPaginate": {
                "sFirst": "Primero",
                "sLast": "Último",
                "sNext": "Siguiente",
                "sPrevious": "Anterior"
            },
            "zeroRecords": "Ningún dato disponible en esta tabla",
            "sInfo": "Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros",
            "infoEmpty": "Tabla vacía",
            "lengthMenu": "Mostrar _MENU_ registros",
            "sSearch": "Buscar:",
            "infoFiltered": "(filtrado de _MAX_ registros totales)",
            "processing": "Procesando..."
        },

        // ======================================================
        // CONFIGURACION IMPORTANTE
        // ======================================================

        processing: true,
        serverSide: true,
        paging: true,
        pageLength: 100,

        responsive: true,
        autoWidth: false,
        destroy: true,
        deferRender: true,

        scrollY: "700px",
        scrollX: true,

        dom: 'Bfrtip',

        // ======================================================
        // AJAX
        // ======================================================

        ajax: {
            url: window.location.pathname,
            type: 'POST',

            data: function (d) {

                d.action = 'searchdata';
                d.empresa = 'BIO';

                return d;
            },

            dataSrc: 'data'
        },

        // ======================================================
        // BOTONES
        // ======================================================

        buttons: [

            {
                extend: 'excelHtml5',
                text: '<i class="fas fa-file-excel"></i>',
                titleAttr: 'Exportar Excel',
                className: 'btn btn-success'
            },

            {
                extend: 'print',
                text: '<i class="fa fa-print"></i>',
                titleAttr: 'Imprimir',
                className: 'btn btn-info'
            },

            {
                extend: 'pdfHtml5',
                text: '<i class="fas fa-file-pdf"></i>',
                titleAttr: 'Exportar PDF',
                className: 'btn btn-danger',

                download: 'open',
                orientation: 'landscape',
                pageSize: 'LEGAL',

                exportOptions: {
                    columns: ':visible'
                }
            }
        ],

        // ======================================================
        // COLUMNAS
        // ======================================================

        columns: [

            {"data": "codigo"},
            {"data": "nombre"},
            {"data": "descripcion"},
            {"data": "fecha"},
            {"data": "transaccion"},
            {"data": "asiento"},
            {"data": "debe"},
            {"data": "haber"},
            {"data": "saldo"},
        ],

        // ======================================================
        // DEFINICIONES DE COLUMNAS
        // ======================================================

        columnDefs: [

            // CODIGO
            {
                targets: [0],
                className: 'text-center',
                render: function (data) {
                    return '<b>' + data + '</b>';
                }
            },

            // NOMBRE
            {
                targets: [1],
                className: 'text-left',
            },

            // DESCRIPCION
            {
                targets: [2],
                className: 'text-left',
            },

            // FECHA
            {
                targets: [3],
                className: 'text-center',
                render: function (data) {
                    return '<b>' + data + '</b>';
                }
            },

            // TRANSACCION
            {
                targets: [4],
                className: 'text-center',
                render: function (data) {

                    if (data === "1") {
                        return 'DIARIO CONTABLE';
                    }
                    else if (data === "2") {
                        return 'COMPROBANTE DE PAGO';
                    }
                    else if (data === "3") {
                        return 'INGRESO A CAJA';
                    }

                    return 'EGRESO DE CAJA';
                }
            },

            // ASIENTO
            {
                targets: [5],
                className: 'text-center',
            },

            // DEBE
            {
                targets: [6],
                className: 'text-right',
                render: function (data) {
                    return parseFloat(data).toFixed(2);
                }
            },

            // HABER
            {
                targets: [7],
                className: 'text-right',
                render: function (data) {
                    return parseFloat(data).toFixed(2);
                }
            },

            // SALDO
            {
                targets: [8],
                className: 'text-right',

                render: function (data) {
                    return '<b>' + parseFloat(data).toFixed(2) + '</b>';
                }
            }
        ],

        // ======================================================
        // CUANDO TERMINA DE CARGAR
        // ======================================================

        initComplete: function () {

            console.log('DataTable cargado correctamente');
        }
    });
}

// ==========================================================
// INICIAR
// ==========================================================

$(function () {

    mayor_list();

});
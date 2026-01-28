var tblProducts_psm;
var tblProducts_bio;

var kardex_psm = {
    items: [],
    clear: function() {
        this.items = [];
    },
    setProducts: function(products) {
        this.items = products;
        this.list();
    },
    list: function() {
        if ($.fn.DataTable.isDataTable('#tblProducts_psm')) {
            $('#tblProducts_psm').DataTable().destroy();
        }

        tblProducts_psm = $('#tblProducts_psm').DataTable({
            language: {
                "lengthMenu": "Mostrar _MENU_ registros",
                "zeroRecords": "No se encontraron resultados para PSM",
                "info": "Mostrando _START_ al _END_ de _TOTAL_ registros",
                "infoEmpty": "Sin registros",
                "infoFiltered": "(filtrado de _MAX_ registros)",
                "sSearch": "Buscar:",
                "oPaginate": {
                    "sFirst": "Primero",
                    "sLast": "Ultimo",
                    "sNext": "Siguiente",
                    "sPrevious": "Anterior"
                },
            },
            autoWidth: false,
            dom: 'Bfrtip',
            paging: true,
            pageLength: 25,
            scrollY: "400px",
            scrollX: true,
            destroy: true,
            data: this.items,
            columns: [
                {"data": "fecha_ingreso"},
                {"data": "producto_empresa.nombre_prod.nombre"},
                {"data": "cantidad_ingreso"},
                {"data": "cantidad_egreso"},
                {"data": "id"},
            ],
            columnDefs: [
                {
                    targets: [0, 1, 2, 3],
                    className: 'text-center',
                    orderable: false
                },
                {
                    targets: [4],
                    className: 'text-center',
                    orderable: false,
                    render: function(data, type, row) {
                        var ingreso = parseFloat(row.cantidad_ingreso) || 0;
                        var egreso = parseFloat(row.cantidad_egreso) || 0;
                        var saldo = ingreso - egreso;

                        if (row.tipo === 'INGRESO') {
                            return '<span style="background-color:#5f9ea0;color:white;padding:2px 8px;border-radius:3px;"><b>' + saldo.toFixed(0) + '</b></span>';
                        } else {
                            return '<span style="background-color:#f08080;color:white;padding:2px 8px;border-radius:3px;"><b>' + saldo.toFixed(0) + '</b></span>';
                        }
                    }
                }
            ],
            buttons: [
                {
                    extend: 'csvHtml5',
                    text: '<i class="fas fa-file-csv"></i> CSV',
                    titleAttr: 'CSV',
                    className: 'btn btn-success btn-sm'
                },
                {
                    extend: 'pdfHtml5',
                    text: '<i class="fas fa-file-pdf"></i> PDF',
                    titleAttr: 'PDF',
                    className: 'btn btn-danger btn-sm',
                    orientation: 'landscape'
                }
            ]
        });
    }
};

var kardex_bio = {
    items: [],
    clear: function() {
        this.items = [];
    },
    setProducts: function(products) {
        this.items = products;
        this.list();
    },
    list: function() {
        if ($.fn.DataTable.isDataTable('#tblProducts_bio')) {
            $('#tblProducts_bio').DataTable().destroy();
        }

        tblProducts_bio = $('#tblProducts_bio').DataTable({
            language: {
                "lengthMenu": "Mostrar _MENU_ registros",
                "zeroRecords": "No se encontraron resultados para BIO",
                "info": "Mostrando _START_ al _END_ de _TOTAL_ registros",
                "infoEmpty": "Sin registros",
                "infoFiltered": "(filtrado de _MAX_ registros)",
                "sSearch": "Buscar:",
                "oPaginate": {
                    "sFirst": "Primero",
                    "sLast": "Ultimo",
                    "sNext": "Siguiente",
                    "sPrevious": "Anterior"
                },
            },
            autoWidth: false,
            dom: 'Bfrtip',
            paging: true,
            pageLength: 25,
            scrollY: "400px",
            scrollX: true,
            destroy: true,
            data: this.items,
            columns: [
                {"data": "fecha_ingreso"},
                {"data": "producto_empresa.nombre_prod.nombre"},
                {"data": "cantidad_ingreso"},
                {"data": "cantidad_egreso"},
                {"data": "id"},
            ],
            columnDefs: [
                {
                    targets: [0, 1, 2, 3],
                    className: 'text-center',
                    orderable: false
                },
                {
                    targets: [4],
                    className: 'text-center',
                    orderable: false,
                    render: function(data, type, row) {
                        var ingreso = parseFloat(row.cantidad_ingreso) || 0;
                        var egreso = parseFloat(row.cantidad_egreso) || 0;
                        var saldo = ingreso - egreso;

                        if (row.tipo === 'INGRESO') {
                            return '<span style="background-color:#5f9ea0;color:white;padding:2px 8px;border-radius:3px;"><b>' + saldo.toFixed(0) + '</b></span>';
                        } else {
                            return '<span style="background-color:#f08080;color:white;padding:2px 8px;border-radius:3px;"><b>' + saldo.toFixed(0) + '</b></span>';
                        }
                    }
                }
            ],
            buttons: [
                {
                    extend: 'csvHtml5',
                    text: '<i class="fas fa-file-csv"></i> CSV',
                    titleAttr: 'CSV',
                    className: 'btn btn-success btn-sm'
                },
                {
                    extend: 'pdfHtml5',
                    text: '<i class="fas fa-file-pdf"></i> PDF',
                    titleAttr: 'PDF',
                    className: 'btn btn-danger btn-sm',
                    orientation: 'landscape'
                }
            ]
        });
    }
};

function buscarProducto(nombreProducto) {
    // Buscar en PSM
    $.ajax({
        url: window.location.pathname,
        type: 'POST',
        data: {
            'action': 'search_producto_psm',
            'nombre_producto': nombreProducto
        },
        dataType: 'json'
    }).done(function(data) {
        if (data && Array.isArray(data) && data.length > 0) {
            kardex_psm.setProducts(data);
        } else {
            kardex_psm.clear();
            kardex_psm.list();
        }
    }).fail(function(jqXHR, textStatus, errorThrown) {
        console.error('Error al buscar PSM:', textStatus);
        kardex_psm.clear();
        kardex_psm.list();
    });

    // Buscar en BIO
    $.ajax({
        url: window.location.pathname,
        type: 'POST',
        data: {
            'action': 'search_producto_bio',
            'nombre_producto': nombreProducto
        },
        dataType: 'json'
    }).done(function(data) {
        if (data && Array.isArray(data) && data.length > 0) {
            kardex_bio.setProducts(data);
        } else {
            kardex_bio.clear();
            kardex_bio.list();
        }
    }).fail(function(jqXHR, textStatus, errorThrown) {
        console.error('Error al buscar BIO:', textStatus);
        kardex_bio.clear();
        kardex_bio.list();
    });
}

$(function() {
    // Inicializar tablas vacias
    kardex_psm.list();
    kardex_bio.list();

    // Configurar autocomplete con jQuery UI
    $('input[name="search"]').autocomplete({
        source: function(request, response) {
            $.ajax({
                url: window.location.pathname,
                type: 'POST',
                data: {
                    'action': 'search_autocomplete',
                    'term': request.term
                },
                dataType: 'json'
            }).done(function(data) {
                if (data && Array.isArray(data)) {
                    response($.map(data, function(item) {
                        return {
                            label: item.text,
                            value: item.value
                        };
                    }));
                } else {
                    response([]);
                }
            }).fail(function() {
                response([]);
            });
        },
        delay: 400,
        minLength: 2,
        select: function(event, ui) {
            event.preventDefault();
            $(this).val(ui.item.value);
            buscarProducto(ui.item.value);
        }
    });

    // Buscar al presionar Enter
    $('input[name="search"]').on('keypress', function(e) {
        if (e.which === 13) {
            e.preventDefault();
            var term = $(this).val().trim();
            if (term.length >= 2) {
                buscarProducto(term);
            }
        }
    });
});
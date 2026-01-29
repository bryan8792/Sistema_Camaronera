var tblProducts_psm = null;
var tblProducts_bio = null;
var productoSeleccionado = '';
var stockPSM = 0;
var stockBIO = 0;

// Formatear numero con 2 decimales y separador de miles
function formatNumber(valor) {
    if (valor === null || valor === undefined || isNaN(valor)) {
        return '0,00';
    }
    var num = parseFloat(valor);
    return num.toLocaleString('es-EC', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

// Inicializar DataTable PSM
function initTablePSM(data, totales) {
    if (tblProducts_psm !== null) {
        tblProducts_psm.destroy();
        $('#tblProducts_psm tbody').empty();
    }

    tblProducts_psm = $('#tblProducts_psm').DataTable({
        language: {
            "lengthMenu": "Mostrar _MENU_",
            "zeroRecords": "Sin registros",
            "info": "Pag _PAGE_ de _PAGES_",
            "infoEmpty": "Sin registros",
            "infoFiltered": "",
            "sSearch": "Buscar:",
            "oPaginate": {
                "sFirst": "<<",
                "sLast": ">>",
                "sNext": "Siguiente",
                "sPrevious": "Anterior"
            }
        },
        data: data,
        paging: true,
        pageLength: 15,
        lengthChange: false,
        ordering: false,
        autoWidth: false,
        scrollY: "350px",
        scrollCollapse: true,
        columns: [
            {data: "fecha_ingreso", className: "text-left"},
            {data: "proveedor", className: "text-left"},
            {
                data: "cantidad_ingreso",
                className: "col-ingreso text-right",
                render: function(data) {
                    return data > 0 ? formatNumber(data) : '';
                }
            },
            {
                data: "cantidad_egreso",
                className: "col-egreso text-right",
                render: function(data) {
                    return data > 0 ? formatNumber(data) : '';
                }
            },
            {
                data: "saldo",
                className: "col-saldo text-right",
                render: function(data) {
                    return formatNumber(data);
                }
            }
        ],
        drawCallback: function() {
            // Actualizar totales en el footer despues de cada redibujado
            if (totales) {
                $('#total_ing_psm').text(formatNumber(totales.total_ingreso));
                $('#total_eg_psm').text(formatNumber(totales.total_egreso));
                $('#saldo_final_psm').text(formatNumber(totales.saldo_final));
            }
        }
    });

    // Actualizar totales inmediatamente
    if (totales) {
        $('#total_ing_psm').text(formatNumber(totales.total_ingreso));
        $('#total_eg_psm').text(formatNumber(totales.total_egreso));
        $('#saldo_final_psm').text(formatNumber(totales.saldo_final));
    }
}

// Inicializar DataTable BIO
function initTableBIO(data, totales) {
    if (tblProducts_bio !== null) {
        tblProducts_bio.destroy();
        $('#tblProducts_bio tbody').empty();
    }

    tblProducts_bio = $('#tblProducts_bio').DataTable({
        language: {
            "lengthMenu": "Mostrar _MENU_",
            "zeroRecords": "Sin registros",
            "info": "Pag _PAGE_ de _PAGES_",
            "infoEmpty": "Sin registros",
            "infoFiltered": "",
            "sSearch": "Buscar:",
            "oPaginate": {
                "sFirst": "<<",
                "sLast": ">>",
                "sNext": "Siguiente",
                "sPrevious": "Anterior"
            }
        },
        data: data,
        paging: true,
        pageLength: 15,
        lengthChange: false,
        ordering: false,
        autoWidth: false,
        scrollY: "350px",
        scrollCollapse: true,
        columns: [
            {data: "fecha_ingreso", className: "text-left"},
            {data: "proveedor", className: "text-left"},
            {
                data: "cantidad_ingreso",
                className: "col-ingreso text-right",
                render: function(data) {
                    return data > 0 ? formatNumber(data) : '';
                }
            },
            {
                data: "cantidad_egreso",
                className: "col-egreso text-right",
                render: function(data) {
                    return data > 0 ? formatNumber(data) : '';
                }
            },
            {
                data: "saldo",
                className: "col-saldo text-right",
                render: function(data) {
                    return formatNumber(data);
                }
            }
        ],
        drawCallback: function() {
            // Actualizar totales en el footer despues de cada redibujado
            if (totales) {
                $('#total_ing_bio').text(formatNumber(totales.total_ingreso));
                $('#total_eg_bio').text(formatNumber(totales.total_egreso));
                $('#saldo_final_bio').text(formatNumber(totales.saldo_final));
            }
        }
    });

    // Actualizar totales inmediatamente
    if (totales) {
        $('#total_ing_bio').text(formatNumber(totales.total_ingreso));
        $('#total_eg_bio').text(formatNumber(totales.total_egreso));
        $('#saldo_final_bio').text(formatNumber(totales.saldo_final));
    }
}

// Buscar producto en PSM
function buscarProductoPSM(nombreProducto) {
    $.ajax({
        url: window.location.pathname,
        type: 'POST',
        data: {
            'action': 'search_producto_psm',
            'nombre_producto': nombreProducto
        },
        dataType: 'json'
    }).done(function(response) {
        if (response.error) {
            console.log('[v0] Error PSM:', response.error);
            initTablePSM([], null);
            return;
        }

        var data = response.data || [];
        stockPSM = response.stock_actual || 0;

        // Actualizar Stock en header
        $('#stock_psm').text(formatNumber(stockPSM));

        // Mostrar nombre del producto
        if (data.length > 0) {
            $('#producto_info_psm').show();
            $('#producto_nombre_psm').text(nombreProducto);
        } else {
            $('#producto_info_psm').hide();
        }

        // Crear objeto de totales
        var totales = {
            total_ingreso: response.total_ingreso || 0,
            total_egreso: response.total_egreso || 0,
            saldo_final: response.saldo_final || 0
        };

        // Inicializar tabla con datos y totales
        initTablePSM(data, totales);
        actualizarSaldoBodega();

    }).fail(function(jqXHR, textStatus, errorThrown) {
        console.log('[v0] Error al buscar PSM:', textStatus);
        initTablePSM([], null);
    });
}

// Buscar producto en BIO
function buscarProductoBIO(nombreProducto) {
    $.ajax({
        url: window.location.pathname,
        type: 'POST',
        data: {
            'action': 'search_producto_bio',
            'nombre_producto': nombreProducto
        },
        dataType: 'json'
    }).done(function(response) {
        if (response.error) {
            console.log('[v0] Error BIO:', response.error);
            initTableBIO([], null);
            return;
        }

        var data = response.data || [];
        stockBIO = response.stock_actual || 0;

        // Actualizar Stock en header
        $('#stock_bio').text(formatNumber(stockBIO));

        // Mostrar nombre del producto
        if (data.length > 0) {
            $('#producto_info_bio').show();
            $('#producto_nombre_bio').text(nombreProducto);
        } else {
            $('#producto_info_bio').hide();
        }

        // Crear objeto de totales
        var totales = {
            total_ingreso: response.total_ingreso || 0,
            total_egreso: response.total_egreso || 0,
            saldo_final: response.saldo_final || 0
        };

        // Inicializar tabla con datos y totales
        initTableBIO(data, totales);
        actualizarSaldoBodega();

    }).fail(function(jqXHR, textStatus, errorThrown) {
        console.log('[v0] Error al buscar BIO:', textStatus);
        initTableBIO([], null);
    });
}

// Actualizar saldo bodega total
function actualizarSaldoBodega() {
    var saldoTotal = stockPSM + stockBIO;
    $('#saldo_bodega_total').text(formatNumber(saldoTotal));
}

// Buscar producto en ambas empresas
function buscarProducto(nombreProducto) {
    if (!nombreProducto || nombreProducto.trim().length < 2) {
        return;
    }

    productoSeleccionado = nombreProducto;
    $('#producto_seleccionado').show();
    $('#nombre_producto_seleccionado').text(nombreProducto);

    // Buscar en ambas empresas simultaneamente
    buscarProductoPSM(nombreProducto);
    buscarProductoBIO(nombreProducto);
}

// Limpiar todo
function limpiarBusqueda() {
    $('#search').val('');
    productoSeleccionado = '';
    stockPSM = 0;
    stockBIO = 0;

    $('#producto_seleccionado').hide();
    $('#producto_info_psm').hide();
    $('#producto_info_bio').hide();

    $('#stock_psm').text('0,00');
    $('#stock_bio').text('0,00');
    $('#saldo_bodega_total').text('0,00');

    $('#total_ing_psm').text('0,00');
    $('#total_eg_psm').text('0,00');
    $('#saldo_final_psm').text('0,00');

    $('#total_ing_bio').text('0,00');
    $('#total_eg_bio').text('0,00');
    $('#saldo_final_bio').text('0,00');

    initTablePSM([], null);
    initTableBIO([], null);
}

$(function() {
    // Inicializar tablas vacias
    initTablePSM([], null);
    initTableBIO([], null);

    // Configurar autocomplete
    $('#search').autocomplete({
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
        delay: 300,
        minLength: 2,
        select: function(event, ui) {
            event.preventDefault();
            $(this).val(ui.item.value);
            buscarProducto(ui.item.value);
        }
    });

    // Buscar al presionar Enter
    $('#search').on('keypress', function(e) {
        if (e.which === 13) {
            e.preventDefault();
            var term = $(this).val().trim();
            if (term.length >= 2) {
                buscarProducto(term);
            }
        }
    });

    // Boton limpiar
    $('#btn_limpiar').on('click', function() {
        limpiarBusqueda();
    });
});
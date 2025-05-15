var tblProducts;
var tblSearchProducts;
var balanced = [];
var supplies = [];
var vents = {
    items: {
        mes_dieta: '',
        fecha: '',
        piscinas: '',
        balanceado: '',
        cantidad: 0,
        insumo1: 0,
        insumo2: 0,
        insumo3: 0,
        insumo4: 0,
        gramaje1: 0,
        gramaje2: 0,
        gramaje3: 0,
        gramaje4: 0,
        products: []
    },
    getItems: function () {
        $.ajax({
            url: window.location.pathname,
            type: 'POST',
            data: {
                'action': 'search_balanceado'
            },
            dataType: 'json',
        }).done(function (data) {
            if (!data.hasOwnProperty('error')) {
                console.log('data');
                console.log(data);
                $.each(data, function (key, value) {
                    console.log('value');
                    console.log(value);
                    console.log('value.categoria');
                    console.log(value.categoria);
                    if (value.categoria && value.categoria.id === 2) {
                        balanced.push({'id': value.id, 'text': value.nombre});
                    } else {
                        if (value.gramaje != null) {
                            supplies.push({'id': value.id, 'text': value.nombre});
                        }
                    }
                });
            }
        }).fail(function (jqXHR, textStatus, errorThrown) {
            alert(textStatus + ': ' + errorThrown);
        }).always(function (data) {

        });
    },
    get_ids: function () {
        var ids = [];
        $.each(this.items.products, function (key, value) {
            ids.push(value.id);
        });
        return ids;
    },
    calculate_dosis: function () {
        $.each(this.items.products, function (pos, dict) {
            console.log('este es pos');
            console.log(pos);
            console.log('este es dict cantidad');
            console.log(dict);
            dict.pos = pos;
            console.log('este es dict.pos')
            console.log(dict.pos)
        });

    },
    calculos: function (libras, gramaje) {
        calculo = parseInt(libras) * eval(gramaje)
        return calculo
    },
    add: function (item) {
        this.items.products.push(item);
        this.list();
    },
    list: function () {
        //this.calculate_dosis();
        tblProducts = $('#tblProducts').DataTable({
            dom: 'Bfrtip',
            bPaginate: false,
            bFilter: false,
            bInfo: false,
            //language: {"url": "//cdn.datatables.net/plug-ins/1.11.5/i18n/es-ES.json"},
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
            autoWidth: false,
            scrollY: "700px",
            scrollX: true,
            destroy: true,
            data: this.items.products,
            columns: [
                {"data": "id", "width": "1%"},
                {"data": "numero", "width": "7%"},
                {"data": "id", "width": "15%"},
                {"data": "id", "width": "6%"},
                {"data": "id", "width": "13%"},
                {"data": "id", "width": "6%"},
                {"data": "id", "width": "10%"},
                {"data": "id"},
                {"data": "id", "width": "10%"},
                {"data": "id"},
                {"data": "id", "width": "10%"},
                {"data": "id"},
            ],
            columnDefs: [
                {
                    targets: [0],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '<a rel="remove" class="btn btn-danger btn-xs" style="color: white;"><i class="fas fa-times"><br/>' + row.id + '</i></a>';
                        //return data;
                    }
                },
                {
                    targets: [1],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return data;
                    }
                },
                {
                    targets: [2],
                    class: 'text-left',
                    orderable: false,
                    render: function (data, type, row) {
                        return `<select class="form-control select2" name="balanceado">
                                    <option value="">------</option>
                                </select>`;
                    }
                },
                {
                    targets: [3],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '<input type="text" name="cantidad" class="form-control text-center" autocomplete="off" value="' + parseFloat(row.cantidad > 0 ? row.cantidad : 0).toFixed(0) + '">';
                    }
                },
                {
                    targets: [-8],
                    class: 'text-left',
                    orderable: false,
                    render: function (data, type, row) {
                        return `<select class="form-control select2" name="insumo1">
                                    <option value="">------</option>
                                </select>`;
                    }
                },
                {
                    targets: [-7],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '<b>' + parseFloat(row.gramaje1 > 0 ? row.gramaje1 : 0).toFixed(0) + '</b>';
                    }
                },
                {
                    targets: [-6],
                    class: 'text-left',
                    orderable: false,
                    render: function (data, type, row) {
                        return `<select class="form-control" name="insumo2">
                                    <option value="">------</option>
                                </select>`;
                    }
                },
                {
                    targets: [-5],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '<b>' + parseFloat(row.gramaje2 > 0 ? row.gramaje2 : 0).toFixed(0) + '</b>';
                    }
                },
                {
                    targets: [-4],
                    class: 'text-left',
                    orderable: false,
                    render: function (data, type, row) {
                        return `<select class="form-control" name="insumo3">
                                    <option value="">------</option>
                                </select>`;
                    }
                },
                {
                    targets: [-3],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '<b>' + parseFloat(row.gramaje3 > 0 ? row.gramaje3 : 0).toFixed(0) + '</b>';
                    }
                },
                {
                    targets: [-2],
                    class: 'text-left',
                    orderable: false,
                    render: function (data, type, row) {
                        return `<select class="form-control" name="insumo4">
                                    <option value="">------</option>
                                </select>`;
                    }
                },
                {
                    targets: [-1],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '<b>' + parseFloat(row.gramaje4 > 0 ? row.gramaje4 : 0).toFixed(0) + '</b>';
                    }
                }
            ],
            rowCallback: function (row, data, index) {
                var tr = $(row).closest('tr');
                console.log('resultado de balanced');
                console.log(balanced);
                console.log('resultado de supplies');
                console.log(supplies);
                //console.log(data);
                tr.find('select[name="balanceado"]').select2({
                    theme: 'bootstrap4',
                    language: "es",
                    data: balanced
                }).val(data.balanceado).trigger('change');

                tr.find('select[name="insumo1"]').select2({
                    theme: 'bootstrap4',
                    language: "es",
                    data: supplies
                }).val(data.insumo1).trigger('change');

                tr.find('select[name="insumo2"]').select2({
                    theme: 'bootstrap4',
                    language: "es",
                    data: supplies
                }).val(data.insumo2).trigger('change');

                tr.find('select[name="insumo3"]').select2({
                    theme: 'bootstrap4',
                    language: "es",
                    data: supplies
                }).val(data.insumo3).trigger('change');

                tr.find('select[name="insumo4"]').select2({
                    theme: 'bootstrap4',
                    language: "es",
                    data: supplies
                }).val(data.insumo4).trigger('change');

            },
            initComplete: function (settings, json) {

            }
        });
    },
};


$(function () {

    $('.select2').select2({
        theme: 'bootstrap4',
        language: "es",
    });


    $('#btnBuscarPsm').on('click', function () {
        tblSearchProducts = $('#tblSearchProducts').DataTable({
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
                    'action': 'search_piscinas',
                    'ids': JSON.stringify(vents.get_ids()),
                    'empresa': 'PSM'
                },
                dataSrc: ""
            },
            columns: [
                {"data": "id"},
                {"data": "numero"},
                {"data": "empresa.siglas"},
                {"data": "id"},
            ],
            columnDefs: [
                {
                    targets: [-4],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return data;
                    }
                },
                {
                    targets: [-3],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return data;
                    }
                },
                {
                    targets: [-2],
                    class: 'text-center',
                    render: function (data, type, row) {
                        return data;
                    }
                },
                {
                    targets: [-1],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        var buttons = '<a rel="add" class="btn btn-success btn-xs" style="color: white;"><i class="fas fa-plus"></i></a> ';
                        return buttons;
                    }
                },
            ],
            initComplete: function (settings, json) {

            }
        });
        $('#myModalSearchProducts').modal('show');
    });


    $('#btnBuscarBio').on('click', function () {
        tblSearchProducts = $('#tblSearchProducts').DataTable({
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
                    'action': 'search_piscinas',
                    'ids': JSON.stringify(vents.get_ids()),
                    'empresa': 'BIO'
                },
                dataSrc: ""
            },
            columns: [
                {"data": "id"},
                {"data": "numero"},
                {"data": "empresa.siglas"},
                {"data": "id"},
            ],
            columnDefs: [
                {
                    targets: [-4],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return data;
                    }
                },
                {
                    targets: [-3],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return data;
                    }
                },
                {
                    targets: [-2],
                    class: 'text-center',
                    render: function (data, type, row) {
                        return data;
                    }
                },
                {
                    targets: [-1],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        var buttons = '<a rel="add" class="btn btn-success btn-xs" style="color: white;"><i class="fas fa-plus"></i></a> ';
                        return buttons;
                    }
                },
            ],
            initComplete: function (settings, json) {

            }
        });
        $('#myModalSearchProducts').modal('show');
    });


    $('#tblSearchProducts tbody').on('click', 'a[rel="add"]', function () {
        var tr = tblSearchProducts.cell($(this).closest('td, li')).index();
        var product = tblSearchProducts.row(tr.row).data();
        vents.add(product);
        tblSearchProducts.row($(this).parents('tr')).remove().draw();
    });


    $('#tblProducts tbody')
        .on('click', 'a[rel="remove"]', function () {
            var tr = tblProducts.cell($(this).closest('td, li')).index();
            vents.items.products.splice(tr.row, 1);
            vents.list();
            // alert_action('Notificación', '¿Seguro de quitar la Piscina de la Dieta?',
            //     function () {
            //         vents.items.products.splice(tr.row, 1);
            //         vents.list();
            //     }, function () {
            //
            //     });
        })

        .on('change', 'select[name="balanceado"]', function () {
            var tr = tblProducts.cell($(this).closest('td, li')).index();
            var data = tblProducts.row(tr.row).data();
            data.balanceado = $(this).val();
            console.log('data.balanceado')
            console.log(data.balanceado)
            /* var balan = data.balanceado;
             if (data.balanceado > 0) {
                 parseFloat(data.balanceado > 0 ? data.balanceado : 0).toFixed(0)
             } else {

             }*/
        })

        .on('change', 'input[name="cantidad"]', function () {
            var tr = tblProducts.cell($(this).closest('td, li')).index();
            var data = tblProducts.row(tr.row).data();
            data.cantidad = parseInt($(this).val());
        })

        .on('change', 'select[name="insumo1"]', function () {
            var tr = tblProducts.cell($(this).closest('td, li')).index();
            var data = tblProducts.row(tr.row).data();
            data.insumo1 = $(this).val();
            var insum1 = data.insumo1;
            if (data.insumo1 > 0) {
                $.ajax({
                    url: window.location.pathname,
                    type: 'POST',
                    data: {
                        'action': 'search_balanceado'
                    },
                    dataType: 'json',
                }).done(function (data) {
                    if (!data.hasOwnProperty('error')) {
                        $.each(data, function (key, value) {
                            if (insum1 == value.id) {
                                vents.items.products[tr.row].gramaje1 = (vents.items.products[tr.row].cantidad * eval(value.gramaje)).toFixed(0);
                                $('td:eq(5)', tblProducts.row(tr.row).node()).html('<b>' + parseFloat(vents.items.products[tr.row].gramaje1 > 0 ? vents.items.products[tr.row].gramaje1 : 0).toFixed(0) + '</b>');
                            }
                        });
                        return false;
                    }
                }).fail(function (jqXHR, textStatus, errorThrown) {
                    alert(textStatus + ': ' + errorThrown);
                }).always(function (data) {
                    //select_products.html(options);
                });
            } else {
                $('td:eq(5)', tblProducts.row(tr.row).node()).html('<b>' + 0 + '</b>');
            }
        })

        .on('change', 'select[name="insumo2"]', function () {
            var tr = tblProducts.cell($(this).closest('td, li')).index();
            var data = tblProducts.row(tr.row).data();
            data.insumo2 = $(this).val();
            var insum2 = data.insumo2;
            if (data.insumo2 > 0) {
                $.ajax({
                    url: window.location.pathname,
                    type: 'POST',
                    data: {
                        'action': 'search_balanceado'
                    },
                    dataType: 'json',
                }).done(function (data) {
                    if (!data.hasOwnProperty('error')) {
                        $.each(data, function (key, value) {
                            if (insum2 == value.id) {
                                vents.items.products[tr.row].gramaje2 = (vents.items.products[tr.row].cantidad * eval(value.gramaje)).toFixed(0);
                                $('td:eq(7)', tblProducts.row(tr.row).node()).html('<b>' + parseFloat(vents.items.products[tr.row].gramaje2 > 0 ? vents.items.products[tr.row].gramaje2 : 0).toFixed(0) + '</b>');
                            }
                        });
                        return false;
                    }
                }).fail(function (jqXHR, textStatus, errorThrown) {
                    alert(textStatus + ': ' + errorThrown);
                }).always(function (data) {
                    //select_products.html(options);
                });
            } else {
                $('td:eq(7)', tblProducts.row(tr.row).node()).html('<b>' + 0 + '</b>');
            }
        })

        .on('change', 'select[name="insumo3"]', function () {
            var tr = tblProducts.cell($(this).closest('td, li')).index();
            var data = tblProducts.row(tr.row).data();
            data.insumo3 = $(this).val();
            var insum3 = data.insumo3;
            if (data.insumo3 > 0) {
                $.ajax({
                    url: window.location.pathname,
                    type: 'POST',
                    data: {
                        'action': 'search_balanceado'
                    },
                    dataType: 'json',
                }).done(function (data) {
                    if (!data.hasOwnProperty('error')) {
                        $.each(data, function (key, value) {
                            if (insum3 == value.id) {
                                vents.items.products[tr.row].gramaje3 = (vents.items.products[tr.row].cantidad * eval(value.gramaje)).toFixed(0);
                                $('td:eq(9)', tblProducts.row(tr.row).node()).html('<b>' + parseFloat(vents.items.products[tr.row].gramaje3 > 0 ? vents.items.products[tr.row].gramaje3 : 0).toFixed(0) + '</b>');
                            }
                        });
                        return false;
                    }
                }).fail(function (jqXHR, textStatus, errorThrown) {
                    alert(textStatus + ': ' + errorThrown);
                }).always(function (data) {
                    //select_products.html(options);
                });
            } else {
                $('td:eq(9)', tblProducts.row(tr.row).node()).html('<b>' + 0 + '</b>');
            }
        })

        .on('change', 'select[name="insumo4"]', function () {
            var tr = tblProducts.cell($(this).closest('td, li')).index();
            var data = tblProducts.row(tr.row).data();
            data.insumo4 = $(this).val();
            var insum4 = data.insumo4;
            if (data.insumo4 > 0) {
                $.ajax({
                    url: window.location.pathname,
                    type: 'POST',
                    data: {
                        'action': 'search_balanceado'
                    },
                    dataType: 'json',
                }).done(function (data) {
                    if (!data.hasOwnProperty('error')) {
                        $.each(data, function (key, value) {
                            if (insum4 == value.id) {
                                vents.items.products[tr.row].gramaje4 = calculos(vents.items.products[tr.row].cantidad, value.gramaje);
                                $('td:eq(-1)', tblProducts.row(tr.row).node()).html('<b>' + parseFloat(vents.items.products[tr.row].gramaje4 > 0 ? vents.items.products[tr.row].gramaje4 : 0).toFixed(0) + '</b>');
                            }
                        });
                        return false;
                    }
                }).fail(function (jqXHR, textStatus, errorThrown) {
                    alert(textStatus + ': ' + errorThrown);
                }).always(function (data) {
                    console.log('Operacion realizada correctamente')
                });
            } else {
                $('td:eq(-1)', tblProducts.row(tr.row).node()).html('<b>' + 0 + '</b>');
            }
        });

    function calculos(libras, gramaje) {
        console.log('libras, gramaje')
        console.log(libras, gramaje)
        calculo = parseInt(libras) * eval(gramaje)
        return calculo.toFixed(0)
    }


    $('.btnSave').on('click', function (event) {
        event.preventDefault();
        var items = tblProducts.rows().data().toArray();
        if ($.isEmptyObject(items)) {
            alerta_error('Debe registar al menos una piscina a la dieta');
            return false;
        }
        $.ajax({
            url: window.location.pathname,
            data: {
                'action': $('input[name="action"]').val(),
                'mes_dieta': $('input[name="mes_dieta"]').val(),
                'fecha': $('input[name="fecha"]').val(),
                'items': JSON.stringify(items)
            },
            type: 'POST',
            dataType: 'json',
            success: function (request) {
                if (!request.hasOwnProperty('error')) {
                    Swal.fire({
                        position: 'top-end',
                        icon: 'success',
                        title: 'Registro ingresado correctamente',
                        showConfirmButton: false,
                        timer: 1500
                    });
                    location.href = '/dieta/listar/anio/';
                    return false;
                }
                alert(request.error);
            },
            error: function (jqXHR, textStatus, errorThrown) {
                alert(errorThrown + ' ' + textStatus);
            }
        });
    });

    //vents.list();
});
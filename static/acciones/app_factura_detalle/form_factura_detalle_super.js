
var tblProducts_sup;
var tblSearchProducts;
var vents_sup = {
    items: {
        producto_empresa: '',
        cantidad_usar: '',
        cantidad_ingreso: '',
        fecha_ingreso: '',
        numero_guia: '',
        costo: 0.0000000000,
        costo_aplicacion: 0.0000000000,
        responsable_ingreso: '',
        proveedor: '',
        observacion: '',
        subtotal: 0.00,
        iva: 0,
        total: 0.00,
        products: []
    },
    get_ids_sup: function () {
        var ids = [];
        $.each(this.items.products, function (key, value) {
            ids.push(value.id);
        });
        return ids;
    },
    calculate_invoice: function () {
        var subtotal = 0.00;
        var iva = $('input[name="iva"]').val();
        $.each(this.items.products, function (pos, dict) {
            console.log('dict')
            console.log(dict)
            dict.pos = pos;
            if (dict.nombre_prod.unid_aplicacion === 'GR'){
                dict.subtotal = dict.cantidad_ingreso * parseFloat(dict.nombre_prod.costo_aplicacion);
            } else if (dict.nombre_prod.unid_aplicacion === 'LB'){
                dict.subtotal = dict.cantidad_ingreso * parseFloat(dict.nombre_prod.costo_aplicacion);
            }else{
                dict.subtotal = dict.cantidad_usar * parseFloat(dict.nombre_prod.costo);
            }
            subtotal += dict.subtotal;
        });
        this.items.subtotal = subtotal;
        this.items.iva = this.items.subtotal * (iva/100);
        this.items.total = this.items.subtotal + this.items.iva;

        $('input[name="subtotal"]').val(this.items.subtotal.toFixed(2));
        $('input[name="ivacalc"]').val(this.items.iva.toFixed(2));
        $('input[name="total"]').val(this.items.total.toFixed(2));
    },
    add_sup: function (item) {
        this.items.products.push(item);
        this.list();
    },
    list: function () {
        this.calculate_invoice()
        tblProducts_sup = $('#tblProducts_sup').DataTable({
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
            bFilter: false,
            scrollY: "535px",
            destroy: true,
            data: this.items.products,
            columns: [
                {"data": "id"},
                {"data": "nombre_prod.nombre"},
                {"data": "nombre_prod.presentacion"},
                {"data": "nombre_empresa.siglas"},
                {"data": "stock"},
                {"data": "id"},
                {"data": "nombre_prod.costo"},
                {"data": "subtotal"},
            ],
            columnDefs: [
                {
                    targets: [0],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '<a rel="remove" class="btn btn-danger btn-xs btn-flat" style="color: white;"><i class="fas fa-trash-alt"></i></a>';
                    }
                },
                {
                    targets: [-7],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        // console.log(data)
                        return data;
                    }
                },
                {
                    targets: [-6],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        // console.log(data)
                        return data;
                    }
                },
                {
                    targets: [-5],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        // console.log(data)
                        return data;
                    }
                },
                {
                    targets: [-4],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '<input type="text" name="cantidad_usar" class="form-control text-center" autocomplete="off" value="' + row.cantidad_usar + '">';
                    }
                },
                {
                    targets: [-3],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '<b>' + parseFloat(row.cantidad_ingreso).toFixed(2) + '<b>';
                    }
                },
                 {
                    targets: [-2],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        // console.clear()
                        console.log('row de costoooooo')
                        console.log(row.nombre_prod)
                        // return row.nombre_prod.costo;
                        if(row.nombre_prod.unid_aplicacion === 'GR') {
                            return '<input type="text" name="costo" class="form-control text-center" autocomplete="off" value="' + parseFloat(row.costo_aplicacion > 0 ? row.costo_aplicacion : row.nombre_prod.costo_aplicacion).toFixed(9) + '">';
                            // return row.nombre_prod.costo_aplicacion;
                        }else if(row.nombre_prod.unid_aplicacion === 'LB'){
                            return '<input type="text" name="costo" class="form-control text-center" autocomplete="off" value="' + parseFloat(row.costo_aplicacion > 0 ? row.costo_aplicacion : row.nombre_prod.costo_aplicacion).toFixed(9) + '">';
                        }
                        return '<input type="text" name="costo" class="form-control text-center" autocomplete="off" value="' + parseFloat(row.costo > 0 ? row.costo : row.nombre_prod.costo).toFixed(9) + '">';
                    }
                },
                {
                    targets: [-1],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '$ ' + parseFloat(data).toFixed(2);
                    }
                },
            ],

            rowCallback(row, data, displayNum, displayIndex, dataIndex) {

                 /*$(row).find('input[name="cantidad_usar"]').TouchSpin({
                    min: 0,
                    max: 10000,
                    step: 1,
                    decimals: 2,
                    boostat: 5,
                    maxboostedstep: 10,
                }).on('change', function () {
                    vents_sup.calculate_invoice();
                }).val(1);*/

                /*$(row).find('input[name="costo"]').TouchSpin({
                    min: 0,
                    max: 10000,
                    step: 1,
                    decimals: 2,
                    boostat: 5,
                    maxboostedstep: 10,
                }).on('change', function () {
                    vents_sup.calculate_invoice();
                });*/

            },

            initComplete: function (settings, json) {

            }
        });
        // console.clear();
        console.log(this.items);
        console.log(this.get_ids_sup());
    },
};

$(function () {

    console.log('ENTRO A FORM SUPER')

    $('.select2').select2({
        theme: 'bootstrap4',
        language: "es",
    });

    /*$("input[name='iva']").on('change keyup', function () {
        vents_sup.calculate_invoice();
    });*/

    $("input[name='iva']").TouchSpin({
        min: 0,
        max: 100,
        step: 0.01,
        decimals: 2,
        boostat: 5,
        maxboostedstep: 10,
        postfix: '%'
    }).on('change touchspin.on.min touchspin.on.max', function () {
            var iva = $(this).val();
            if (iva === '' || iva === 0.00) {
                $(this).val('12');
            }
            vents_sup.calculate_invoice();
    }).val(12);

    // const isEmpty = str => !str.trim().length;

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
                    'action': 'search_products',
                    'ids': JSON.stringify(vents_sup.get_ids_sup()),
                    'empresa': 'PSM'
                },
                dataSrc: ""
            },
            columns: [
                {"data": "nombre_prod.nombre"},
                {"data": "nombre_empresa.nombre"},
                {"data": "id"},
            ],
            columnDefs: [
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
                        return '<a rel="add" class="btn btn-success btn-xs btn-flat" style="color: white;"><i class="fas fa-plus"></i></a> ';
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
                    'action': 'search_products',
                    'ids': JSON.stringify(vents_sup.get_ids_sup()),
                    'empresa': 'BIO'
                    // 'term': $('select[name="search"]').val()
                },
                dataSrc: ""
            },
            columns: [
                {"data": "nombre_prod.nombre"},
                {"data": "nombre_empresa.nombre"},
                {"data": "id"},
            ],
            columnDefs: [
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
                        return '<a rel="add" class="btn btn-success btn-xs btn-flat" style="color: white;"><i class="fas fa-plus"></i></a> ';
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
        var product = tblSearchProducts.row(tr).data();
        // var product = tblSearchProducts.row(tr.row).data();
        product.cantidad_usar = '0';
        product.subtotal = 0.00;
        vents_sup.add_sup(product);
        tblSearchProducts.row($(this).parents('tr')).remove().draw();
    });


    $('#tblProducts_sup tbody')
        .on('click', 'a[rel="remove"]', function () {
            // var tr = tblProducts_sup.cell($(this)).index();
            var tr = tblProducts_sup.cell($(this).closest('td, li')).index();
            // alert('¿Estas seguro de eliminar el producto de tu detalle?');
            vents_sup.items.products.splice(tr.row, 1);
            vents_sup.list();
        })

        .on('change', 'input[name="cantidad_usar"]', function () {
            // console.clear();
            var cant = parseFloat($(this).val());
            var tr = tblProducts_sup.cell($(this).closest('td, li')).index();
            var data = tblProducts_sup.row(tr.row).data();
            console.log('data');
            console.log(data);
            data.cantidad_usar = cant;
            vents_sup.calculate_invoice();

            //alert(data.cantidad_usar)
            if (data.nombre_prod.presentacion === 'CANECA') {
                data.cantidad_ingreso = data.cantidad_usar * data.nombre_prod.valor_aplicacion * 1;
            } else if (data.nombre_prod.nombre === 'PRO W' ) {
                data.cantidad_ingreso = data.cantidad_usar * data.nombre_prod.peso_presentacion;
            } else if (data.nombre_prod.nombre === 'CAL' || data.nombre_prod.nombre === 'CARBONATO' || data.nombre_prod.nombre === 'MELAZA' || data.nombre_prod.nombre === 'POWER CAMARON' || data.nombre_prod.nombre === 'SILICATO ACUICOLA') {
                data.cantidad_ingreso = data.cantidad_usar;
            /*} else if (data.nombre_prod.nombre === 'ECOBONAZA') {
                data.cantidad_ingreso = data.cantidad_usar;*/
                /*alert('data.nombre_prod.categoria')
                alert(data.nombre_prod.categoria)
                alert('data.nombre_prod.valor_aplicacion')
                alert(data.nombre_prod.valor_aplicacion)
                alert('data.nombre_prod.unid_medida')
                alert(data.nombre_prod.unid_medida)
                alert('data.nombre_prod.unid_aplicacion')
                alert(data.nombre_prod.unid_aplicacion)*/
            } else if (data.nombre_prod.unid_aplicacion === 'SC') {
                data.cantidad_ingreso = data.cantidad_usar;
            } else {
                data.cantidad_ingreso = data.cantidad_usar * data.nombre_prod.peso_presentacion * data.nombre_prod.valor_aplicacion;
            }
            $('td:eq(-3)', tblProducts_sup.row(tr.row).node()).html('<b>' + data.cantidad_ingreso.toFixed(2) + '</b>');
            vents_sup.list();
        });


    $('.btnSave').on('click', function (event) {

        event.preventDefault();
        var items = tblProducts_sup.rows().data().toArray();
        if ($.isEmptyObject(items)) {
            alerta_error('Debe ingresar al menos un registro');
            return false;
        }

        $.ajax({
            url: window.location.pathname,
            data: {
                'action': $('input[name="action"]').val(),
                'fecha_ingreso': $('input[name="fecha_ingreso"]').val(),
                'numero_guia': $('input[name="numero_guia"]').val(),
                'responsable_ingreso': $('input[name="responsable_ingreso"]').val(),
                'proveedor': $('select[name="proveedor"]').val(),
                'subtotal': $('input[name="subtotal"]').val(),
                'iva': $('input[name="iva"]').val(),
                'ivacalc': $('input[name="ivacalc"]').val(),
                'total': $('input[name="total"]').val(),
                'observacion': $('textarea[name="observacion"]').val(),
                'items': JSON.stringify(items),
            },
            type: 'POST',
            dataType: 'json',
            success: function (request) {
                if (!request.hasOwnProperty('error')) {
                    location.href = '/factura/listar';
                    return false;
                }
                alert(request.error);
            },
            error: function (jqXHR, textStatus, errorThrown) {
                alert(errorThrown + ' ' + textStatus);
            }
        });
    });

    vents_sup.list();
});
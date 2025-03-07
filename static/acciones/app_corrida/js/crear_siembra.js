var tb_detalle;
var tb_proceso;
var tb_devolucion;
var tblSearchProd;
var tblSearchPiscinas;
var acumulador = 0.00;
var sum_dias_hect = 0.00, t_hct_dias = 0, t_cost_larv = 0, cont_general = 0.00, sum_gen = 0;
var t2 = 0, sum_fot = 0;
var newRowfooter;
var foot_dev, foot_dev_detalle;
var co_1 = 0, co_2 = 0, co_3 = 0, tot_co = 0;
var h_resul = "RESULTADO ENTRE EMPRESAS";
var Tab_resp;
var tabledev;
var tprod_id;
var tprod_canti;


// TABLA ESCOGER PRODUCTOS
var dats = {
    items: {
        fecha: '',
        producto: '',
        prod_cantidad: 0.00,
        products: []
    },
    get_ids: function () {
        var ids = [];
        $.each(this.items.products, function (key, value) {
            ids.push(value.id);
        });
        return ids;
    },
    add: function (item) {
        this.items.products.push(item);
        this.list();
    },
    list: function () {
        tb_detalle = $('#tb_detalle').DataTable({
            language: {
                "oPaginate": {
                    "sFirst": "Primero",
                    "sLast": "Último",
                    "sNext": "Siguiente",
                    "sPrevious": "Anterior"
                },
                "zeroRecords": "No se encontró nada, lo siento",
                "sInfo": "Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros",
                "infoEmpty": "Tabla vacia por favor inserte datos",
                "sSearch": "Buscar:",
                "infoFiltered": "(filtrado de _MAX_ registros totales)"
            },
            dom: 'rtip',
            bPaginate: false,
            scrollY: "326px",
            destroy: true,
            order: [[3, 'asc']],
            deferRender: true,
            paging: false,
            info: false,
            data: this.items.products,
            columns: [
                {"data": "id", "width": "2%"},
                {"data": "categoria", "width": "15%"},
                {"data": "descripcion", "width": "25%"},
                {"data": "nombre", "width": "30%"},
                {"data": "id", "width": "16%"},
                {"data": "id", "width": "12%"},
            ],
            columnDefs: [
                {
                    targets: [0],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '<a rel="remove" class="btn btn-danger btn-xs" style="color: white;text-align: center"><i class="fas fa-times" style="text-align: center"></i></a> ';
                    }
                },
                {
                    targets: [1],
                    class: 'text-left',
                    orderable: false,
                    render: function (data, type, row) {

                        console.log('data')
                        console.log(data)
                        console.log('row.id')
                        console.log(row.id)
                        /*if (row.stock > 0) {
                            return '<span class="badge badge-success">' + data + '</span>'
                        }
                        return '<span class="badge badge-danger">'+data+'</span>'*/
                        if(data === 1){
                            valor = '<b>'+ 'INSUMOS' +'</b>'
                        }else{
                            valor = '<b>'+ 'BALANCEADOS' +'</b>'
                        }
                        return valor;
                    }
                },
                {
                    targets: [2, 3],
                    class: 'text-left',
                    orderable: false,
                    render: function (data, type, row) {
                        return '<b>' + data + '</b>';
                    }
                },
                {
                    targets: [-2],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '<input type="text" name="prod_cantidad" class="form-control text-center" autocomplete="off" value="' + parseFloat(row.prod_cantidad).toFixed(2) + '">';
                    }
                },
                {
                    targets: [-1],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        var val = 0.00;
                        return '<b>' + '$ '+val.toFixed(2) + '</b>';
                    }
                },
            ],
            initComplete: function (settings, json) {

            }
        });
    }
};


// CALCULOS Y DESARROLLO DE LA TABLA PROCESO DONDE SE CALCULAN LOS DETALLES GENERALES
var proceso = {
    items: {
        fecha: '',
        comp_1: 0.00,
        comp_2: 0.00,
        comp_3: 0.00,
        tot_comp: 0.00,
        producto: '',
        prod_cantidad: '',
        piscina: 0,
        dias: 0,
        siembra: 0.000,
        costo_larva: 0.00,
        dia_por_hect: 0.00,
        prod_cantidad_proceso: '',
        total: 0.00,
        resul_oper: '',
        products: []
    },
    get_ids: function () {
        var ids = [];
        $.each(this.items.products, function (key, value) {
            ids.push(value.id);
        });
        return ids;
    },
    calcular_fot: function () {
        var total_siembra_tab = 0, total_costo_larva_tab = 0, total_dia_por_hect_tab = 0, total_sum = 0;
        $.each(this.items.products, function (el, index) {
            total_siembra_tab += index.siembra;
            total_costo_larva_tab += index.costo_larva;
            total_dia_por_hect_tab += index.dia_por_hect;
            total_sum += index.total;
        });
        calculos_prod(this.items.products, total_siembra_tab, total_costo_larva_tab, total_dia_por_hect_tab, total_sum);
    },
    add: function (item) {
        this.items.products.push(item);
        this.list();
    },
    list: function () {
        console.clear();
        this.calcular_fot();
        tb_proceso = $('#tb_proceso').DataTable({
            language: {
                "oPaginate": {
                    "sFirst": "Primero",
                    "sLast": "Último",
                    "sNext": "Siguiente",
                    "sPrevious": "Anterior"
                },
                "zeroRecords": "No se encontró nada, lo siento",
                "sInfo": "Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros",
                "infoEmpty": "Tabla vacia por favor inserte datos",
                "sSearch": "Buscar:",
                "infoFiltered": "(filtrado de _MAX_ registros totales)"
            },
            //responsive: true,
            autoWidth: false,
            bPaginate: false,
            scrollY: "800px",
            scrollX: true,
            dom: 'rtilp',
            destroy: true,
            deferRender: true,
            info: false,
            data: this.items.products,
            columns: [
                {"data": "id", 'width': '3%'},
                {"data": "numero", 'width': '8%'},
                {"data": "id", 'width': '9%'},
                {"data": "id", 'width': '10%'},
                {"data": "id", 'width': '10%'},
                {"data": "id", 'width': '10%'},
                {"data": "id", 'width': '33%'},
                {"data": "id", 'width': '15%'},
                {"data": "id", 'width': '2%'},
            ],
            columnDefs: [
                {
                    targets: [0],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '<a rel="remove_proc" class="btn btn-danger btn-xs" style="color: white;"><i class="fas fa-times"><br/>' + row.id + '</i></a>';
                    }
                },
                {
                    targets: [1],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '<b>' + data + '</b>';
                    }
                },
                {
                    targets: [2],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '<input type="text" name="dias" class="form-control text-center" autocomplete="off" value="' + row.dias + '">';
                        //return row.dias;
                    }
                },
                {
                    targets: [3],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '<input type="text" name="siembra" class="form-control text-center" autocomplete="off" value="' + parseFloat(row.siembra).toFixed(3) + '">';
                    }
                },
                {
                    targets: [4],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '<b>' + parseFloat(row.costo_larva > 0 ? row.costo_larva : 0).toFixed(2) + '</b>';
                    }
                },
                {
                    targets: [5],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '<b>' + parseFloat(row.dia_por_hect > 0 ? row.dia_por_hect : 0).toFixed(2) + '</b>';
                    }
                },
                {
                    targets: [-3],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        //return `<div id="tabla_prod"></div>`;
                        return row.prod_cantidad_proceso !== null ? row.prod_cantidad_proceso : '';
                    }
                },
                {
                    targets: [-2],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        //return '<input type="text" name="cantidad_usar" class="form-control text-center" autocomplete="off" value="' + 100 + '">';
                        return '<b>' + parseFloat(row.total > 0 ? row.total : 0).toFixed(2) + '</b>';
                    }
                },
                {
                    targets: [-1],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '<a rel="btn-edit" class="btn btn-primary btn-xs" style="color: white;">&nbsp;<i class="fas fa-list"></i>&nbsp;</a>';
                    }
                },
            ],
            initComplete: function (settings, json) {

            }
        });
    }
};


// TABLA RECULTADOS DE LAS DEVOLUCIONES
var results = {
    list: function () {
        tb_devolucion = $('#tb_devolucion').DataTable({
            language: {
                "oPaginate": {
                    "sFirst": "Primero",
                    "sLast": "Último",
                    "sNext": "Siguiente",
                    "sPrevious": "Anterior"
                },
                "zeroRecords": "No se encontró nada, lo siento",
                "sInfo": "Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros",
                "infoEmpty": "Tabla vacia por favor inserte datos",
                "sSearch": "Buscar:",
                "infoFiltered": "(filtrado de _MAX_ registros totales)"
            },
            autoWidth: false,
            responsive:false,
            bPaginate: false,
            scrollY: "1000px",
            scrollX: true,
            dom: 'rtilp',
            destroy: true,
            deferRender: true,
            info: false,
            order: [[1, 'asc']],
            columns: [
                {"data": "id", 'width': '10%'},
                {"data": "id", 'width': '65%'},
                {"data": "id", 'width': '25%'},
            ],
            columnDefs: [
                {
                    targets: [0, 1, 2],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '<b>' + data + '</b>';
                    }
                }
            ],
            initComplete: function (settings, json) {

            }
        });
    }
};


// INICIO DEL SISTEMA PARTE DONDE SE EJECUTA TODO EL PROCESO DE DESARROLLO
$(function () {

    $('#btnBuscProducto').on('click', function () {
        tblSearchProd = $('#tblSearchProducts').DataTable({
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
                    'ids': JSON.stringify(dats.get_ids()),
                },
                dataSrc: ""
            },
            columns: [
                {"data": "id"},
                {"data": "nombre"},
                {"data": "id"},
            ],
            columnDefs: [
                {
                    targets: [0],
                    class: 'text-center',
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
                        return '<b>' + data + '</b>';
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


    $('#btnBuscPiscina').on('click', function () {
        tblSearchPiscinas = $('#tblSearchPiscinas').DataTable({
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
                    'action': 'search_piscina',
                    'ids': JSON.stringify(proceso.get_ids()),
                },
                dataSrc: ""
            },
            columns: [
                {"data": "id"},
                {"data": "numero"},
                {"data": "id"},
            ],
            columnDefs: [
                {
                    targets: [0],
                    class: 'text-center',
                    orderable: true,
                    render: function (data, type, row) {
                        return data;
                    }
                },
                {
                    targets: [-2],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '<b>' + data + '</b>';
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
        $('#myModalSearchPiscinas').modal('show');
    });


    $('#btnRefrescar').on('click', function () {
        mensaje_succes('Actualizando Tabla', 'success');
        proceso.list();
        restar_dias($('input[name="fecha_compra"]').val(), $('input[name="fecha_transferencia"]').val());
    });


    $('#tblSearchProducts tbody').on('click', 'a[rel="add"]', function () {
        var tr = tblSearchProd.cell($(this).closest('td, li')).index();
        var product = tblSearchProd.row(tr.row).data();
        dats.add(product);
        tblSearchProd.row($(this).parents('tr')).remove().draw();
    });


    $('#tblSearchPiscinas tbody').on('click', 'a[rel="add"]', function () {
        var tr = tblSearchPiscinas.cell($(this).closest('td, li')).index();
        var product = tblSearchPiscinas.row(tr.row).data();
        proceso.add(product);
        tblSearchPiscinas.row($(this).parents('tr')).remove().draw();
    });


    // ESTA ES LA PRIMERA TABLA
    $('#tb_detalle tbody')
        .on('click', 'a[rel="remove"]', function () {
            var tr = $("#tb_detalle").DataTable().cell($(this).closest('td, li')).index();
            dats.items.products.splice(tr.row, 1);
            dats.list();
        })

        .on('change', 'input[name="prod_cantidad"]', function () {
            var tr = tb_detalle.cell($(this).closest('td, li')).index();
            var data = tb_detalle.row(tr.row).data();
            data.prod_cantidad = parseFloat($(this).val());
            console.log('data.prod_cantidad')
            console.log(data.prod_cantidad)
            console.log('data')
            console.log(data)
            var val = (data.costo * data.prod_cantidad);
            $('td:eq(-1)', tb_detalle.row(tr.row).node()).html('<b>' + '$ '+val.toFixed(2) + '</b>');
        });


    // ESTA ES LA SEGUNDA TABLA
    $('#tb_proceso tbody')
        .off()
        .on('click', 'a[rel="remove_proc"]', function () {
            var tr = tb_proceso.cell($(this).closest('td')).index();
            alert_action('Notificación', '¿Estas seguro de eliminar la Piscina?',
                function () {
                    proceso.items.products.splice(tr.row, 1);
                    proceso.list();
                }, function () {

            });
        })

        .on('change', 'input[name="dias"]', function () {
            var tr_mant = $(this).parents("tr")[0]
            var tr = tb_proceso.cell($(this).closest('td, li')).index();
            var data = tb_proceso.row(tr.row).data();
            data.dias = parseInt($(this).val());
            data.dia_por_hect = data.dias * data.hect;
            $('td:eq(-4)', tb_proceso.row(tr.row).node()).html('<b>' + data.dia_por_hect.toFixed(2) + '</b>');
            $("td:eq(2)", tr_mant).text(data.dias);
        })

        .on('change', 'input[name="siembra"]', function () {
            var tr_mant = $(this).parents("tr")[0]
            var tr = tb_proceso.cell($(this).closest('td, li')).index();
            var data = tb_proceso.row(tr.row).data();
            data.siembra = parseFloat($(this).val());
            $("td:eq(3)", tr_mant).text(data.siembra);
            proceso.calcular_fot();
        })

        .on('click', 'a[rel="btn-edit"]', function (e) {
            var tr2 = tb_proceso.cell($(this).closest('td, li')).index();
            var data = tb_proceso.row(tr2.row).data();
            console.log('BOTON EDIT');
            console.log(data);
            const tr = $(this).parents("tr")[0]
            console.log(tr);
            $("td:eq(2)", tr).empty().append($('<input type="text" name="dias" class="form-control text-center" autocomplete="off" value="' + data.dias + '">'))
            $("td:eq(3)", tr).empty().append($('<input type="text" name="siembra" class="form-control text-center" autocomplete="off" value="' + data.siembra + '">'))
            $("td:eq(-1)", tr).prepend("<a rel='btn-update' class='btn btn-info btn-xs' style='color: white;'> <i class='fas fa-edit'></i> </a> <a rel='btn-cancel' class='btn btn-danger btn-xs' style='color: white;'> <i class='fas fa-times'></i> </a>")
            $(this).hide()
        })

        .on('click', 'a[rel="btn-cancel"]', function (e) {
            var tr2 = tb_proceso.cell($(this).closest('td, li')).index();
            var data = tb_proceso.row(tr2.row).data();
            const tr = $(this).parents("tr")[0]
            console.log(tr);

            $("td:eq(2)", tr).text(data.dias)
            $("td:eq(3)", tr).text(data.siembra.toFixed(3))

            $("a[rel=\"btn-edit\"]", tr).show()
            $("a[rel=\"btn-update\"], a[rel=\"btn-cancel\"]", tr).remove()
        });


    $('.btnCalcular').on('click', function (event) {
        proceso.list();
        $(newRowfooter).appendTo("#tb_proceso");
        document.getElementById("resul").innerHTML = h_resul;
        var tr = tb_detalle.cell($(this).closest('td, li')).index();
        var data = tb_detalle.row(tr).data();
        data.resul_oper = tabledev;
        document.getElementById("Resultad_ope").innerHTML = data.resul_oper;
        $(foot_dev).appendTo("#tb_devolucion");
        $(foot_dev_detalle).appendTo("#tb_detalle");
    });


    $('.btnSave').on('click', function (event) {
        event.preventDefault();
        console.log('llego aqui')
        var items = tb_proceso.rows().data().toArray();
        if ($.isEmptyObject(items)) {
            alerta_error('Debe ingresar al menos un registro');
            return false;
        }
        $.ajax({
            url: window.location.pathname,
            data: {
                'action': $('input[name="action"]').val(),
                'fecha_registro': $('input[name="fecha_registro"]').val(),
                'fecha_compra': $('input[name="fecha_compra"]').val(),
                'fecha_transferencia': $('input[name="fecha_transferencia"]').val(),
                'comp_1': $('input[name="comp_1"]').val(),
                'comp_2': $('input[name="comp_2"]').val(),
                'comp_3': $('input[name="comp_3"]').val(),
                'tot_comp': $('input[name="tot_comp"]').val(),
                'observacion': $('input[name="observacion"]').val(),
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
                    location.href = '/corrida/listar_siembra';
                    return false;
                }
                alert(request.error);
            },
            error: function (jqXHR, textStatus, errorThrown) {
                alert(errorThrown + ' ' + textStatus);
            }
        });
    });


    $("input[name='comp_1']").on('change keyup', function () {
        suma_cuant();
    });


    $("input[name='comp_2']").on('change keyup', function () {
        suma_cuant();
    });


    $("input[name='comp_3']").on('change keyup', function () {
        suma_cuant();
    });


    $('#btnCalcFechas').on('click', function () {
        mensaje_succes('Dias Calculados', 'info');
        restar_dias($('input[name="fecha_compra"]').val(), $('input[name="fecha_transferencia"]').val());
    });


    $("input[name='fecha_transferencia']").on('change', function () {
        mensaje_succes('Dias Calculados', 'info');
        restar_dias($('input[name="fecha_compra"]').val(), $('input[name="fecha_transferencia"]').val());
    });


    dats.list();
    proceso.list();
    results.list();

});


function restar_dias(fecha_1, fecha_2) {
    var day1 = new Date(fecha_1.split('/').reverse().join('/'));
    var day2 = new Date(fecha_2.split('/').reverse().join('/'));

    var difference = Math.abs(day2 - day1);
    var days = difference / (1000 * 3600 * 24)

    console.log( ' Los dias son: '+ (days+1))
    document.getElementById("lblResulDias").innerHTML = '<h3><span class="badge badge-danger">Resultado: &nbsp; <b>'+ (days+1) + '</b>  &nbsp; dias </span></h3>';
    return (days+1);
}


function suma_cuant() {
    const $total = document.getElementById('tot_comp_sum');
    let subtotal = 0;
    [...document.getElementsByClassName("monto")].forEach(function (element) {
        if (element.value !== '') {
            subtotal += parseFloat(element.value);
        }
    });
    $total.value = subtotal;
    tot_co = subtotal;
}


function calculos_prod(json, tot_siembra, tot_cost_larv, tot_dia_hec, tot_sum) {
    sum_dias_hect = tot_siembra;
    t_hct_dias = tot_dia_hec;
    t_cost_larv = tot_cost_larv;
    sum_gen = tot_sum;

    var tabla_final = {}

    newRowfooter = '<tr>';

    json.map(function (dict, pos) {

        console.log('dict')
        console.log(dict)
        dict.costo_larva = (tot_co / sum_dias_hect) * dict.siembra;

        var psm = 'PSM', bio = 'BIO';
        var total_consumos = 0, cantidad_tab_int = 0, conteo = 0, nombre = '', ref = 0, cant_ref = 0;

        var tableData = '<table class="table table-sm table-striped table-bordered tb"><thead><tr><th>Nombre</th><th>Cantidad</th></tr></thead><tbody>';
        var res_prod_cant = '<table class="table table-sm table-striped table-bordered tb"><thead><tr><th>Nombre</th><th>Cantidad</th></tr></thead><tbody>';

        tb_detalle.rows().data().toArray().forEach(function (value, pos, array) {
            console.log('Presentacion del resultado tb_detalle')
            console.log(value)
            nombre = value.nombre;
            cantidad_tab_int = value.prod_cantidad / t_hct_dias * dict.dia_por_hect;
            total_consumos += cantidad_tab_int;
            tableData += '<tr>'
            tableData += '<td style="text-align: center">' + value.nombre + '</td>'
            tableData += '<td style="text-align: center">' + parseFloat(cantidad_tab_int > 0 ? cantidad_tab_int : 0).toFixed(2) + '</td>'
            tableData += '</tr>';
            dict.total = parseFloat(total_consumos);

            // Proceso Interno, objeto de la tabla prod ingresado
            ref = value.id;
            res_prod_cant += '<tr>'
            res_prod_cant += '<td style="text-align: center">' + value.nombre + '</td>'
            res_prod_cant += '<td style="text-align: center">' + parseFloat(value.prod_cantidad).toFixed(2) + '</td>'
            res_prod_cant += '</tr>';

            console.log('value')
            console.log(value)

            // Objeto devolucion
            producto = nombre;
            cantidad = cantidad_tab_int;

            if (dict.orden <= 20) {
                console.log("entro a psm")
                if (!tabla_final.hasOwnProperty(psm)) {
                    tabla_final[psm] = {}
                }
                if (tabla_final[psm].hasOwnProperty(producto)) {
                    cantidad_actual = tabla_final[psm][producto] + cantidad;
                    tabla_final[psm][producto] = cantidad_actual;
                } else {
                    tabla_final[psm][producto] = cantidad;
                }

            } else {
                console.log("entro a bio")
                if (!tabla_final.hasOwnProperty(bio)) {
                    tabla_final[bio] = {}
                }
                if (tabla_final[bio].hasOwnProperty(producto)) {
                    cantidad_actual = tabla_final[bio][producto] + cantidad;
                    tabla_final[bio][producto] = cantidad_actual;
                } else {
                    tabla_final[bio][producto] = cantidad;
                }
            }

        });

        tableData += '</tbody></table>';
        dict.prod_cantidad_proceso = tableData;
        res_prod_cant += '</tbody></table>';
        dict.prod_cantidad = res_prod_cant;
        dict.producto = ref;
        dict.resul_oper = tabla_final;

    });


    // Recorro objeto devolucion para la tabla
    tabledev = '<table class="table">';
    foot_dev = '<tr>';
    foot_dev_detalle = '<tr>';
    for (var empresa in tabla_final) {
        for (var producto in tabla_final[empresa]) {
            tabledev += '<tr>'
            tabledev += '<td style="text-align: center">' + empresa + '</td>'
            tabledev += '<td style="text-align: center">' + producto + '</td>'
            tabledev += '<td style="text-align: center">' + parseFloat(tabla_final[empresa][producto]).toFixed(2) + '</td>'
            tabledev += '</tr>';
        }
    }
    tabledev += '</table>';
    foot_dev += '<th colspan="2" style="text-align: center"><b>Total</b></th>'
    foot_dev += '<td style="text-align: center"><b>' + sum_gen.toFixed(2) + '</b></td>'
    foot_dev += '</tr>';


    // Devolucion del objeto detalle tb
    foot_dev_detalle += '<th colspan="2" style="text-align: center"><b>Total</b></th>'
    foot_dev_detalle += '<th></th>'
    foot_dev_detalle += '<th></th>'
    foot_dev_detalle += '<td style="text-align: center"><b>' + sum_gen.toFixed(2) + '</b></td>'
    foot_dev_detalle += '</tr>';


    // Pie de la Tabla sumas de valores
    newRowfooter += '<th colspan="3" style="text-align: center"><b>Total</b></th>'
    newRowfooter += '<td style="text-align: center"><b>' + sum_dias_hect.toFixed(3) + '</b></td>'
    newRowfooter += '<td style="text-align: center"><b>' + t_cost_larv.toFixed(2) + '</b></td>'
    newRowfooter += '<td style="text-align: center"><b>' + t_hct_dias.toFixed(2) + '</b></td>'
    newRowfooter += '<td style="text-align: center"></td>'
    newRowfooter += '<td style="text-align: center"><b>' + sum_gen.toFixed(2) + '</b></td>'
    newRowfooter += '<td style="text-align: center"></td>'
    newRowfooter += '</tr>';

}
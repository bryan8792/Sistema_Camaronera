var tbl_transaccionPlan;
var tblSearchPlan;
var clave_acceso;
var select_receipt, select_company;
var deb = 0.00, hab = 0.00;
var date_now = new moment().format('YYYY-MM-DD');
const fecha_actual = new Date();

var vents = {
    items: {
        codigo: 0,
        comprobante: '',
        tip_cuenta: '',
        direccion: '',
        descripcion: '',
        ruc: '',
        fecha: '',
        products: []
    },
    get_ids: function () {
        var ids = [];
        $.each(this.items.products, function (key, value) {
            ids.push(value.id);
        });
        return ids;
    },
    calculate_invoice: function () {
        var debe = 0.00, haber = 0.00, detalle = '';
        $.each(this.items.products, function (pos, dict) {
            console.log(dict)
            dict.pos = pos;
            detalle = dict.detalle;
            debe += parseFloat(dict.debe);
            haber += parseFloat(dict.haber);
        });
        this.items.detalle = detalle;
        this.items.debe = debe;
        this.items.haber = haber;
        console.log(debe)
        console.log(haber)
        calculos_prod(this.items.products, debe, haber);

        /*$('input[name="debe_resp"]').val(this.items.debe.toFixed(2));
        $('input[name="haber_resp"]').val(this.items.haber.toFixed(2));*/
    },
    add: function (item) {
        console.log('item: ', item)
        this.items.products.push(item);
        this.list();
    },
    searchVoucherNumber: function () {
        var company = select_company.val();
        var receipt = select_receipt.val();

        if (!company || company === "") {
            Swal.fire({
                title: 'Error',
                text: 'Por favor, selecciona una empresa antes de continuar.',
                icon: 'warning',
                confirmButtonText: 'Entendido'
            });
            return;
        }

        if (!receipt || receipt === "") {
            Swal.fire({
                title: 'Error',
                text: 'Por favor, selecciona un tipo de recibo antes de continuar.',
                icon: 'warning',
                confirmButtonText: 'Entendido',
            });
            return;
        }

        $.ajax({
            url: window.location.pathname, // Ruta actual de la vista
            data: {
                action: 'search_voucher_number',
                receipt: receipt,
                company: company,
            },
            type: 'POST',
            dataType: 'json',
            headers: {
                'X-CSRFToken': csrftoken,
            },
        })
            .done(function (data) {
                if (!data.hasOwnProperty('error')) {
                    $('input[name="comp_numero"]').val(data.voucher_number);
                } else {
                    Swal.fire({
                        title: 'Error',
                        text: data.error,
                        icon: 'error',
                        confirmButtonText: 'Entendido',
                    });
                }
            })
            .fail(function (jqXHR, textStatus, errorThrown) {
                Swal.fire({
                    title: 'Error',
                    text: 'Ocurrió un error al buscar el número de comprobante: ' + textStatus,
                    icon: 'error',
                    confirmButtonText: 'Entendido',
                });
            });

    },
    searchVoucherRecibo: function () {
        var company = select_company.val();
        var receipt = select_receipt.val();

        if (!company || company === "") {
            Swal.fire({
                title: 'Error',
                text: 'Por favor, selecciona una empresa antes de continuar.',
                icon: 'warning',
                confirmButtonText: 'Entendido'
            });
            return;
        }


        $.ajax({
            url: window.location.pathname, // Ruta actual de la vista
            data: {
                action: 'search_recibo',
                company: company,
            },
            type: 'POST',
            dataType: 'json',
            headers: {
                'X-CSRFToken': csrftoken,
            },
        })
            .done(function (data) {
                if (!data.hasOwnProperty('error')) {
                    console.log(data['recibos'])
                    const select = $('select[name="receipt"]');
                    select.empty();
                    select.append('<option value="" selected>Seleccione una opción</option>');

                    data['recibos'].forEach(option => {
                        select.append(`<option value="${option.codigo}">${option.text}</option>`);
                    });
                    //$('input[name="receipt"]').val(data.voucher_number);
                } else {
                    Swal.fire({
                        title: 'Error',
                        text: data.error,
                        icon: 'error',
                        confirmButtonText: 'Entendido',
                    });
                }
            })
            .fail(function (jqXHR, textStatus, errorThrown) {
                Swal.fire({
                    title: 'Error',
                    text: 'Ocurrió un error al buscar el número de comprobante: ' + textStatus,
                    icon: 'error',
                    confirmButtonText: 'Entendido',
                });
            });

    },
    list: function () {
        this.calculate_invoice();
        tbl_transaccionPlan = $('#tbl_transaccionPlan').DataTable({
            language: {
                "lengthMenu": "Mostrar _MENU_ registros",
                "zeroRecords": "No se encontraron resultados",
                "info": "Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros",
                "infoEmpty": "Mostrando registros del 0 al 0 de un total de 0 registros",
                "infoFiltered": "(filtrado de un total de _MAX_ registros)",
                "sSearch": "Buscar:",
                "oPaginate": {
                    "sFirst": "Primero",
                    "sLast": "Último",
                    "sNext": "Siguiente",
                    "sPrevious": "Anterior"
                },
                "sProcessing": "Procesando...",
            },
            dom: 'rtip',
            /*buttons: [
                {
                    extend: 'excelHtml5',
                    text: '<i class="fas fa-file-excel"></i> ',
                    titleAttr: 'Exportar a Excel',
                    className: 'btn btn-success'
                },
                {
                    extend: 'pdfHtml5',
                    text: '<i class="fas fa-file-pdf"></i> ',
                    titleAttr: 'Exportar a PDF',
                    className: 'btn btn-danger'
                },
                {
                    extend: 'print',
                    text: '<i class="fa fa-print"></i> ',
                    titleAttr: 'Imprimir',
                    className: 'btn btn-info'
                },
                {
                    extend: 'copyHtml5',
                    text: '<i class="fas fa-copy"></i> ',
                    titleAttr: 'Copiar Datos',
                    className: 'btn btn-secondary'
                },
                {
                    extend: 'csvHtml5',
                    text: '<i class="fas fa-file-csv"></i> ',
                    titleAttr: 'Exportar a CSV',
                    className: 'btn btn-success'
                },
                {
                    extend: 'colvis',
                    text: '<i class="fas fa-file-export"></i> ',
                    titleAttr: 'Exportar a CSV',
                    className: 'btn btn-success'
                },
            ],*/
            bPaginate: false,
            responsive: true,
            autoWidth: false,
            bFilter: false,
            scrollY: "305px",
            destroy: true,
            data: this.items.products,
            // order : [[0, 'asc']],
            columns: [
                {"data": "id", "width": "3%"},
                {"data": "codigo", "width": "10%"},
                {"data": "nombre", "width": "20%"},
                {"data": "detalle", "width": "47%"},
                {"data": "debe", "width": "10%"},
                {"data": "haber", "width": "10%"},

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
                    targets: [1],
                    class: 'text-left',
                    orderable: false,
                    render: function (data, type, row) {
                        /*var ampliar = row.codigo + ' / '+ row.nombre;
                        return ampliar;*/
                        return data;
                    }
                },
                {
                    targets: [2],
                    class: 'text-left',
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
                        // return '<input type="text" name="detalle" class="form-control text-center border-0" autocomplete="off" value="' + (row.detalle != null ? row.detalle : '') + '">';
                        return '<input type="text" name="detalle" class="form-control text-center border-0" autocomplete="off" value="' + (row.detalle != null ? row.detalle : '') + '">';
                    }
                },
                {
                    targets: [-2],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        console.log(data)
                        // return '<input type="text" name="debe" class="form-control text-center border-0" autocomplete="off" value="' + parseFloat(row.debe > 0 ? row.debe : 0).toFixed(2) + '">';
                        return '<input type="text" name="debe" class="form-control text-center border-0" autocomplete="off" value="' + parseFloat(row.debe > 0 ? row.debe : 0).toFixed(2) + '">';
                    }
                },
                {
                    targets: [-1],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        // return '<input type="text" name="haber" class="form-control text-center border-0" autocomplete="off" value="' + parseFloat(row.haber > 0 ? row.haber : 0).toFixed(2) + '">';
                        return '<input type="text" name="haber" class="form-control text-center border-0" autocomplete="off" value="' + parseFloat(row.haber > 0 ? row.haber : 0).toFixed(2) + '">';
                    }
                },

            ],
            rowCallback(row, data, index) {
                var tr = $(row).closest('tr');

                /*tr.find('input[name="debe"]')
                    .TouchSpin({
                        min: 0.00,
                        max: 1000000,
                        step: 0.01,
                        decimals: 2,
                        boostat: 5,
                        verticalbuttons: true,
                        maxboostedstep: 10,
                    })
                    .on('change', function () {
                        vents.calculate_invoice();
                    })
                    .val(0.00);*/

                tr.find('input[name="debe"]').blur(function () {
                    vents.calculate_invoice();
                });

                /*tr.find("input[name='haber']")
                    .TouchSpin({
                        min: 0,
                        max: 1000000,
                        step: 0.01,
                        decimals: 2,
                        boostat: 5,
                        maxboostedstep: 10,
                    }).on('change', function () {
                    vents.calculate_invoice();
                    })
                    .val(0.00);*/

                tr.find('input[name="haber"]').blur(function () {
                    vents.calculate_invoice();
                });

            },
            initComplete: function (settings, json) {

            },
            /*footerCallback: function (row, data, index) {

            total_debe = this.api()
                .column(3)
                //.column(3, {page: 'current'})//para sumar solo la pagina actual
                .data()
                .reduce(function (a, b) {
                    return parseInt(a) + parseInt(b);
                }, 0);
            $(this.api().column(3).footer()).html('' + total_debe);

            total_haber = this.api()
                .column(4)
                //.column(4, {page: 'current'})//para sumar solo la pagina actual
                .data()
                .reduce(function (a, b) {
                    return parseInt(a) + parseInt(b);
                }, 0);
            $(this.api().column(4).footer()).html('' + total_haber);
            // $(this.api().column(6).footer()).html('' + total_ing - total_eg);
        },*/

        });
        // console.clear();
        console.log(this.items);
        console.log(this.get_ids());
    }
};

function formatRepo(repo) {
    if (repo.loading) {
        return repo.text;
    }

    var option = $(
        '<div class="wrapper container">' +
        '<div class="row">' +
        '<div class="col-lg-1">' +
        '<i class=\'fa fa-sort-amount-down-alt\'></i>' +
        '</div>' +
        '<div class="col-lg-11">' +
        '<p style="margin-bottom: 0;">' +
        '<b>Codigo:</b>' + '&nbsp;&nbsp;&nbsp;' + repo.codigo + '<br>' +
        '<b>Nombre:</b>' + '&nbsp;&nbsp;' + repo.nombre + '<br>' +
        '<b>Nivel:</b>' + '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' + repo.nivel + '<br>' +
        '<b>Detalle de Cuenta Padre:</b>' + '&nbsp;&nbsp;' + repo.cuenta_padre + '<br>' +
        '</p>' +
        '</div>' +
        '</div>' +
        '</div>');

    return option;
}

function validateExt() {
    var ext = $('input[name="archive"]').val().split('.').pop().toLowerCase();
    return $.inArray(ext, ['xml', 'lxml']) !== -1;
}

document.addEventListener('DOMContentLoaded', function (e) {
    const form = document.getElementById('frmUploadExcel');
    const fv = FormValidation.formValidation(form, {
            locale: 'es_ES',
            localization: FormValidation.locales.es_ES,
            plugins: {
                trigger: new FormValidation.plugins.Trigger(),
                submitButton: new FormValidation.plugins.SubmitButton(),
                bootstrap: new FormValidation.plugins.Bootstrap(),
                icon: new FormValidation.plugins.Icon({
                    valid: 'fa fa-check',
                    invalid: 'fa fa-times',
                    validating: 'fa fa-refresh',
                }),
            },
            fields: {
                archive: {
                    validators: {
                        notEmpty: {},
                        callback: {
                            message: 'Introduce un archivo en formato xml',
                            callback: function (input) {
                                return validateExt();
                            }
                        },
                    }
                },
            },
        }
    )
        .on('core.element.validated', function (e) {
            if (e.valid) {
                const groupEle = FormValidation.utils.closest(e.element, '.form-group');
                if (groupEle) {
                    FormValidation.utils.classSet(groupEle, {
                        'has-success': false,
                    });
                }
                FormValidation.utils.classSet(e.element, {
                    'is-valid': false,
                });
            }
            const iconPlugin = fv.getPlugin('icon');
            const iconElement = iconPlugin && iconPlugin.icons.has(e.element) ? iconPlugin.icons.get(e.element) : null;
            iconElement && (iconElement.style.display = 'none');
        })
        .on('core.validator.validated', function (e) {
            if (!e.result.valid) {
                const messages = [].slice.call(form.querySelectorAll('[data-field="' + e.field + '"][data-validator]'));
                messages.forEach((messageEle) => {
                    const validator = messageEle.getAttribute('data-validator');
                    messageEle.style.display = validator === e.validator ? 'block' : 'none';
                });
            }
        })
        .on('core.form.valid', function () {
            var parameters = new FormData($(fv.form)[0]);
            parameters.append('action', 'upload_xml');
            $.ajax({
                url: window.location.pathname,
                data: parameters,
                type: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken
                },
                dataType: 'json',
                processData: false,
                contentType: false,
                success: function (request) {
                    if (!request.hasOwnProperty('error')) {
                        let factura = JSON.parse(request);

                        const {info_tributaria, info_factura, detalles} = factura;

                        console.log('info_tributaria')
                        console.log(info_tributaria)
                        console.log('info_factura')
                        console.log(info_factura)
                        console.log('detalles')
                        console.log(detalles)

                        console.log('factura')
                        console.log(factura)
                        console.log("Nombre Comercial:", factura.info_tributaria.nombre_comercial);
                        console.log("Razón Social:", factura.info_tributaria.razon_social);
                        console.log("RUC:", factura.info_tributaria.ruc);
                        console.log("Establecimiento:", factura.info_tributaria.estab);
                        console.log("Secuencial:", factura.info_tributaria.secuencial);
                        console.log("Fecha de emisión:", factura.info_factura.fecha_emision);
                        factura.detalles.forEach((detalle, index) => {
                            console.log(`Detalle ${index + 1}:`);
                            console.log("Descripción:", detalle.descripcion);
                            console.log("Cantidad:", detalle.cantidad);
                            console.log("Precio Unitario:", detalle.precio_unitario);
                            console.log("Precio Total:", detalle.precio_total);
                        });
                        Swal.fire({
                            position: 'toPosition',
                            icon: 'success',
                            title: 'XML cargado correctamente',
                            showConfirmButton: false,
                            timer: 1500
                        });
                        let fechaEmision = factura.info_factura.fecha_emision;
                        console.log(fechaEmision)
                        let [dia, mes, anio] = fechaEmision.split('/');
                        let fechaFormateada = new Date(`${anio}-${mes}-${dia}`).toISOString().split('T')[0];
                        let full_number_serie = factura.info_tributaria.cod_estab + factura.info_tributaria.pto_Emi;
                        $('input[name="ruc"]').val(factura.info_tributaria.ruc);
                        $('input[name="comprobante"]').val(factura.info_tributaria.clave_acceso);
                        $('input[name="fecha"]').val(fechaFormateada);
                        $('input[name="descripcion"]').val(factura.info_tributaria.razon_social);
                        $('textarea[name="direccion"]').val(factura.info_tributaria.dir_matriz);
                        $('input[name="comp_serie"]').val(full_number_serie);
                        $('input[name="comp_secuencia"]').val(factura.info_tributaria.secuencial);
                        $('input[name="n_autoriz"]').val(factura.info_tributaria.clave_acceso);
                        $('#myModalUploadXML').modal('hide')
                        return false;
                    }
                    message_error(request.error);
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    message_error(errorThrown + ' ' + textStatus);
                },
            });
            /*alert_sweetalert('success', 'Alerta', 'Productos actualizados correctamente', function () {
                location.reload();
            }, 2000, null);*/
        });
});

/*
function validateExt() {
    const ext = $('input[name="archive"]').val().split('.').pop().toLowerCase();
    return ['xml', 'lxml'].includes(ext);
}

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('frmUploadExcel');

    const fv = FormValidation.formValidation(form, {
        locale: 'es_ES',
        localization: FormValidation.locales.es_ES,
        plugins: {
            trigger: new FormValidation.plugins.Trigger(),
            submitButton: new FormValidation.plugins.SubmitButton(),
            bootstrap: new FormValidation.plugins.Bootstrap(),
            icon: new FormValidation.plugins.Icon({
                valid: 'fa fa-check',
                invalid: 'fa fa-times',
                validating: 'fa fa-refresh',
            }),
        },
        fields: {
            archive: {
                validators: {
                    notEmpty: {},
                    callback: {
                        message: 'Introduce un archivo en formato XML',
                        callback: validateExt,
                    },
                },
            },
        },
    })
        .on('core.form.valid', () => {
            const parameters = new FormData(form);
            parameters.append('action', 'upload_xml');

            $.ajax({
                url: window.location.pathname,
                data: parameters,
                type: 'POST',
                headers: { 'X-CSRFToken': csrftoken },
                dataType: 'json',
                processData: false,
                contentType: false,
                success: (response) => {
                    if (!response.error) {
                        const factura = JSON.parse(response);

                        const { info_tributaria, info_factura, detalles } = factura;

                        console.log("info_tributaria")
                        console.log(info_tributaria)
                        console.log("info_factura")
                        console.log(info_factura)
                        console.log("detalles")
                        console.log(detalles)
                        // console.log('info_factura.fecha_emision')
                        // console.log(info_factura.fecha_emision)

                        // Asignar datos de la factura al formulario
                        // let fechaEmision = info_factura.fecha_emision;
                        // let [dia, mes, anio] = fechaEmision.split('-');
                        // let fechaFormateada = new Date(`${anio}-${mes}-${dia}`).toISOString().split('T')[0];
                        // $('input[name="ruc"]').val(info_tributaria.clave_acceso);
                        $('input[name="comprobante"]').val(info_tributaria.clave_acceso);
                        $('textarea[name="direccion"]').val(info_tributaria.dir_matriz);
                        $('input[name="descripcion"]').val(info_tributaria.razon_social);
                        $('input[name="n_autoriz"]').val(info_tributaria.clave_acceso);

                        // $('input[name="fecha"]').val(fechaFormateada).trigger('change');

                        Swal.fire({
                            position: 'top-end',
                            icon: 'success',
                            title: 'XML cargado correctamente',
                            showConfirmButton: false,
                            timer: 1500,
                        });

                        $('#myModalUploadXML').modal('hide');
                    } else {
                        message_error(response.error);
                    }
                },
                error: (jqXHR, textStatus, errorThrown) => {
                    message_error(`${errorThrown} ${textStatus}`);
                },
            });

            return false;
        });
});
*/

$(function () {

    select_receipt = $('select[name="receipt"]');
    select_company = $('select[name="company"]');

    select_receipt.on('change', function () {
        $('.content-electronic-billing').find('input,select').prop('disabled', $(this).val() !== '01');
        vents.searchVoucherNumber();
    });

    select_company.on('change', function () {
        vents.searchVoucherRecibo();
    });

    $('.select2').select2({
        theme: 'bootstrap4',
        language: "es",
    });

    $('#btnBuscarPlanPSM').on('click', function () {
        tblSearchPlan = $('#tblSearchPlan').DataTable({
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
            // rowsGroup: [3],
            dom: 'frtip',
            // keys: true,
            keys: {
                focus: ':eq(0)'
            },
            bPaginate: false,
            ordering: false,
            responsive: true,
            autoWidth: false,
            scrollY: "305px",
            destroy: true,
            select: "row",
            autoheight: true,
            autowidth: true,
            width: '100%',
            /*view:"treetable",*/
            ajax: {
                url: window.location.pathname,
                type: 'POST',
                beforeSend: function () {
                    loading_message('Cargando Plan por favor Espere .....');
                },
                data: {
                    'action': 'search_plan',
                    'ids': JSON.stringify(vents.get_ids()),
                    'empresa': 'PSM'
                },
                dataSrc: "",
                complete: function () {
                    // Ocultar el overlay cuando la petición ha terminado
                    $.LoadingOverlay("hide");
                }

            },
            columns: [
                {"data": "codigo", "searchable": true},
                {"data": "tipo_cuenta"},
                {"data": "nombre"},
                {"data": "empresa.siglas"},
                {"data": "id"},
            ],
            /*buttons: [
                /!*{
                    text: 'Button <u>9</u>',
                    key: '9',
                    action: function (e, dt, node, config) {
                        alert('Button 9 activated');
                    }
                },*!/
                /!*{
                    text: 'Button <u><i>shift</i> 9</u>',
                    // key: {
                    //     shiftKey: true,
                    //     key: '9'
                    // },
                    // action: function (e, dt, node, config) {
                    //     alert('Button 9 activated');
                    // }
                }*!/
            ],*/
            datatype: "xml",
            // aLengthMenu: [
            //     [15, 20, 25, 30, -1],
            //     [15, 20, 25, 30, "All"]
            // ],
            // order : [[0, 'asc']],
            columnDefs: [
                {
                    targets: [0],
                    class: 'text-left',
                    // orderable: true,
                    searchable: true,
                    render: function (data, type, row) {
                        return data;
                    }
                },
                {
                    targets: [-4, -3],
                    // visible: false,
                    class: 'text-left',
                    orderable: true,
                    render: function (data, type, row) {
                        return data;
                    }
                },
                {
                    targets: [-2],
                    class: 'text-left',
                    orderable: true,
                    render: function (data, type, row) {
                        return data;
                    }
                },
                {
                    targets: [-1],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        console.log('data')
                        console.log(data)
                        console.log('row.tipo_cuenta')
                        console.log(row.tipo_cuenta)
                        if (row.tipo_cuenta === 'GENERAL' || row.tipo_cuenta === 'G' || row.tipo_cuenta === 'GEN') {
                            return '<a rel="neg" class="btn btn-danger btn-xs btn-flat" style="color: white;"><i class="fas fa-times"></i></a> ';
                        }
                        return '<a rel="add" class="btn btn-success btn-xs btn-flat" style="color: white;"><i class="fas fa-plus"></i></a> ';
                    }
                },
            ],
            initComplete: function (settings, json) {
                // console.log('settings')
                // console.log(settings.aoData)
                /*$(this).closest('.dataTables_wrapper').find('.dataTables_filter input').val();
                $(this).key()*/
            }
        });
        $('#myModalSearchPlan').modal('show');
    });

    $('#btnBuscarPlanBIO').on('click', function () {
        tblSearchPlan = $('#tblSearchPlan').DataTable({
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
            dom: 'frtip',
            keys: {
                focus: ':eq(0)'
            },
            bPaginate: false,
            ordering: false,
            responsive: true,
            autoWidth: false,
            scrollY: "305px",
            destroy: true,
            select: "row",
            ajax: {
                url: window.location.pathname,
                type: 'POST',
                beforeSend: function () {
                    loading_message('Cargando Plan por favor Espere .....');
                },
                data: {
                    'action': 'search_plan',
                    'ids': JSON.stringify(vents.get_ids()),
                    'empresa': 'BIO'
                },
                dataSrc: "",
                complete: function () {
                    // Ocultar el overlay cuando la petición ha terminado
                    $.LoadingOverlay("hide");
                }
            },
            columns: [
                {"data": "codigo", "searchable": true},
                {"data": "tipo_cuenta"},
                {"data": "nombre"},
                {"data": "empresa.siglas"},
                {"data": "id"}
            ],
            columnDefs: [
                {
                    targets: [0],
                    class: 'text-left',
                    searchable: true,
                    render: function (data, type, row) {
                        return data;
                    }
                },
                {
                    targets: [-4, -3],
                    class: 'text-left',
                    orderable: true,
                    render: function (data, type, row) {
                        return data;
                    }
                },
                {
                    targets: [-2],
                    class: 'text-left',
                    orderable: true,
                    render: function (data, type, row) {
                        return data;
                    }
                },
                {
                    targets: [-1],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        if (row.tipo_cuenta === 'GENERAL' || row.tipo_cuenta === 'G' || row.tipo_cuenta === 'GEN') {
                            return '<a rel="neg" class="btn btn-danger btn-xs btn-flat" style="color: white;"><i class="fas fa-times"></i></a> ';
                        }
                        return '<a rel="add" class="btn btn-success btn-xs btn-flat" style="color: white;"><i class="fas fa-plus"></i></a> ';
                    }
                },
            ],
            initComplete: function (settings, json) {
                // Aquí puedes realizar acciones adicionales una vez cargados los datos
            }
        });

        $('#myModalSearchPlan').modal('show');


    });

    $('.btnUpload').on('click', function () {
        $('#myModalUploadXML').modal('show');
    });

    $('#btnAnexoTransac').on('click', function () {
        /*tblSearchPlan = $('#tblSearchPlan').DataTable({
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
            // rowsGroup: [3],
            dom: 'frtip',
            // keys: true,
            keys: {
                focus: ':eq(0)'
            },
            bPaginate: false,
            ordering: false,
            responsive: true,
            autoWidth: false,
            scrollY: "305px",
            destroy: true,
            select: "row",
            autoheight: true,
            autowidth: true,
            /!*view:"treetable",*!/
            ajax: {
                url: window.location.pathname,
                type: 'POST',
                data: {
                    'action': 'search_plan',
                    'ids': JSON.stringify(vents.get_ids())
                },
                dataSrc: ""
            },
            columns: [
                {"data": "codigo", "searchable": true},
                {"data": "tipo_cuenta"},
                {"data": "nombre"},
                {"data": "id"},
            ],
            /!*buttons: [
                /!*{
                    text: 'Button <u>9</u>',
                    key: '9',
                    action: function (e, dt, node, config) {
                        alert('Button 9 activated');
                    }
                },*!/
                /!*{
                    text: 'Button <u><i>shift</i> 9</u>',
                    // key: {
                    //     shiftKey: true,
                    //     key: '9'
                    // },
                    // action: function (e, dt, node, config) {
                    //     alert('Button 9 activated');
                    // }
                }*!/
            ],*!/
            datatype: "xml",
            // aLengthMenu: [
            //     [15, 20, 25, 30, -1],
            //     [15, 20, 25, 30, "All"]
            // ],
            // order : [[0, 'asc']],
            columnDefs: [
                {
                    targets: [0],
                    class: 'text-left',
                    // orderable: true,
                    searchable: true,
                    render: function (data, type, row) {
                        return data;
                    }
                },
                {
                    targets: [-3],
                    // visible: false,
                    class: 'text-left',
                    orderable: true,
                    render: function (data, type, row) {
                        return data;
                    }
                },
                {
                    targets: [-2],
                    class: 'text-left',
                    orderable: true,
                    render: function (data, type, row) {
                        return data;
                    }
                },
                {
                    targets: [-1],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        if (row.tipo_cuenta === 'GENERAL') {
                            return '<a rel="neg" class="btn btn-danger btn-xs btn-flat" style="color: white;"><i class="fas fa-times"></i></a> ';
                        }
                        return '<a rel="add" class="btn btn-success btn-xs btn-flat" style="color: white;"><i class="fas fa-plus"></i></a> ';
                    }
                },
            ],
            initComplete: function (settings, json) {
                // console.log('settings')
                // console.log(settings.aoData)
                /!*$(this).closest('.dataTables_wrapper').find('.dataTables_filter input').val();
                $(this).key()*!/
            }
        });*/
        $('#myModalSearchAnexoTransac').modal('show');
    });

    $('#frmAnextoTransaccional').on('submit', function (event) {
        event.preventDefault();

        /*$.ajax({
            url: window.location.pathname,
            data: {
                'action': 'search_ats',
                'codigo': $('input[name="codigo"]').val(),
                'tip_cuenta': $('select[name="tip_cuenta"]').val(),
                'fecha': $('input[name="fecha"]').val(),
                'descripcion': $('input[name="descripcion"]').val(),
                'comprobante': $('input[name="comprobante"]').val(),
                'direccion': $('textarea[name="direccion"]').val(),
                'comp_fecha_reg': $('input[name="comp_fecha_reg"]').val(),
                'comp_fecha_em': $('input[name="comp_fecha_em"]').val(),
            },
            type: 'POST',
            dataType: 'json',
            success: function (request) {
                console.log('El resultado de request:')
                console.log(request)
                if (!request.hasOwnProperty('error')) {
                    alert('request.comp_fecha_reg')
                    alert(request.comp_fecha_reg)
                    alert('request.comp_fecha_em')
                    alert(request.comp_fecha_em)
                    // location.reload();
                    var newOption = new Option(request.comp_fecha_reg, request.comp_fecha_em, false, true);
                    console.log('newOption')
                    console.log(newOption)
                    $('select[name="cli"]').append(newOption).trigger('change');
                    return false;
                }
                alert(request.error);
            },
            error: function (jqXHR, textStatus, errorThrown) {
                alert(errorThrown + ' ' + textStatus);
            }
        });*/

        var parameters = new FormData(this);
        parameters.append('action', 'search_ats');
        parameters.append('codigo', $('input[name="codigo"]').val());
        parameters.append('tip_cuenta', $('select[name="tip_cuenta"]').val());
        parameters.append('tip_transa', $('select[name="tip_transa"]').val());
        parameters.append('fecha', $('input[name="fecha"]').val());
        parameters.append('descripcion', $('input[name="descripcion"]').val());
        parameters.append('comprobante', $('input[name="comprobante"]').val());
        parameters.append('direccion', $('textarea[name="direccion"]').val());
        parameters.append('reg_ats', 'CON REGISTRO DE ATS');
        console.log(parameters)
        submit_with_ajax(window.location.pathname, 'Notificación', '¿Estas seguro de crear al siguiente ATS?', parameters, function (response) {
            console.log('respuesta: ', response);
            $.confirm({
                theme: 'material',
                title: 'Imprimir ATS',
                icon: 'fa fa-info',
                content: 'Deseas imprmir ats',
                columnClass: 'small',
                typeAnimated: true,
                cancelButtonClass: 'btn-primary',
                draggable: true,
                dragWindowBorder: false,
                buttons: {
                    info: {
                        text: "Si",
                        btnClass: 'btn-primary',
                        action: function () {
                            window.open(response.print_url, '_blank');
                            location.href = '/planCuentas/fact_gasto_bio/listar/';
                            $('#myModalClient').modal('hide');
                            return true;
                        }
                    },
                    danger: {
                        text: "No",
                        btnClass: 'btn-red',
                        action: function () {
                            location.href = '/planCuentas/fact_gasto_bio/listar/';
                            $('#myModalClient').modal('hide');
                            return true;
                        }
                    },
                }
            });
            //$('#myModalClient').modal('hide');
        });

    });

    /*$('#tblSearchPlan').on('search.dt', function () {
        // var value = $('.dataTables_filter input').val();
        var value = $(this).closest('.dataTables_wrapper').find('.dataTables_filter input').val();
        console.log('Valor de value: ',value);
    });*/


    $('#tblSearchPlan')
        /*.on('search.dt', function () {
            // var value = $('.dataTables_filter input').val();
            var value = $(this).closest('.dataTables_wrapper').find('.dataTables_filter input').val();
            alert('Valor de value: '+ value);
        })*/
        /*.on('key-focus', 'tbody tr', function () {
            let data = tblSearchPlan.row(this).data();
            console.log('Valor de data: ','\n', data)
            alert('You clicked on ' + data + "'s row");
        })*/
        /*.on('key-focus key-refocus key-blur change', 'tbody tr', function (e, datatable, cell, originalEvent) {
            var rowData = tblSearchPlan.row(cell.index().row).data();
            alert('Cell in ' + rowData[0] + ' focused');
        })*/
        .on('key-blur', function (e, datatable, cell) {
            alert('No cell selected');
        });

    /*$('#tblSearchPlan').on('draw.dt', function () {
        console.log('Table redrawn');
    });*/

    /*new $.fn.dataTable.KeyTable(tblSearchPlan, {
        // options
    });*/

    $('#tblSearchPlan tbody').on('click', 'a[rel="add"]', function () {
        var tr = tblSearchPlan.cell($(this).closest('td, li')).index();
        var product = tblSearchPlan.row(tr.row).data();
        product.detalle = $('input[name="descripcion"]').val();
        product.debe = 0.00;
        product.haber = 0.00;
        vents.add(product);
        tblSearchPlan.row($(this).parents('tr')).remove().draw();
    });


    $('.btnAdd').on('click', function () {
        console.log('x', this);
        $('#arbol').on('click', function (e) {
            console.log('Se ha seleccionado', this);
        });
    });


    $("select[name='tip_cuenta']").on('change', function () {
        var cuenta = $("select[name='tip_cuenta']").val();
        var fecha = fecha_actual;
        var extraer_mes = fecha.getMonth();
        var mes_exacto = extraer_mes + 1;
        if (cuenta === '1') {

            console.log('entro a DIARIO CONTABLE')
            if (mes_exacto < 10) {
                $('input[name="codigo"]').val('0' + mes_exacto + cuenta)
                $.ajax({
                    url: window.location.pathname,
                    type: 'POST',
                    data: {
                        'action': 'search_cuenta'
                    },
                    dataType: 'json',
                }).done(function (data) {
                    if (!data.hasOwnProperty('error')) {
                        console.log(data);
                        $.each(data, function (key, value) {
                            //console.log(value);
                            /*if (value.categoria === 2) {
                                balanced.push({'id': value.id, 'text': value.nombre});
                            } else {
                                if (value.gramaje != null) {
                                    supplies.push({'id': value.id, 'text': value.nombre});
                                }
                            }*/
                        });
                    }
                }).fail(function (jqXHR, textStatus, errorThrown) {
                    alert(textStatus + ': ' + errorThrown);
                }).always(function (data) {

                });
            } else {
                $('input[name="codigo"]').val(mes_exacto + cuenta)
            }
        } else if (cuenta === '2') {
            console.log('entro a COMPROBANTE PAGO')
            if (mes_exacto < 10) {
                $('input[name="codigo"]').val('0' + mes_exacto + cuenta)
            } else {
                $('input[name="codigo"]').val(mes_exacto + cuenta)
            }
        } else if (cuenta === '3') {
            console.log('entro a INGRESO A CAJA')
            if (mes_exacto < 10) {
                $('input[name="codigo"]').val('0' + mes_exacto + cuenta)
            } else {
                $('input[name="codigo"]').val(mes_exacto + cuenta)
            }
        } else {
            console.log('entro a EGRESO A CAJA')
            if (mes_exacto < 10) {
                $('input[name="codigo"]').val('0' + mes_exacto + cuenta)
            } else {
                $('input[name="codigo"]').val(mes_exacto + cuenta)
            }
        }
    });


    $('#tbl_transaccionPlan tbody')
        .on('click', 'a[rel="remove"]', function () {
            //var tr = tbl_transaccionPlan.cell($(this).closest('td, li')).index();
            // alert('¿Estas seguro de eliminar el producto de tu detalle?');
            // vents.items.products.splice($(this).closest('tr').index(), 1);
            var tr = tbl_transaccionPlan.cell($(this).closest('td, li')).index();
            vents.items.products.splice(tr.row, 1);
            vents.list();
        })
        .on('change', 'input[name="debe"]', function () {
            // console.clear();
            var debe = parseFloat($(this).val());
            var tr = tbl_transaccionPlan.cell($(this).closest('td, li')).index();
            vents.items.products[tr.row].debe = debe;
            vents.calculate_invoice();
            // $('td:eq(5)', tblProducts.row(tr.row).node()).html('$' + vents.items.products[tr.row].subtotal.toFixed(2));
        })
        .on('change', 'input[name="haber"]', function () {
            // console.clear();
            var haber = parseFloat($(this).val());
            var tr = tbl_transaccionPlan.cell($(this).closest('td, li')).index();
            vents.items.products[tr.row].haber = haber;
            vents.calculate_invoice();
            // $('td:eq(5)', tblProducts.row(tr.row).node()).html('$' + vents.items.products[tr.row].subtotal.toFixed(2));
        })
        .on('change', 'input[name="detalle"]', function () {
            // console.clear();
            var detalle = this.val();
            var tr = tbl_transaccionPlan.cell($(this).closest('td, li')).index();
            vents.items.products[tr.row].detalle = detalle;
            vents.calculate_invoice();
            //$('td:eq(-4)', tbl_transaccionPlan.row(tr.row).node()).html('$' + vents.items.products[tr.row].detalle);
        });

    $('#btnSave').on('click', function (event) {
        event.preventDefault();
        var items = tbl_transaccionPlan.rows().data().toArray();
        if ($.isEmptyObject(items)) {
            alerta_error('Debe ingresar al menos un item');
            return false;
        }
        $.ajax({
            url: window.location.pathname,
            data: {
                'action': $('input[name="action"]').val(),
                'codigo': $('input[name="codigo"]').val(),
                'tip_cuenta': $('select[name="tip_cuenta"]').val(),
                'tip_transa': $('select[name="tip_transa"]').val(),
                'fecha': $('input[name="fecha"]').val(),
                'comprobante': $('input[name="comprobante"]').val(),
                'descripcion': $('input[name="descripcion"]').val(),
                'direccion': $('textarea[name="direccion"]').val(),
                'ruc': $('input[name="ruc"]').val(),
                'empresa': $('select[name="empresa"]').val(),
                'reg_ats': $('input[name="reg_ats"]').val(),
                'reg_control': $('input[name="reg_control"]').val(),
                'items': JSON.stringify(items)
            },
            type: 'POST',
            dataType: 'json',
            success: function (request) {
                console.log('request')
                console.log(request)
                console.log("request['pk']")
                console.log(request['pk'])
                $.confirm({
                    theme: 'material',
                    title: 'Generación ATS',
                    icon: 'fa fa-info',
                    content: 'Deseas generar ats',
                    columnClass: 'small',
                    typeAnimated: true,
                    cancelButtonClass: 'btn-primary',
                    draggable: true,
                    dragWindowBorder: false,
                    buttons: {
                        info: {
                            text: "Si",
                            btnClass: 'btn-primary',
                            action: function () {
                                location.href = '/planCuentas/fact_gasto/editar/' + request['pk'];
                                return true;
                            }
                        },
                        danger: {
                            text: "No",
                            btnClass: 'btn-red',
                            action: function () {
                                location.href = '/planCuentas/fact_gasto_bio/listar/';
                                return true;
                            }
                        },
                    }
                });
            },
            error: function (jqXHR, textStatus, errorThrown) {
                alert(errorThrown + ' ' + textStatus);
            }
        });
    });

    $('select[name="search"]').select2({
        theme: "bootstrap4",
        language: 'es',
        allowClear: true,
        ajax: {
            delay: 250,
            type: 'POST',
            url: window.location.pathname,
            data: function (params) {
                console.log('params.term')
                console.log(params.term)
                var queryParameters = {
                    term: params.term,
                    action: 'search_autocomplete',
                    ids: JSON.stringify(vents.get_ids())
                }
                return queryParameters;
            },
            processResults: function (data) {
                return {
                    results: data
                };
            },
        },
        placeholder: 'Ingrese una Cuenta a Buscar',
        minimumInputLength: 1,
        templateResult: formatRepo,
    }).on('select2:select', function (e) {
        var data = e.params.data;
        console.log('DATA DEL SELECT BUSQUEDA')
        console.log(data)
        if (data.tipo_cuenta === 'GENERAL') {
            return false;
        }
        data.detalle = $('input[name="descripcion"]').val();
        data.debe = 0.00;
        data.haber = 0.00;
        vents.add(data);
        $(this).val('').trigger('change.select2');
    });

    vents.list();

});


function calculos_prod(json, debe, haber) {
    deb = debe;
    hab = haber;
    if (deb === hab) {
        console.log('Operacion bien');
        $('input[name="debe_resp"]').val(deb.toFixed(2));
        $('input[name="haber_resp"]').val(hab.toFixed(2));
        $('input[name="proceso"]').val('OPERACION BALANCEADA !CORRECTA!');
        var cal = debe - haber;
        $('input[name="resultado"]').val(cal.toFixed(2));
        document.getElementById("btnSave").disabled = false;
    } else if (hab > deb) {
        console.log('haber mayor al debe');
        $('input[name="debe_resp"]').val(deb.toFixed(2));
        $('input[name="haber_resp"]').val(hab.toFixed(2));
        $('input[name="proceso"]').val('EL HABER ES MAYOR AL DEBE !!!ERROR!!!');
        var cal = haber - debe;
        $('input[name="resultado"]').val(cal.toFixed(2));
        document.getElementById("btnSave").disabled = true;
    } else if (hab < deb) {
        console.log('haber es menor al debe');
        $('input[name="debe_resp"]').val(deb.toFixed(2));
        $('input[name="haber_resp"]').val(hab.toFixed(2));
        $('input[name="proceso"]').val('EL DEBE ES MAYOR AL HABER !!!ERROR!!!');
        var cal = debe - haber;
        $('input[name="resultado"]').val(cal.toFixed(2));
        document.getElementById("btnSave").disabled = true;
    } else {
        console.log('entro por else')
        $('input[name="proceso"]').val('PROCESO A REALIZAR');
    }
}
$(function () {
    listar_dieta();
});

function crear_dieta() {
    $("#modal-default").modal("show");
    $("#titulo_modal_proyecto").text("Nuevo ")
    $("#btn_guardar_proyecto").attr("onclick", "guardar_proyecto()");
    $("#txt_nombre").val("");
    $("#txt_descripcion").val("");
}

function guardar_dieta() {
    var elmForm = $("#frm_dieta");
    if (elmForm) {
        elmForm.validator('validate');
        var elmErr = elmForm.find('.has-error');
        if (elmErr && elmErr.length > 0) {
            peligro("Complete todos los campos del formulario correctamente");
        } else {
            var titulo = $("#txt_nombre").val();
            var descripcion = $("#txt_descripcion").val();
            $("#modal_dieta").modal("hide");
            $.ajax({
                url: '/evaluacion/proyectos/crear/',
                data: {"titulo": titulo, "descripcion": descripcion},
                method: 'post',
                success: function (data) {
                    if (data.hasOwnProperty('estado')) {
                        if (data.estado == "OK") {
                            correcto(data.mensaje);
                            listar_proyecto();
                        }
                    } else {
                        fallo(data.mensaje);
                    }
                    $("#modal_proyecto").modal("hide");
                },
                error: function (jqxhr, data, err) {
                    fallo("Ocurrio un erro inesperado, vuelva a intentarlo")
                    console.log(jqxhr.responseText);
                }
            });
        }
    }
}

function mod_proyecto(proyecto_id) {
    $.ajax({
        url: "/evaluacion/proyectos/obtener/",
        data: {proyecto_id: proyecto_id},
        type: "GET",
        success: function (data) {
            if (data['estado'] == "OK") {
                $("#txt_id_proyecto").val(proyecto_id)
                $("#modal_proyecto").modal("show");
                $("#titulo_modal_proyecto").text("Modificar Proyecto")
                $("#btn_guardar_proyecto").attr("onclick", "modificar_proyecto()");
                $("#txt_descripcion").val(data["descripcion"]);
                $("#txt_nombre").val(data["nombre"])
            } else {
                fallo(data['mensaje']);
            }
        },
        error: function (jhx, error, lol) {
            fallo("Ocurrió un problema durante el proceso, vuelva a intentar");
            console.log(jhx.responseText);
        }
    });
    $("#modal_proyecto").modal("show");
    id_detalle_actividad = id_detalleactividad;
    $("#titulo_modal_proyecto").text("Modificar Proyecto")
    $("#btn_guardar_proyecto").attr("onclick", "add_indicador_accion()");
}


function modificar_proyecto() {
    var elmForm = $("#frm_proyecto");
    if (elmForm) {
        elmForm.validator('validate');
        var elmErr = elmForm.find('.has-error');
        if (elmErr && elmErr.length > 0) {
            peligro("Complete todos los campos del formulario correctamente");
        } else {
            var id = $("#txt_id_proyecto").val();
            var titulo = $("#txt_nombre").val();
            var descripcion = $("#txt_descripcion").val();
            $("#modal_proyecto").modal("hide");
            $.ajax({
                url: '/evaluacion/proyectos/editar/',
                data: {"proyecto_id": id, "titulo": titulo, "descripcion": descripcion},
                method: 'post',
                success: function (data) {
                    if (data.hasOwnProperty('estado')) {
                        if (data.estado == "OK") {
                            correcto(data.mensaje);
                            listar_proyecto();
                        }
                    } else {
                        fallo(data.mensaje);
                    }
                    $("#modal_proyecto").modal("hide");
                },
                error: function (jqxhr, data, err) {
                    fallo("Ocurrio un erro inesperado, vuelva a intentarlo")
                    console.log(jqxhr.responseText);
                }
            });
        }
    }
}


function listar_dieta() {
    $.ajax({
        url: '/dieta/dieta/principal/',
        method: 'get',
        success: function (data) {
            alert('aquiiiii BRYAN');
            console.log(data)
            var tabla1 = '';
            $("#listar_dietas").empty();
            for (var i = 0; i < data['dieta'].length; i++) {
                tabla1 += `
                <div class="col-sm-3">
                    <div class="position-relative p-3 bg-gray" style="height: 180px">
                        ${data['dieta'][i]['mes_dieta']}<br/>
                        <small>Todas las Dietas de Febrero ${data['dieta'][i]['descripcion']}</small>
                    </div>
                </div>
                `
            }
            $('#listar_dietas').append(tabla1);
        },
        error: function (jqxhr, data, err) {
            alert(jqxhr.responseText);
        }
    });
}

function eliminar_proyecto(proyecto_id) {
    swal({
            title: "Eliminar Proyecto",
            text: "Está seguro de eliminar este proyecto",
            type: "warning",
            showCancelButton: true,
            cancelButtonText: "Cancelar",
            confirmButtonText: "Aceptar",
            closeOnConfirm: false,
            showLoaderOnConfirm: true
        },
        function () {
            $.ajax({
                url: "/evaluacion/proyectos/eliminar/",
                data: {proyecto_id: proyecto_id},
                type: "POST",
                success: function (data) {
                    $("#my_dialog").modal("hide");
                    if (data['estado'] == "OK") {
                        listar_proyecto();
                        correcto(data['mensaje']);
                        swal.close()
                    } else {
                        fallo(data['mensaje']);
                        swal.close()
                    }
                },
                error: function (jhx, error, lol) {
                    fallo("Ocurrió un problema durante el proceso, vuelva a intentar");
                    console.log(jhx.responseText);
                }
            });
        });
}


function print_proyecto(proyecto_id) {
    window.open('/evaluacion/proyectos/imprimir/' + proyecto_id + '/', '_blank');
}





$(document).ready(function () {
    listar_dieta();
});

function listar_dieta() {
    $.ajax({
        url: '/dieta/dieta/listar/dia/',
        method: 'get',
        success: function (data) {
            console.log(data)
            var tabla1 = '';
            $("#tblProducts").empty();
            for (var i = 0; i < data['dieta'].length; i++) {
                tabla1 += `
                <div class="col-sm-3">
                    <div class="position-relative p-3 bg-gray" style="height: 180px">
                        ${data['dieta'][i]['insuno1']}<br/>
                        <small>Todas las Dietas de Febrero ${data['dieta'][i]['gran1']}</small>
                    </div>
                </div>
                `
            }
            $('#tblProducts').append(tabla1);
        },
        error: function (jqxhr, data, err) {
            alert(jqxhr.responseText);
        }
    });
}
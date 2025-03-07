function validateExt() {
    var ext = $('input[name="archive"]').val().split('.').pop().toLowerCase();
    return $.inArray(ext, ['xls', 'xlsx']) !== -1;
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
                            message: 'Introduce un archivo en formato excel',
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
            parameters.append('action', 'upload_excel');
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
                        Swal.fire({
                            position: 'top-center',
                            icon: 'success',
                            title: 'Registro ingresado correctamente',
                            showConfirmButton: false,
                            timer: 1500
                        });
                        location.href = '/dieta/listar/anio/';
                        return false;
                    }
                    message_error(request.error);
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    message_error(errorThrown + ' ' + textStatus);
                }
            });
            alert_sweetalert('success', 'Alerta', 'Productos actualizados correctamente', function () {
                location.reload();
            }, 2000, null);
        });
});

$(function () {
    $('.btnUpload').on('click', function () {
        $('#myModalUploadExcel').modal('show');
    });
});

(function ($) {
    "use strict";

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    var csrftoken = window.csrftoken || getCookie('csrftoken');

    $(function () {

        console.log('[form.js] cargado');

        $('select[name="cod_contable"]').select2({
            theme: "bootstrap4",
            language: 'es',
            allowClear: true,
            ajax: {
                delay: 250,
                type: 'POST',
                url: window.location.pathname,
                data: function (params) {
                    return {
                        term: params.term,
                        action: 'search_clients'
                    };
                },
                processResults: function (data) {
                    return { results: data };
                },
            },
            placeholder: 'Ingrese una descripción',
            minimumInputLength: 1,
        });

        $('.btnAddClient').on('click', function () {
            $('#myModalClient').modal('show');
        });

        $('#myModalClient').on('hidden.bs.modal', function () {
            $('#frmClient').trigger('reset');
        });

        $('#frmClient').on('submit', function (e) {
            e.preventDefault();
            var parameters = new FormData(this);
            parameters.append('action', 'create_client');
            submit_with_ajax(window.location.pathname, 'Notificación',
                '¿Estas seguro de crear al siguiente proveedor?', parameters, function (response) {
                    var newOption = new Option(response.full_name_total, response.id, false, true);
                    $('select[name="cod_contable"]').append(newOption).trigger('change');
                    $('#myModalClient').modal('hide');
                });
        });

        var input_ruc = $('input[name="ruc"]');
        var btn_search_ruc = $('.btnSearchRUCInSRI');

        btn_search_ruc.on('click', function (e) {
            e.preventDefault();
            var ruc_value = input_ruc.val() ? input_ruc.val().trim() : '';

            if (!ruc_value) {
                Swal.fire({
                    icon: 'warning',
                    title: 'RUC vacío',
                    text: 'Ingrese un RUC antes de buscar.',
                });
                return;
            }

            btn_search_ruc.prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> Buscando...');

            $.ajax({
                url: window.location.pathname,
                type: 'POST',
                data: { action: 'search_ruc_in_sri', ruc: ruc_value },
                headers: { 'X-CSRFToken': csrftoken },
                dataType: 'json',
                timeout: 20000,
            })
            .done(function (request) {
                if (!request) return;

                if (request.error) {
                    Swal.fire('Error', request.error, 'error');
                    return;
                }

                $('input[name="ruc"]').val(request.numeroRuc || '');
                $('input[name="razon_soc"]').val(request.razonSocial || '');
                $('input[name="nombre_com"]').val(request.nombreComercial || request.razonSocial || '');
                $('input[name="actividad_com"]').val(request.actividadEconomicaPrincipal || '');
                $('input[name="estado"]').val(request.estadoContribuyenteRuc || '');

                if (request.establecimientos && request.establecimientos.length > 0) {
                    var matriz = request.establecimientos.find(function (ee) {
                        return ee.matriz === true || (typeof ee.matriz === 'string' && ee.matriz.toUpperCase() === 'SI');
                    });
                    if (!matriz) {
                        matriz = request.establecimientos[0];
                    }
                    $('input[name="direccion1"]').val(matriz.direccionCompleta || '');
                    $('input[name="ciudad"]').val(matriz.provincia || matriz.ciudad || '');
                }

                var content = '<h5><strong>Información del RUC</strong></h5>';
                content += '<table class="table table-sm table-bordered">';
                content += '<tr><th>RUC</th><td>' + (request.numeroRuc || '') + '</td></tr>';
                content += '<tr><th>Razón Social</th><td>' + (request.razonSocial || '') + '</td></tr>';
                content += '<tr><th>Nombre Comercial</th><td>' + (request.nombreComercial || request.razonSocial || '') + '</td></tr>';
                content += '<tr><th>Estado</th><td>' + (request.estadoContribuyenteRuc || '') + '</td></tr>';
                content += '<tr><th>Tipo Contribuyente</th><td>' + (request.tipoContribuyente || '') + '</td></tr>';
                content += '<tr><th>Actividad Principal</th><td>' + (request.actividadEconomicaPrincipal || '') + '</td></tr>';
                content += '<tr><th>Agente Retención</th><td>' + (request.agenteRetencion || '') + '</td></tr>';
                content += '<tr><th>Contribuyente Especial</th><td>' + (request.contribuyenteEspecial || '') + '</td></tr>';
                content += '<tr><th>Obligado a llevar contabilidad</th><td>' + (request.obligadoLlevarContabilidad || '') + '</td></tr>';
                content += '<tr><th>Regimen</th><td>' + (request.regimen || '') + '</td></tr>';

                var f = request.informacionFechasContribuyente || {};
                content += '<tr><th>Fecha Inicio Actividades</th><td>' + (f.fechaInicioActividades || '') + '</td></tr>';
                content += '<tr><th>Fecha Cese</th><td>' + (f.fechaCese || '') + '</td></tr>';
                content += '<tr><th>Fecha Reinicio</th><td>' + (f.fechaReinicioActividades || '') + '</td></tr>';
                content += '<tr><th>Última Actualización</th><td>' + (f.fechaActualizacion || '') + '</td></tr>';
                content += '</table>';

                if (request.representantesLegales && request.representantesLegales.length) {
                    content += '<br>';
                    content += '<h5><strong>Representante Legal</strong></h5>';
                    content += '<table class="table table-sm table-bordered">';
                    content += '<tr><th>Identificación</th><th>Nombre</th></tr>';
                    request.representantesLegales.forEach(function (r) {
                        content += '<tr><td>' + (r.identificacion || '') + '</td><td>' + (r.nombre || '') + '</td></tr>';
                    });
                    content += '</table>';
                }

                if (request.establecimientos && request.establecimientos.length) {
                    content += '<br>';
                    content += '<h5><strong>Establecimientos</strong></h5>';
                    content += '<table class="table table-sm table-bordered">';
                    content += '<tr><th>Número</th><th>Tipo</th><th>Dirección</th><th>Estado</th><th>Matriz</th></tr>';
                    request.establecimientos.forEach(function (e, idx) {
                        content += '<tr>' +
                            '<td>' + String(idx + 1).padStart(3, '0') + '</td>' +
                            '<td>' + (e.tipoEstablecimiento || '') + '</td>' +
                            '<td>' + (e.direccionCompleta || '') + '</td>' +
                            '<td>' + (e.estado || '') + '</td>' +
                            '<td>' + ((e.matriz === true || (typeof e.matriz === 'string' && e.matriz.toUpperCase() === 'SI')) ? 'SI' : 'NO') + '</td>' +
                            '</tr>';
                    });
                    content += '</table>';
                }

                $('#sri_result_summary').html(content);
                $('#myModalRUC').modal('show');

            })
            .fail(function (jqXHR, textStatus, errorThrown) {
                Swal.fire('Error', 'No se pudo consultar el RUC: ' + (errorThrown || textStatus), 'error');
            })
            .always(function () {
                btn_search_ruc.prop('disabled', false).html('<i class="fas fa-search"></i> Buscar RUC en el SRI');
            });

        });

    });

})(jQuery);

/*
  form.js - completo y con debug para Buscar RUC en SRI
  Reemplaza todo el contenido actual por este archivo.
*/

(function ($) {
    "use strict";

    // helper: lee cookie csrftoken si no existe la variable global csrftoken
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // asegurarnos csrftoken
    var csrftoken = window.csrftoken || getCookie('csrftoken');

    $(function () {

        console.log('[form.js] cargado - iniciando script');

        // --- SELECT2: Buscar plan contable (tu código existente) ---
        $('select[name="cod_contable"]').select2({
            theme: "bootstrap4",
            language: 'es',
            allowClear: true,
            ajax: {
                delay: 250,
                type: 'POST',
                url: window.location.pathname,
                data: function (params) {
                    var queryParameters = {
                        term: params.term,
                        action: 'search_clients'
                    };
                    return queryParameters;
                },
                processResults: function (data) {
                    return {
                        results: data
                    };
                },
            },
            placeholder: 'Ingrese una descripción',
            minimumInputLength: 1,
        });

        // --- Modal para crear plan contable desde proveedor ---
        $('.btnAddClient').on('click', function () {
            $('#myModalClient').modal('show');
        });

        $('#myModalClient').on('hidden.bs.modal', function (e) {
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

        // --- BOTÓN BUSCAR RUC EN EL SRI ---
        var input_ruc = $('input[name="ruc"]'); // debe existir name="ruc"
        var btn_search_ruc = $('.btnSearchRUCInSRI');

        // debug: mostrar si los elementos fueron localizados
        console.log('[form.js] input_ruc.length =', input_ruc.length);
        console.log('[form.js] btn_search_ruc.length =', btn_search_ruc.length);

        btn_search_ruc.on('click', function (e) {
            e.preventDefault();
            console.log('[form.js] click en Buscar RUC');

            var ruc_value = input_ruc.val() ? input_ruc.val().trim() : '';
            console.log('[form.js] ruc_value =', ruc_value);

            if (!ruc_value) {
                // mensaje rápido
                Swal.fire({
                    icon: 'warning',
                    title: 'RUC vacío',
                    text: 'Ingrese un RUC antes de buscar.',
                });
                return;
            }

            // mostrar carga
            btn_search_ruc.prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> Buscando...');

            $.ajax({
                url: window.location.pathname,
                type: 'POST',
                data: {
                    'action': 'search_ruc_in_sri',
                    'ruc': ruc_value
                },
                headers: {
                    'X-CSRFToken': csrftoken
                },
                dataType: 'json',
                timeout: 20000,
            })
            .done(function (request) {
                console.log('[form.js] AJAX done:', request);

                // si la vista devuelve {'error': '...'} o similar
                if (request && request.hasOwnProperty('error')) {
                    console.warn('[form.js] respuesta con error:', request.error);
                    message_error(request.error || 'Error en la consulta');
                    return;
                }

                // Caso normal: request contiene el objeto con claves SRI
                // comprobamos que tenga numeroRuc o razonSocial
                var info = request || {};

                // Si tu vista envolvía en {data: {...}} ajusta: var info = request.data || request;
                // ejemplo: var info = request.data ? request.data : request;

                // Autocompletar campos del formulario Proveedor
                $('input[name="razon_soc"]').val(info.razonSocial || '');
                $('input[name="nombre_com"]').val(info.razonSocial || '');
                $('input[name="actividad_com"]').val(info.actividadEconomicaPrincipal || '');

                if (info.establecimientos && info.establecimientos.length > 0) {
                    $('input[name="direccion1"]').val(info.establecimientos[0].direccionCompleta || '');
                }

                // si el SRI devuelve telefonos o correos en el futuro, puedes mapear aquí
                // $('input[name="telef1"]').val(info.telefono || '');
                // $('input[name="mail"]').val(info.correo || '');

                // mostrar resumen en pantalla (opcional)
                var summary = '<strong>RUC:</strong> ' + (info.numeroRuc || 'N/A') + '<br>' +
                              '<strong>Razón Social:</strong> ' + (info.razonSocial || 'N/A') + '<br>' +
                              '<strong>Actividad:</strong> ' + (info.actividadEconomicaPrincipal || 'N/A');

                $('#sri_result_summary').html(summary).show();

                console.log('[form.js] campos autocompletados OK');
            })
            .fail(function (jqXHR, textStatus, errorThrown) {
                console.error('[form.js] AJAX fail:', textStatus, errorThrown, jqXHR);
                var msg = 'Error en la consulta: ' + (errorThrown || textStatus);
                message_error(msg);
            })
            .always(function () {
                btn_search_ruc.prop('disabled', false).html('<i class="fas fa-search"></i> Buscar RUC en el SRI');
            });
        });

    }); // end ready

})(jQuery);

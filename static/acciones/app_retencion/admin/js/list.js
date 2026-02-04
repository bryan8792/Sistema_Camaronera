var tblRetention;

$(function () {

    tblRetention = $('#tblRetention').DataTable({
        ajax: {
            url: window.location.pathname,
            type: 'POST',
            data: { action: 'searchdata' },
            dataSrc: ""
        },
        columns: [
            { data: "id" },
            { data: "voucher_number_full" },
            { data: "provider" },
            { data: "date_joined" },
            { data: "total_retained" },
            { data: null }, // ESTADO
            { data: null }  // OPCIONES
        ],
        columnDefs: [

            // ===== ESTADO =====
            {
                targets: 5,
                className: 'text-center',
                render: function (data, type, row) {

                    if (row.email_sent === true) {
                        return '<span class="badge badge-success">AUTORIZADO / ENVIADO</span>';
                    }

                    if (row.pdf && row.xml) {
                        return '<span class="badge badge-info">AUTORIZADO</span>';
                    }

                    return '<span class="badge badge-warning">PENDIENTE</span>';
                }
            },

            // ===== OPCIONES =====
            {
                targets: -1,
                className: 'text-center',
                orderable: false,
                render: function (data, type, row) {

                    let html = '<div class="btn-group">';

                    if (row.pdf) {
                        html += `
                        <a href="${row.pdf}" target="_blank"
                           class="btn btn-danger btn-sm" title="PDF">
                           <i class="fas fa-file-pdf"></i>
                        </a>`;
                    }

                    if (row.xml) {
                        html += `
                        <a href="${row.xml}" target="_blank"
                           class="btn btn-success btn-sm" title="XML">
                           <i class="fas fa-file-code"></i>
                        </a>`;
                    }

                    if (!row.email_sent) {
                        html += `
                        <button type="button"
                                class="btn btn-primary btn-sm"
                                data-action="send-email"
                                data-id="${row.id}"
                                title="Enviar por email">
                            <i class="fas fa-envelope"></i>
                        </button>`;
                    }

                    html += '</div>';
                    return html;
                }
            }
        ]
    });

    // ===== ENVIAR POR EMAIL =====
    $('#tblRetention').on('click', 'button[data-action="send-email"]', function () {

        let id = $(this).data('id');

        Swal.fire({
            title: '¿Enviar comprobante?',
            text: 'Se enviará el comprobante por correo electrónico',
            icon: 'question',
            showCancelButton: true,
            confirmButtonText: 'Sí, enviar',
            cancelButtonText: 'Cancelar'
        }).then((result) => {

            if (result.isConfirmed) {

                let params = new FormData();
                params.append('action', 'send_retention_by_email');
                params.append('id', id);

                $.ajax({
                    url: window.location.pathname,
                    type: 'POST',
                    data: params,
                    processData: false,
                    contentType: false,
                    success: function (response) {

                        if (response.success) {
                            Swal.fire({
                                icon: 'success',
                                title: 'Enviado',
                                text: response.message,
                                timer: 2500,
                                showConfirmButton: false
                            });

                            // 🔥 RECARGA TABLA Y CAMBIA A VERDE
                            tblRetention.ajax.reload(null, false);
                        } else {
                            Swal.fire('Error', response.error, 'error');
                        }
                    },
                    error: function () {
                        Swal.fire('Error', 'No se pudo enviar el correo', 'error');
                    }
                });
            }
        });
    });

});

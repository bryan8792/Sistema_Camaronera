$(document).ready(function() {
    $('#tb_usuario').DataTable({
        responsive: true,
        autoWidth: false,
        destroy: true,
        deferRender: true,
        ajax: {
            url: window.location.pathname,
            type: 'POST',
            data: {
                'action': 'searchdata'
            },
            dataSrc: "",
            headers: {
                'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
            }
        },
        columns: [
            {
                "data": "id",
                "className": "text-center"
            },
            {
                "data": "username"
            },
            {
                "data": null,
                "render": function(data, type, row) {
                    var firstName = row.first_name || '';
                    var lastName = row.last_name || '';
                    var fullName = (firstName + ' ' + lastName).trim();
                    return fullName || 'Sin nombre';
                }
            },
            {
                "data": "email"
            },
            {
                "data": "date_joined",
                "render": function(data, type, row) {
                    if (data) {
                        var date = new Date(data);
                        return date.toLocaleDateString('es-ES');
                    }
                    return 'N/A';
                }
            },
            {
                "data": "is_active",
                "className": "text-center",
                "render": function(data, type, row) {
                    if (data) {
                        return '<span class="badge badge-success"><i class="fas fa-check mr-1"></i>Activo</span>';
                    } else {
                        return '<span class="badge badge-danger"><i class="fas fa-times mr-1"></i>Inactivo</span>';
                    }
                }
            },
            {
                "data": null,
                "orderable": false,
                "className": "text-center",
                "render": function(data, type, row) {
                    var buttons = '<div class="btn-group" role="group">';
                    buttons += '<a href="/usuario/usuario/actualizar/' + row.id + '/" class="btn btn-warning btn-sm" title="Editar">';
                    buttons += '<i class="fas fa-edit"></i>';
                    buttons += '</a>';
                    buttons += '<a href="/usuario/usuario/detail/' + row.id + '/" class="btn btn-info btn-sm" title="Ver">';
                    buttons += '<i class="fas fa-eye"></i>';
                    buttons += '</a>';
                    buttons += '<a href="/usuario/usuario/eliminar/' + row.id + '/" class="btn btn-danger btn-sm" title="Eliminar">';
                    buttons += '<i class="fas fa-trash"></i>';
                    buttons += '</a>';
                    buttons += '</div>';
                    return buttons;
                }
            }
        ],
        language: {
            "decimal": "",
            "emptyTable": "No hay información disponible",
            "info": "Mostrando _START_ a _END_ de _TOTAL_ registros",
            "infoEmpty": "Mostrando 0 a 0 de 0 registros",
            "infoFiltered": "(filtrado de _MAX_ registros totales)",
            "infoPostFix": "",
            "thousands": ",",
            "lengthMenu": "Mostrar _MENU_ registros por página",
            "loadingRecords": "Cargando...",
            "processing": "Procesando...",
            "search": "Buscar:",
            "zeroRecords": "No se encontraron registros coincidentes",
            "paginate": {
                "first": "Primero",
                "last": "Último",
                "next": "Siguiente",
                "previous": "Anterior"
            },
            "aria": {
                "sortAscending": ": activar para ordenar la columna ascendente",
                "sortDescending": ": activar para ordenar la columna descendente"
            }
        }
    });
});

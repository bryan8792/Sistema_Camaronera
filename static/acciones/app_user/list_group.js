function getData() {
    $('#tb_grupo').DataTable({
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
            dataSrc: ""
        },
        columns: [
            {"data": "id"},
            {"data": "name"},
            {"data": "users_count"},
            {"data": "permissions_count"},
            {
                "data": "modulos",
                "render": function(data, type, row) {
                    var badges = '';
                    data.forEach(function(modulo) {
                        badges += '<span class="badge badge-info mr-1">' + modulo + '</span>';
                    });
                    return badges;
                }
            },
            {
                "data": null,
                "render": function(data, type, row) {
                    var buttons = '<div class="btn-group">';
                    buttons += '<a href="/grupo/detail/' + row.id + '/" class="btn btn-info btn-sm" title="Ver"><i class="fas fa-eye"></i></a>';
                    buttons += '<a href="/grupo/actualizar/' + row.id + '/" class="btn btn-warning btn-sm" title="Editar"><i class="fas fa-edit"></i></a>';
                    buttons += '<a href="/grupo/eliminar/' + row.id + '/" class="btn btn-danger btn-sm" title="Eliminar"><i class="fas fa-trash"></i></a>';
                    buttons += '</div>';
                    return buttons;
                }
            }
        ],
        columnDefs: [
            {
                targets: [-1],
                class: 'text-center',
                orderable: false,
            }
        ],
        initComplete: function(settings, json) {
            // Código adicional si es necesario
        }
    });
}

$(document).ready(function() {
    getData();
});
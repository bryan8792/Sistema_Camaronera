$(function () {
    $('#tb_usuario').DataTable({
        responsive: true,
        autoWidth: false,
        destroy: true,
        deferRender: true,
        ajax: {
            url: window.location.pathname,
            type: 'POST',
            headers: {
                'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val()
            },
            data: { action: 'searchdata' },
            dataSrc: ""
        },
        columns: [
            { data: 'id' },
            { data: 'username' },
            { data: 'full_name' },
            { data: 'email' },
            {
                data: 'groups',
                render: function (data, type, row) {
                    if (data.length === 0) return '<span class="text-muted">Sin grupo</span>';
                    return data.map(g => `<span class="badge badge-info mr-1">${g.name}</span>`).join('');
                }
            },
            { data: 'last_login' },
            {
                data: null,
                className: "text-center",
                render: function (data, type, row) {
                    return `
                        <a href="/usuario/usuario/detail/${row.id}/" class="btn btn-info btn-sm"><i class="fas fa-eye"></i></a>
                        <a href="/usuario/usuario/actualizar/${row.id}/" class="btn btn-warning btn-sm"><i class="fas fa-edit"></i></a>
                        <a href="/usuario/usuario/eliminar/${row.id}/" class="btn btn-danger btn-sm"><i class="fas fa-trash"></i></a>
                    `;
                }
            }
        ]
    });
});

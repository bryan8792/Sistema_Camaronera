var tblProducts_bio;
var vents = {
    items: {
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
        alert(item)
        this.items.products.push(item);
        this.list();
    },
    list: function () {
        tblProducts_bio = $('#tblProducts_bio').DataTable({
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
            autoWidth: false,
            dom: 'Brtip',
            bPaginate: false,
            scrollY: "700px",
            scrollX: true,
            destroy: true,
            data: this.items.products,
            columns: [
                {"data": "fecha_ingreso"},
                {"data": "producto_empresa.nombre_prod.nombre"},
                {"data": "cantidad_ingreso"},
                {"data": "cantidad_egreso"},
                {"data": "id"},
            ],
            columnDefs: [
            {
                targets: [0, 1, 2, 3, 4],
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    return data;
                }
            },
        ],
            rowCallback: function (row, data, index) {

            },
            initComplete: function (settings, json) {

            }
        });
    }
}


$(function () {

    $('input[name="search"]').autocomplete({
        source: function (request, response) {
            alert('LLEGO A BIO')
            $.ajax({
                url: window.location.pathname,
                type: 'POST',
                data: {
                    'action': 'search_autocomplete_bio',
                    'term': request.term,
                    'empresa': 'BIO'
                },
                dataType: 'json'
            }).done(function (data) {
                response(data);
            }).fail(function (jqXHR, textStatus, errorThrown) {

            }).always(function (data) {

            });
        },
        delay: 580,
        minLength: 4,
        select: function (event, ui) {
            event.preventDefault();
            console.clear();
            console.log(vents.items);
            console.log(ui);
            vents.add(ui.item);
            $(this).val('');
        }
    });

    vents.list();
});

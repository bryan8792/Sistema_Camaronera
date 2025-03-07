$(function () {
    $('#tblProducts').DataTable({
        responsive: true,
        autowidth:false,
        destroy:true,
        ajax:{
        url: '/dieta/dieta/listar/dia/',
        type: 'get',
        data:{},
        dataSrc:""
        },
        columns:[
            {"data":"id"},
            {"data":"fecha.fecha"},
            {"data":"piscinas.numero"},
            {"data":"balanceado.nombre"},
            {"data":"balan_lb"},
            {"data":"insuno_1"},
            {"data":"gramaj_1"},
            {"data":"insuno_2"},
            {"data":"gramaj_2"},
            {"data":"insuno_3"},
            {"data":"gramaj_3"},
            {"data":"insuno_4"},
            {"data":"gramaj_4"},
        ],
        columnDefs: [
            {
                targets:[2],
                class:'text-center',
                orderable:false
            }
        ],
        initComplete: function (settings, json) {

        }
    });
});

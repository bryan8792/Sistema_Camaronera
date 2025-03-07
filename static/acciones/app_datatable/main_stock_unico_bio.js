var tblProducts;
var total_eg;
var total_stock = 0;
var tabla = {
    list: function () {
        tblProducts = $('#tb_stock_unico_bio').DataTable({
            language: {
                "oPaginate": {
                    "sFirst": "Primero",
                    "sLast": "Último",
                    "sNext": "Siguiente",
                    "sPrevious": "Anterior"
                },
                "zeroRecords": "Ningun dato disponible en esta tabla",
                "sInfo": "Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros",
                "infoEmpty": "Tabla vacia por favor inserte datos",
                "lengthMenu": "Listando _MENU_ registros",
                "sSearch": "Buscar:",
                "infoFiltered": "(filtrado de _MAX_ registros totales)"
            },
            bPaginate: false,
            responsive: true,
            autoWidth: false,
            scrollY: "600px",
            scrollX: true,
            //dom: 'Bfrtilp',
            bJQueryUI: true,
            dom: 'Bfrtip',
            destroy: true,
            deferRender: true,
            buttons: [
                {
                    extend: 'pdfHtml5',
                    text: '<i class="fas fa-file-pdf"></i> ',
                    titleAttr: 'Exportar a PDF',
                    className: 'btn btn-danger'
                },
                {
                    extend: 'print',
                    text: '<i class="fa fa-print"></i> ',
                    titleAttr: 'Imprimir',
                    className: 'btn btn-info'
                },
                {
                    extend: 'copyHtml5',
                    text: '<i class="fas fa-copy"></i> ',
                    titleAttr: 'Copiar Datos',
                    className: 'btn btn-secondary'
                },
                {
                    extend: 'csvHtml5',
                    text: '<i class="fas fa-file-csv"></i> ',
                    titleAttr: 'Exportar a CSV',
                    className: 'btn btn-success'
                }
            ],
            footerCallback: function (row, data, index) {

                total_ing = this.api()
                    .column(3)//numero de columna a sumar
                    //.column(3, {page: 'current'})//para sumar solo la pagina actual
                    .data()
                    .reduce(function (a, b) {
                        return parseInt(a) + parseInt(b);
                    }, 0);
                $(this.api().column(3).footer()).html('' + total_ing);

                total_eg = this.api()
                    .column(4)//numero de columna a sumar
                    //.column(4, {page: 'current'})//para sumar solo la pagina actual
                    .data()
                    .reduce(function (a, b) {
                        return parseInt(a) + parseInt(b);
                    }, 0);

                $(this.api().column(4).footer()).html('' + total_eg);

                $(this.api().column(5).footer()).html('' + total_ing - total_eg);
            },
            rowCallback: function (row, data, index) {
                //pintar una celda
                console.log('----------------------------------------------------------------------------------------------')
                let contador = 0;
                for (let i = index; i <= index; i++) {
                    contador = (i - 1);
                    if (index > contador) {
                        console.log('Index : ' + i)
                        console.log('Contador -1 a Index : ' + contador)
                        console.log(data[3] + ' - ' + data[4])
                        cantidad_ingreso = parseFloat(data[3])
                        cantidad_egreso = parseFloat(data[4])
                        console.log('total : ' + total_stock);

                        if (cantidad_ingreso > 0) {
                            console.log('entro a ingreso');
                            total_stock += cantidad_ingreso;
                            $('td', row).eq(5).css({'background-color': '#5f9ea0', 'color': 'white',});
                        } else {
                            console.log('entro a egreso');
                            total_stock -= cantidad_egreso;
                            $('td', row).eq(5).css({'background-color': '#f08080', 'color': 'white',});
                        }
                        console.log('nuevo total '+ total_stock);

                        $('td', row).eq(5).html('<b>' + total_stock.toFixed(0) +'</b>');
                    }

                }
            }
        });

    }
};


$(function () {
    tabla.list();
});
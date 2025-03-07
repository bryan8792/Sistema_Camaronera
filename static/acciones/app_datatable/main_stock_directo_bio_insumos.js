$(document).ready(function() {    
    $('#tb_stock_directo_insumo_bio').DataTable({
        language: {
                "lengthMenu": "Mostrar _MENU_ registros",
                "zeroRecords": "No se encontraron resultados",
                "info": "Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros",
                "infoEmpty": "Mostrando registros del 0 al 0 de un total de 0 registros",
                "infoFiltered": "(filtrado de un total de _MAX_ registros)",
                "sSearch": "Buscar:",
                "oPaginate": {
                    "sFirst": "Primero",
                    "sLast":"Último",
                    "sNext":"Siguiente",
                    "sPrevious": "Anterior"
			     },
			     "sProcessing":"Procesando...",
            },
		 columnDefs: [{
			orderable: false,
			targets: [0,1,2,3]
		}],
        // autoWidth: false,
		// scrollY: "580px",
		// scrollCollapse: false,
		// paging: false,
        // //para usar los botones
        // responsive: "true",
        //dom: 'Bfrtilp',
		dom: 'Bfrtip',
        buttons:[ 
			{
				extend:    'excelHtml5',
				text:      '<i class="fas fa-file-excel"></i> ',
				titleAttr: 'Exportar a Excel',
				className: 'btn btn-success'
			},
			{
				extend:    'pdfHtml5',
				text:      '<i class="fas fa-file-pdf"></i> ',
				titleAttr: 'Exportar a PDF',
				className: 'btn btn-danger'
			},
			{
				extend:    'print',
				text:      '<i class="fa fa-print"></i> ',
				titleAttr: 'Imprimir',
				className: 'btn btn-info'
			},
			{
				extend:    'copyHtml5',
				text:      '<i class="fas fa-copy"></i> ',
				titleAttr: 'Copiar Datos',
				className: 'btn btn-secondary'
			},
			{
				extend:    'csvHtml5',
				text:      '<i class="fas fa-file-csv"></i> ',
				titleAttr: 'Exportar a CSV',
				className: 'btn btn-success'
			},
		]	        
    });     
});
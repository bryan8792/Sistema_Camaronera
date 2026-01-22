var moment = window.moment
var $ = window.jQuery

var date_range = null
var tb_piscinas_por_insumos = null
var date_now = moment().format("YYYY-MM-DD")

function generate_report_piscinas() {
  var parameters = {
    action: "search_insumos_conglomerado_bio_linea",
    start_date: date_now,
    end_date: date_now,
  }

  if (date_range !== null) {
    parameters["start_date"] = date_range.startDate.format("YYYY-MM-DD")
    parameters["end_date"] = date_range.endDate.format("YYYY-MM-DD")
  }

  // Destruir tabla existente si existe
  if (tb_piscinas_por_insumos !== null) {
    tb_piscinas_por_insumos.destroy()
    $("#insumos_conglomerado_psm tbody").empty()
  }

  // Hacer petición AJAX para obtener datos
  $.ajax({
    url: window.location.pathname,
    type: "POST",
    data: parameters,
    dataType: "json",
    success: (json) => {
      var groupedData = {}

      json.forEach((valor) => {
        // Obtener linea y sublinea
        var linea = valor.producto_empresa.nombre_prod.categoria.nombre
        var sublinea = valor.producto_empresa.nombre_prod.descripcion.nombre
        var costo = Number.parseFloat(valor.producto_empresa.nombre_prod.costo_aplicacion)
        var cantidad = Number.parseFloat(valor.cantidad_egreso)

        // Crear clave única combinando linea + sublinea
        var key = linea + "|" + sublinea

        if (!groupedData[key]) {
          groupedData[key] = {
            linea: linea,
            sublinea: sublinea,
            cantidad: 0,
            total: 0,
          }
        }

        // Sumar cantidad y calcular total
        groupedData[key].cantidad += cantidad
        groupedData[key].total += cantidad * costo
      })

      // Convertir objeto agrupado a array y preparar datos para DataTable
      var tableData = []
      var totalCantidad = 0
      var totalMonto = 0

      Object.values(groupedData).forEach((item) => {
        totalCantidad += item.cantidad
        totalMonto += item.total

        tableData.push({
          linea: item.linea,
          sublinea: item.sublinea,
          cantidad: item.cantidad,
          // Calcular costo promedio: total / cantidad (evitar división por cero)
          costo: item.cantidad > 0 ? item.total / item.cantidad : 0,
          total: item.total,
        })
      })

      // Actualizar totales en el footer
      $("#total_cantidad").text(totalCantidad.toFixed(2))
      $("#total_monto").text(totalMonto.toFixed(2))

      // Inicializar DataTable con los datos procesados
      tb_piscinas_por_insumos = $("#insumos_conglomerado_psm").DataTable({
        data: tableData,
        destroy: true,
        lengthChange: false,
        autoWidth: false,
        language: {
          lengthMenu: "Mostrar _MENU_ registros",
          zeroRecords: "No se encontraron resultados",
          info: "Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros",
          infoEmpty: "Mostrando registros del 0 al 0 de un total de 0 registros",
          infoFiltered: "(filtrado de un total de _MAX_ registros)",
          sSearch: "Buscar:",
          oPaginate: {
            sFirst: "Primero",
            sLast: "Último",
            sNext: "Siguiente",
            sPrevious: "Anterior",
          },
          sProcessing: "Procesando...",
        },
        scrollY: "400px",
        scrollCollapse: true,
        paging: false,
        info: false,
        dom: "Bfrtip",
        buttons: [
          {
            extend: "excelHtml5",
            text: '<i class="fas fa-file-excel"></i> Excel',
            titleAttr: "Exportar a Excel",
            className: "btn btn-success btn-sm",
            title:
              "Resumen Consumo BIO - " +
              (date_range
                ? date_range.startDate.format("YYYY-MM-DD") + " a " + date_range.endDate.format("YYYY-MM-DD")
                : date_now),
            exportOptions: {
              columns: ":visible",
            },
            footer: true,
          },
          {
            extend: "print",
            text: '<i class="fa fa-print"></i> Imprimir',
            titleAttr: "Imprimir",
            className: "btn btn-info btn-sm",
            title: "RESUMEN CONSUMO BIO",
            messageTop:
              "Fecha: " +
              (date_range
                ? date_range.startDate.format("YYYY-MM-DD") + " a " + date_range.endDate.format("YYYY-MM-DD")
                : date_now),
            exportOptions: {
              columns: ":visible",
            },
            footer: true,
            customize: (win) => {
              $(win.document.body).find("table").addClass("display").css("font-size", "12px")
              $(win.document.body).find("table thead th").css({
                "background-color": "#3498DB",
                color: "white",
                "text-align": "center",
              })
              $(win.document.body).find("table tfoot th").css({
                "background-color": "#ecf0f1",
                "font-weight": "bold",
              })
            },
          },
          {
            extend: "pdfHtml5",
            text: '<i class="fas fa-file-pdf"></i> PDF',
            titleAttr: "Exportar a PDF",
            className: "btn btn-danger btn-sm",
            download: "open",
            orientation: "portrait",
            pageSize: "A4",
            title: "RESUMEN CONSUMO BIO",
            exportOptions: {
              columns: ":visible",
            },
            footer: true,
            customize: (doc) => {
              // Título del documento
              doc.content[0].text = "RESUMEN CONSUMO BIO"
              doc.content[0].fontSize = 16
              doc.content[0].bold = true
              doc.content[0].alignment = "center"
              doc.content[0].margin = [0, 0, 0, 10]

              // Agregar fecha
              doc.content.splice(1, 0, {
                text:
                  "Periodo: " +
                  (date_range
                    ? date_range.startDate.format("YYYY-MM-DD") + " a " + date_range.endDate.format("YYYY-MM-DD")
                    : date_now),
                fontSize: 10,
                alignment: "center",
                margin: [0, 0, 0, 15],
              })

              // Anchos de columnas
              doc.content[2].table.widths = ["20%", "30%", "15%", "20%", "15%"]

              // Estilos de la tabla
              doc.styles.tableHeader = {
                bold: true,
                fontSize: 10,
                color: "white",
                fillColor: "#3498DB",
                alignment: "center",
              }

              doc.styles.tableBodyEven = {
                fontSize: 9,
              }

              doc.styles.tableBodyOdd = {
                fontSize: 9,
              }

              doc.styles.tableFooter = {
                bold: true,
                fontSize: 10,
                fillColor: "#ecf0f1",
              }

              // Footer con fecha y página
              doc["footer"] = (currentPage, pageCount) => ({
                columns: [
                  { text: "Fecha de creación: " + date_now, alignment: "left", margin: [40, 0] },
                  { text: "Página " + currentPage + " de " + pageCount, alignment: "right", margin: [0, 0, 40, 0] },
                ],
                margin: [0, 10],
              })
            },
          },
        ],
        columns: [
          {
            data: "linea",
            className: "text-left",
          },
          {
            data: "sublinea",
            className: "text-left",
          },
          {
            data: "cantidad",
            className: "text-center",
            render: (data) => Number.parseFloat(data).toFixed(2),
          },
          {
            data: "costo",
            className: "text-center",
            render: (data) => Number.parseFloat(data).toFixed(10),
          },
          {
            data: "total",
            className: "text-center",
            render: (data) => Number.parseFloat(data).toFixed(2),
          },
        ],
        order: [[0, "asc"]],
      })
    },
    error: (xhr, status, error) => {
      console.error("Error al cargar datos:", error)
      alert("Error al cargar los datos. Por favor intente nuevamente.")
    },
  })
}

$(() => {
  $('input[name="date_range2"]')
    .daterangepicker({
      locale: {
        format: "YYYY-MM-DD",
        applyLabel: '<i class="fas fa-chart-pie"></i> Aplicar',
        cancelLabel: '<i class="fas fa-times"></i> Cancelar',
      },
    })
    .on("apply.daterangepicker", (ev, picker) => {
      date_range = picker
      generate_report_piscinas()
    })
    .on("cancel.daterangepicker", function (ev, picker) {
      $(this).data("daterangepicker").setStartDate(date_now)
      $(this).data("daterangepicker").setEndDate(date_now)
      date_range = picker
      generate_report_piscinas()
    })

  // Cargar datos al iniciar
  generate_report_piscinas()
})

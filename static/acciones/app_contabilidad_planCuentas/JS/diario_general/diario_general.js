
var date_range = null
var tblDiario
var date_now = new moment().format("YYYY-MM-DD")

function generate_report_diario() {
  var parameters = {
    action: "searchdata",
    fecha_inicio: date_now,
    fecha_fin: date_now,
    empresa: "PSM",
  }

  if (date_range !== null) {
    parameters["fecha_inicio"] = date_range.startDate.format("YYYY-MM-DD")
    parameters["fecha_fin"] = date_range.endDate.format("YYYY-MM-DD")
  }

  tblDiario = $("#data").DataTable({
    responsive: true,
    autoWidth: false,
    destroy: true,
    deferRender: true,
    bPaginate: false,
    scrollY: "700px",
    scrollX: true,
    bInfo: false,
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
    dom: "Bfrtip",
    ajax: {
      url: window.location.pathname,
      type: "POST",
      data: parameters,
      dataSrc: (json) => {
        var data = json.asientos
        data.push(json.total_general)
        return data
      },
    },
    columns: [
      { data: "fecha" },
      { data: "codigo" },
      { data: "nombre" },
      { data: "doc" },
      { data: "descripcion" },
      { data: "debe" },
      { data: "haber" },
    ],
    columnDefs: [
      {
        targets: [-1, -2],
        class: "numeric",
        render: (data, type, row) => Number.parseFloat(data).toFixed(2),
      },
    ],
    createdRow: (row, data, dataIndex) => {
      if (data.tipo === "total") {
        $(row).addClass("total-row resaltado")
      } else if (data.tipo === "grand_total") {
        $(row).addClass("grand-total resaltado")
      }
    },
    buttons: [
      {
        extend: "excelHtml5",
        text: '<i class="fas fa-file-excel"></i> Excel',
        titleAttr: "Exportar a Excel",
        className: "btn btn-success btn-sm",
        exportOptions: {
          format: {
            body: (data, row, column, node) => {
              if (row.tipo === "total" || row.tipo === "grand_total") {
                if (column === 0) {
                  return data
                } else if (column === 5 || column === 6) {
                  return data
                }
                return ""
              }
              return data
            },
          },
        },
      },
      {
        extend: "pdfHtml5",
        text: '<i class="fas fa-file-pdf"></i> PDF',
        titleAttr: "Exportar a PDF",
        className: "btn btn-danger btn-sm",
        exportOptions: {
          format: {
            body: (data, row, column, node) => {
              if (row.tipo === "total" || row.tipo === "grand_total") {
                if (column === 0) {
                  return data
                } else if (column === 5 || column === 6) {
                  return data
                }
                return ""
              }
              return data
            },
          },
        },
        customize: (doc) => {
          doc.pageOrientation = "landscape"
          doc.pageSize = "A4"
          doc.pageMargins = [20, 20, 20, 20]
          doc.defaultStyle.fontSize = 8
          doc.styles.tableHeader.fontSize = 9
          doc.content[1].table.widths = ["7%", "10%", "20%", "30%", "23%", "5%", "5%"]
          doc.content.splice(0, 0, {
            text: "Diario General Acumulado",
            style: "header",
            alignment: "center",
            margin: [0, 0, 0, 10],
          })
          doc.styles.header = {
            fontSize: 18,
            bold: true,
          }
          var objLayout = {}
          objLayout["hLineWidth"] = (i) => 0.5
          objLayout["vLineWidth"] = (i) => 0.5
          objLayout["hLineColor"] = (i) => "#aaa"
          objLayout["vLineColor"] = (i) => "#aaa"
          objLayout["paddingLeft"] = (i) => 4
          objLayout["paddingRight"] = (i) => 4
          doc.content[1].layout = objLayout
        },
      },
      {
        extend: "print",
        text: '<i class="fas fa-print"></i> Imprimir',
        titleAttr: "Imprimir",
        className: "btn btn-info btn-sm",
        exportOptions: {
          format: {
            body: (data, row, column, node) => {
              if (row.tipo === "total" || row.tipo === "grand_total") {
                if (column === 0) {
                  return data
                } else if (column === 5 || column === 6) {
                  return data
                }
                return ""
              }
              return data
            },
          },
        },
      },
      {
        extend: "colvis",
        text: '<i class="fas fa-columns"></i> Columnas',
        titleAttr: "Visibilidad de columnas",
        className: "btn btn-secondary btn-sm",
      },
    ],
    initComplete: (settings, json) => {},
  })
}

$(() => {
  $('input[name="rango_dias"]')
    .daterangepicker({
      locale: {
        format: "YYYY-MM-DD",
        applyLabel: '<i class="fas fa-chart-pie"></i> Aplicar',
        cancelLabel: '<i class="fas fa-times"></i> Cancelar',
      },
    })
    .on("apply.daterangepicker", (ev, picker) => {
      date_range = picker
      generate_report_diario()
    })
    .on("cancel.daterangepicker", function (ev, picker) {
      $(this).data("daterangepicker").setStartDate(date_now)
      $(this).data("daterangepicker").setEndDate(date_now)
      date_range = picker
      generate_report_diario()
    })

  generate_report_diario()
})


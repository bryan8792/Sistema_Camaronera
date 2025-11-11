
var date_range = null
var multiplicadora = 0,
  total_stock = 0
var tb_resumen_conglomerado
var total, group_assoc, group_total, total_seg
var cant_tot = 0,
  tot = 0
var date_now = moment().format("YYYY-MM-DD")
var empresa_seleccionada = ""

function get_piscinas_por_empresa(empresa) {
  var piscinas_map = {
    PSM: { min: 1, max: 20 },
    BIO: { min: 21, max: 45 },
  }
  return piscinas_map[empresa] || null
}

function generate_report_insumos() {
  console.log("=== Generando reporte ===")
  console.log("Empresa seleccionada:", empresa_seleccionada)

  var parameters = {
    action: "search_report_insumos_conglomerado",
    start_date: date_now,
    end_date: date_now,
  }

  if (empresa_seleccionada) {
    parameters["empresa"] = empresa_seleccionada
    console.log("Parámetro empresa agregado:", parameters["empresa"])
  }

  if (date_range !== null) {
    parameters["start_date"] = date_range.startDate.format("YYYY-MM-DD")
    parameters["end_date"] = date_range.endDate.format("YYYY-MM-DD")
    console.log("Rango de fechas:", parameters["start_date"], "a", parameters["end_date"])
  }

  var groupColumn = 0

  if ($.fn.DataTable.isDataTable("#tb_resumen_conglomerado")) {
    $("#tb_resumen_conglomerado").DataTable().destroy()
  }

  tb_resumen_conglomerado = $("#tb_resumen_conglomerado").DataTable({
    autoWidth: false,
    destroy: true,
    deferRender: true,
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
    order: [[groupColumn, "asc"]],
    ajax: {
      url: window.location.pathname,
      type: "POST",
      data: parameters,
      dataSrc: (json) => {
        console.log("Datos recibidos del servidor:", json.length, "registros")
        return json
      },
    },
    scrollY: "700px",
    scrollX: true,
    paging: false,
    info: true,
    dom: "Bfrtip",
    buttons: [
      {
        extend: "excelHtml5",
        text: '<i class="fas fa-file-csv"></i> ',
        titleAttr: "Exportar a Excell",
        className: "btn btn-success",
      },
      {
        extend: "pdfHtml5",
        text: '<i class="fas fa-file-pdf"></i> ',
        titleAttr: "Exportar a PDF",
        className: "btn btn-danger",
        download: "open",
        orientation: "portrait",
        pageSize: "LEGAL",
        footer: true,
        header: true,
        customize: (doc) => {
          var lastColX = null
          var lastColY = null
          var bod = []
          doc.content[1].table.body.forEach((line, i) => {
            if (lastColX !== line[0].text && line[0].text !== "") {
              bod.push([
                { text: "", style: "tableHeader" },
                { text: "", style: "tableHeader" },
                { text: "", style: "tableHeader" },
                { text: "", style: "tableHeader" },
                { text: cant_tot.toFixed(2) > 0 ? cant_tot.toFixed(2) : "", style: "tableHeader" },
                { text: "", style: "tableHeader" },
                { text: tot.toFixed(2) > 0 ? tot.toFixed(2) : "", style: "tableHeader" },
              ])

              bod.push([
                { text: line[0].text, style: "tableHeader" },
                { text: "", style: "tableHeader" },
                { text: "", style: "tableHeader" },
                { text: "", style: "tableHeader" },
                { text: "", style: "tableHeader" },
                { text: "", style: "tableHeader" },
                { text: "", style: "tableHeader" },
              ])
              lastColX = line[0].text
              cant_tot = 0
              tot = 0
            }
            if (i < doc.content[1].table.body.length - 1) {
              cant_tot += Number.parseFloat(line[3].text)
              tot += Number.parseFloat(line[5].text)
              bod.push([
                "",
                "",
                { text: line[1].text, style: "defaultStyle" },
                { text: line[2].text, style: "defaultStyle" },
                { text: line[3].text, style: "defaultStyle" },
                { text: line[4].text, style: "defaultStyle" },
                { text: line[5].text, style: "defaultStyle" },
              ])
            } else {
              cant_tot += Number.parseFloat(line[3].text)
              tot += Number.parseFloat(line[5].text)
              bod.push([
                "",
                "",
                { text: line[1].text, style: "defaultStyle" },
                { text: line[2].text, style: "defaultStyle" },
                { text: line[3].text, style: "defaultStyle" },
                { text: line[4].text, style: "defaultStyle" },
                { text: line[5].text, style: "defaultStyle" },
              ])
              bod.push([
                { text: "", style: "tableHeader" },
                { text: "", style: "tableHeader" },
                { text: "", style: "tableHeader" },
                { text: "", style: "tableHeader" },
                { text: cant_tot.toFixed(2) > 0 ? cant_tot.toFixed(2) : "", style: "tableHeader" },
                { text: "", style: "tableHeader" },
                { text: tot.toFixed(2) > 0 ? tot.toFixed(2) : "", style: "tableHeader" },
              ])
            }
          })
          doc.content[1].table.headerRows = 1
          doc.content[1].table.widths = [130, 1, 60, 100, 50, 50, 50]
          doc.content[1].table.body = bod
          doc.content[1].layout = "lightHorizontalLines"
          doc.styles = {
            header: {
              fontSize: 22,
              bold: true,
              alignment: "center",
            },
            subheader: {
              fontSize: 10,
              bold: true,
              color: "black",
            },
            tableHeader: {
              bold: true,
              fontSize: 11,
              color: "white",
              fillColor: "#2d4154",
              alignment: "center",
            },
            lastLine: {
              bold: true,
              fontSize: 11,
              color: "black",
            },
            defaultStyle: {
              fontSize: 10,
              color: "black",
            },
          }
          doc["footer"] = (page, pages) => ({
            columns: [
              {
                alignment: "left",
                text: ["Fecha de creación: ", { text: date_now }],
              },
              {
                alignment: "right",
                text: ["página ", { text: page.toString() }, " de ", { text: pages.toString() }],
              },
            ],
            margin: 20,
          })
          doc["header"] = (page, pages) => ({
            columns: [
              {
                alignment: "center",
                text: ["DETALLE DE INSUMOS POR PISCINAS", " PSM & BIO"],
                margin: [0, 10],
              },
            ],
            margin: [30, 0],
          })
        },
      },
    ],
    columns: [
      { data: "producto_empresa.nombre_prod.nombre", width: "45" },
      { data: "piscinas", width: "10" },
      { data: "fecha_ingreso", width: "10" },
      { data: "cantidad_egreso", width: "10" },
      { data: "producto_empresa.nombre_prod.costo_aplicacion", width: "10" },
      { data: "producto_empresa.nombre_prod.costo_aplicacion", width: "15" },
    ],
    columnDefs: [
      { visible: true, targets: groupColumn },
      {
        targets: [0],
        class: "text-left",
        orderable: false,
        render: (data, type, row) => data,
      },
      {
        targets: [1],
        class: "text-center",
        orderable: false,
        render: (data, type, row) => data,
      },
      {
        targets: [2],
        class: "text-center",
        orderable: false,
        render: (data, type, row) => data,
      },
      {
        targets: [-3],
        class: "text-center",
        orderable: false,
        render: (data, type, row) => Number.parseFloat(data).toFixed(2),
      },
      {
        targets: [-2],
        class: "text-center",
        orderable: false,
        render: (data, type, row) => Number.parseFloat(data).toFixed(4),
      },
      {
        targets: [-1],
        class: "text-center",
        orderable: false,
        render: (row, type, data) => {
          var valor = Number.parseFloat(row).toFixed(4)
          var egreso = Number.parseFloat(data.cantidad_egreso).toFixed(4)
          multiplicadora = valor * egreso
          return "<b>" + Number.parseFloat(multiplicadora).toFixed(4) + "</b>"
        },
      },
    ],
    drawCallback: function (setting) {
      var api = this.api()
      var rows = api.rows({ page: "current" }).nodes()
      var last = null
      var total = 0,
        total2 = 0
      var filas = api.column(groupColumn, { page: "current" }).data()

      console.log("Calculando totales en drawCallback, filas:", filas.length)

      filas.each((group, i) => {
        if (last !== group) {
          if (last !== null) {
            $(rows)
              .eq(i - 1)
              .after(
                `<tr class="total">
                                <td colspan="2" style="width: 55%;"></td>
                                <td class="text-center" style="width: 10%;font-weight:700;background-color:rgb(255, 255, 255)">Cantidad Total:</td>
                                <td class="text-center" style="width: 10%;font-weight:700;background-color:rgb(255, 255, 255)">${total.toFixed(2)}</td>   
                                <td class="text-center" style="width: 10%;font-weight:700;background-color:rgb(255, 255, 255)">Valor Total:</td>  
                                <td class="text-center" style="width: 15%;font-weight:700;background-color:rgb(255, 255, 255)">${total2.toFixed(4)}</td>   
                            </tr>`,
              )
            console.log("Subtotal para grupo", last, "- Cantidad:", total.toFixed(2), "Valor:", total2.toFixed(4))
            total = 0
            total2 = 0
          }
          $(rows)
            .eq(i)
            .before(
              '<tr class="group text-center" style="BACKGROUND-COLOR:rgb(237, 208, 0);font-weight:700;">' +
                '<td colspan="6" style="width: 100%">' +
                group +
                "</td>" +
                "</tr>",
            )
          last = group
        }
        total += +$(rows).eq(i).children()[3].textContent
        total2 += +$(rows).eq(i).children()[5].textContent
        if (i === filas.length - 1) {
          $(rows)
            .eq(i)
            .after(
              `<tr class="total">
                            <td colspan="2" style="width: 55%;"></td>
                            <td class="text-center" style="width: 10%;font-weight:700;background-color:rgb(255, 255, 255)">Cantidad Total:</td>
                            <td class="text-center" style="width: 10%;font-weight:700;background-color:rgb(255, 255, 255)">${total.toFixed(2)}</td>   
                            <td class="text-center" style="width: 10%;font-weight:700;background-color:rgb(255, 255, 255)">Valor Total:</td>  
                            <td class="text-center" style="width: 15%;font-weight:700;background-color:rgb(255, 255, 255)">${total2.toFixed(4)}</td>   
                        </tr>`,
            )
          console.log("Total final - Cantidad:", total.toFixed(2), "Valor:", total2.toFixed(4))
        }
      })
    },
    initComplete: (settings, json) => {
      console.log("DataTable inicializado completamente")
    },
  })
}

$(() => {
  $('input[name="date_range"]')
    .daterangepicker({
      locale: {
        format: "YYYY-MM-DD",
        applyLabel: '<i class="fas fa-chart-pie"></i> Aplicar',
        cancelLabel: '<i class="fas fa-times"></i> Cancelar',
      },
    })
    .on("apply.daterangepicker", (ev, picker) => {
      date_range = picker
      console.log("Aplicando rango de fechas")
      generate_report_insumos()
    })
    .on("cancel.daterangepicker", function (ev, picker) {
      $(this).data("daterangepicker").setStartDate(date_now)
      $(this).data("daterangepicker").setEndDate(date_now)
      date_range = picker
      generate_report_insumos()
    })

  $("#select_empresa").on("change", function () {
    empresa_seleccionada = $(this).val()
    console.log("Empresa seleccionada cambiada a:", empresa_seleccionada)
    generate_report_insumos()
  })

  console.log("Inicializando aplicación - Detalle Insumos por Piscinas")
  generate_report_insumos()
})

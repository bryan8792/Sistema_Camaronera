/*
const { jsPDF } = window.jspdf
let gridOptions

function getCurrentDateTime() {
    const now = new Date()
    return now.toLocaleString("es-EC", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
        hour12: false,
    })
}

const loadData = async () => {
    try {
        const fechaInicio = document.querySelector('input[name="fecha_inicio"]').value
        const fechaFin = document.querySelector('input[name="fecha_fin"]').value

        const response = await fetch(window.location.pathname, {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: new URLSearchParams({
                action: "searchdata_psm",
                fecha_inicio: fechaInicio,
                fecha_fin: fechaFin,
            }),
        })

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
        }

        const contentType = response.headers.get("content-type")
        if (!contentType || !contentType.includes("application/json")) {
            const text = await response.text()
            console.error("Respuesta no JSON:", text)
            throw new Error("La respuesta del servidor no es JSON válido")
        }

        const rawData = await response.json()

        if (rawData.error) {
            console.error("Error en los datos:", rawData.error)
            throw new Error(rawData.error)
        }

        const processedData = rawData
            .map((item) => ({
                ...item,
                saldo_anterior_debe: Number.parseFloat(item.saldo_anterior_debe || 0),
                saldo_anterior_haber: Number.parseFloat(item.saldo_anterior_haber || 0),
                debe: Number.parseFloat(item.debe || 0),
                haber: Number.parseFloat(item.haber || 0),
            }))
            .filter(
                (item, index, self) =>
                    index ===
                    self.findIndex((t) => t.cuenta.codigo === item.cuenta.codigo && t.cuenta.nombre === item.cuenta.nombre),
            )

        console.log("Datos procesados:", processedData)

        gridOptions.api.setRowData(processedData)
    } catch (error) {
        console.error("Error realizando la petición AJAX:", error)
        alert(`Error al cargar los datos: ${error.message}`)
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const columnDefs = [
        {
            headerName: "Group",
            field: "cuenta.codigo",
            rowGroup: true,
            hide: true,
        },
        {
            headerName: "Cuenta",
            field: "cuenta.nombre",
            width: 300,
        },
        {
            headerName: "SALDO ANTERIOR",
            children: [
                {
                    headerName: "DEBE",
                    field: "saldo_anterior_debe",
                    width: 120,
                    valueFormatter: (params) => Number(params.value || 0).toFixed(2),
                    cellClass: "numeric-cell",
                    aggFunc: "sum",
                },
                {
                    headerName: "HABER",
                    field: "saldo_anterior_haber",
                    width: 120,
                    valueFormatter: (params) => Number(params.value || 0).toFixed(2),
                    cellClass: "numeric-cell",
                    aggFunc: "sum",
                },
            ],
        },
        {
            headerName: "SALDO DEL MES",
            children: [
                {
                    headerName: "DEBE",
                    field: "debe",
                    width: 120,
                    valueFormatter: (params) => Number(params.value || 0).toFixed(2),
                    cellClass: "numeric-cell",
                    aggFunc: "sum",
                },
                {
                    headerName: "HABER",
                    field: "haber",
                    width: 120,
                    valueFormatter: (params) => Number(params.value || 0).toFixed(2),
                    cellClass: "numeric-cell",
                    aggFunc: "sum",
                },
            ],
        },
        {
            headerName: "SALDO ACTUAL",
            children: [
                {
                    headerName: "DEBE",
                    width: 120,
                    valueGetter: (params) => {
                        if (params.data) {
                            const total =
                                params.data.saldo_anterior_debe +
                                params.data.debe -
                                (params.data.saldo_anterior_haber + params.data.haber)
                            return total > 0 ? total : 0
                        }
                        return params.node.group ? params.node.aggData?.debe || 0 : 0
                    },
                    valueFormatter: (params) => Number(params.value || 0).toFixed(2),
                    cellClass: "numeric-cell",
                    aggFunc: "sum",
                },
                {
                    headerName: "HABER",
                    width: 120,
                    valueGetter: (params) => {
                        if (params.data) {
                            const total =
                                params.data.saldo_anterior_haber +
                                params.data.haber -
                                (params.data.saldo_anterior_debe + params.data.debe)
                            return total > 0 ? total : 0
                        }
                        return params.node.group ? params.node.aggData?.haber || 0 : 0
                    },
                    valueFormatter: (params) => Number(params.value || 0).toFixed(2),
                    cellClass: "numeric-cell",
                    aggFunc: "sum",
                },
            ],
        },
    ]

    gridOptions = {
        columnDefs: columnDefs,
        defaultColDef: {
            sortable: true,
            filter: true,
            resizable: true,
            suppressMenu: true,
        },
        autoGroupColumnDef: {
            headerName: "Cuenta",
            minWidth: 300,
            cellRenderer: "agGroupCellRenderer",
            cellRendererParams: {
                suppressCount: true,
                innerRenderer: (params) => {
                    if (params.node.group) {
                        return params.value
                    }
                    return `${params.data["cuenta.codigo"]} - ${params.data["cuenta.nombre"]}`
                },
            },
        },
        groupDefaultExpanded: 0,
        suppressAggFuncInHeader: true,
        animateRows: true,
        rowClass: "custom-row",
        getRowStyle: (params) => {
            if (params.node.footer) {
                return {
                    "background-color": "#e6f3ff",
                    "font-weight": "bold",
                }
            }
            return params.node.rowIndex % 2 === 0 ? {"background-color": "#ffffff"} : {"background-color": "#f8f8f8"}
        },
        onGridReady: (params) => {
            params.api.sizeColumnsToFit()
        },
        groupIncludeFooter: true,
        groupFooterAggNodes: "filtered",
        suppressAggFilteredOnly: true,
    }

    // Add CSS styles
    const styleElement = document.createElement("style")
    styleElement.textContent = `
    .ag-theme-alpine {
      --ag-header-height: 40px;
      --ag-header-background-color: #f5f7f7;
      --ag-header-foreground-color: #181d1f;
      --ag-header-cell-hover-background-color: #e6e6e6;
      --ag-row-hover-color: #f0f0f0;
      --ag-selected-row-background-color: #b7e4ff;
    }
    .numeric-cell {
      text-align: right;
    }
    .custom-row {
      border-bottom: 1px solid #e2e2e2;
    }
    .ag-row-group {
      font-weight: bold;
    }
    .ag-row-footer {
      background-color: #e6f3ff !important;
      font-weight: bold;
    }
  `
    document.head.appendChild(styleElement)

    const eGridDiv = document.querySelector("#myGrid")
    new agGrid.Grid(eGridDiv, gridOptions)

    loadData()

    // Export functions remain the same...
    document.getElementById("exportExcel").addEventListener("click", () => {
        const rowData = []
        let totalSaldoAnteriorDebe = 0
        let totalSaldoAnteriorHaber = 0
        let totalDebe = 0
        let totalHaber = 0
        let totalSaldoActualDebe = 0
        let totalSaldoActualHaber = 0

        gridOptions.api.forEachNodeAfterFilterAndSort((node) => {
            if (!node.group) {
                // Solo procesar nodos que no son grupos
                const data = {
                    CÓDIGO: node.data.cuenta.codigo,
                    "NOMBRE CUENTA": node.data.cuenta.nombre,
                    "SALDO ANTERIOR DEBE": Number(node.data.saldo_anterior_debe || 0).toFixed(2),
                    "SALDO ANTERIOR HABER": Number(node.data.saldo_anterior_haber || 0).toFixed(2),
                    DEBE: Number(node.data.debe || 0).toFixed(2),
                    HABER: Number(node.data.haber || 0).toFixed(2),
                    "SALDO ACTUAL DEBE": Number(node.data.saldo_actual_debe || 0).toFixed(2),
                    "SALDO ACTUAL HABER": Number(node.data.saldo_actual_haber || 0).toFixed(2),
                }
                rowData.push(data)

                // Acumular totales
                totalSaldoAnteriorDebe += Number(node.data.saldo_anterior_debe || 0)
                totalSaldoAnteriorHaber += Number(node.data.saldo_anterior_haber || 0)
                totalDebe += Number(node.data.debe || 0)
                totalHaber += Number(node.data.haber || 0)
                totalSaldoActualDebe += Number(node.data.saldo_actual_debe || 0)
                totalSaldoActualHaber += Number(node.data.saldo_actual_haber || 0)
            }
        })

        // Agregar fila de totales
        rowData.push({
            CÓDIGO: "",
            "NOMBRE CUENTA": "TOTALES",
            "SALDO ANTERIOR DEBE": totalSaldoAnteriorDebe.toFixed(2),
            "SALDO ANTERIOR HABER": totalSaldoAnteriorHaber.toFixed(2),
            DEBE: totalDebe.toFixed(2),
            HABER: totalHaber.toFixed(2),
            "SALDO ACTUAL DEBE": totalSaldoActualDebe.toFixed(2),
            "SALDO ACTUAL HABER": totalSaldoActualHaber.toFixed(2),
        })

        const worksheet = XLSX.utils.json_to_sheet(rowData)
        const workbook = XLSX.utils.book_new()

        // Configurar el ancho de las columnas
        const wscols = [
            {wch: 15}, // CÓDIGO
            {wch: 40}, // NOMBRE CUENTA
            {wch: 15}, // SALDO ANTERIOR DEBE
            {wch: 15}, // SALDO ANTERIOR HABER
            {wch: 15}, // DEBE
            {wch: 15}, // HABER
            {wch: 15}, // SALDO ACTUAL DEBE
            {wch: 15}, // SALDO ACTUAL HABER
        ]
        worksheet["!cols"] = wscols

        // Agregar fecha y hora de generación
        XLSX.utils.sheet_add_aoa(worksheet, [["Fecha y hora de generación:", getCurrentDateTime()]], {origin: -1})

        XLSX.utils.book_append_sheet(workbook, worksheet, "Balance de Comprobación")
        XLSX.writeFile(workbook, `balance_comprobacion_${getCurrentDateTime().replace(/[/:]/g, "-")}.xlsx`)
    })

    // Modificar la función de exportación a PDF
    document.getElementById("exportPdf").addEventListener("click", () => {
        const doc = new jsPDF("l", "pt", "a4")

        doc.setFontSize(16)
        doc.text("PESQUERA SAN MIGUEL C. LTDA.", doc.internal.pageSize.width / 2, 40, {align: "center"})
        doc.setFontSize(14)
        doc.text("BALANCE DE COMPROBACIÓN", doc.internal.pageSize.width / 2, 60, {align: "center"})

        const fechaInicio = document.querySelector('input[name="fecha_inicio"]').value
        const fechaFin = document.querySelector('input[name="fecha_fin"]').value
        doc.setFontSize(12)
        doc.text(`Del ${fechaInicio} al ${fechaFin}`, doc.internal.pageSize.width / 2, 80, {align: "center"})

        doc.setFontSize(10)
        doc.text(`Generado el: ${getCurrentDateTime()}`, doc.internal.pageSize.width - 200, 100)

        const rows = []
        let totalSaldoAnteriorDebe = 0
        let totalSaldoAnteriorHaber = 0
        let totalDebe = 0
        let totalHaber = 0
        let totalSaldoActualDebe = 0
        let totalSaldoActualHaber = 0

        gridOptions.api.forEachNodeAfterFilterAndSort((node) => {
            if (!node.group) {
                const saldoAnteriorDebe = Number(node.data.saldo_anterior_debe || 0)
                const saldoAnteriorHaber = Number(node.data.saldo_anterior_haber || 0)
                const debe = Number(node.data.debe || 0)
                const haber = Number(node.data.haber || 0)
                const saldoActualDebe = Number(node.data.saldo_actual_debe || 0)
                const saldoActualHaber = Number(node.data.saldo_actual_haber || 0)

                rows.push([
                    node.data.cuenta.codigo,
                    node.data.cuenta.nombre,
                    saldoAnteriorDebe.toFixed(2),
                    saldoAnteriorHaber.toFixed(2),
                    debe.toFixed(2),
                    haber.toFixed(2),
                    saldoActualDebe.toFixed(2),
                    saldoActualHaber.toFixed(2),
                ])

                totalSaldoAnteriorDebe += saldoAnteriorDebe
                totalSaldoAnteriorHaber += saldoAnteriorHaber
                totalDebe += debe
                totalHaber += haber
                totalSaldoActualDebe += saldoActualDebe
                totalSaldoActualHaber += saldoActualHaber
            }
        })

        rows.push([
            "",
            "TOTALES",
            totalSaldoAnteriorDebe.toFixed(2),
            totalSaldoAnteriorHaber.toFixed(2),
            totalDebe.toFixed(2),
            totalHaber.toFixed(2),
            totalSaldoActualDebe.toFixed(2),
            totalSaldoActualHaber.toFixed(2),
        ])

        doc.autoTable({
            startY: 120,
            head: [
                [
                    "CÓDIGO",
                    "NOMBRE CUENTA",
                    "SALDO ANTERIOR DEBE",
                    "SALDO ANTERIOR HABER",
                    "DEBE",
                    "HABER",
                    "SALDO ACTUAL DEBE",
                    "SALDO ACTUAL HABER",
                ],
            ],
            body: rows,
            theme: "grid",
            styles: {
                fontSize: 8,
                cellPadding: 2,
            },
            columnStyles: {
                0: {cellWidth: 85, halign: "center"},
                1: {cellWidth: 230},
                2: {cellWidth: 85, halign: "right"},
                3: {cellWidth: 85, halign: "right"},
                4: {cellWidth: 70, halign: "right"},
                5: {cellWidth: 70, halign: "right"},
                6: {cellWidth: 75, halign: "right"},
                7: {cellWidth: 75, halign: "right"},
            },
            headStyles: {
                fillColor: [200, 200, 200],
                textColor: [0, 0, 0],
                fontStyle: "bold",
                halign: "center",
            },
            didDrawPage: (data) => {
                doc.setFontSize(8)
                doc.text(
                    "Página " + doc.internal.getCurrentPageInfo().pageNumber,
                    doc.internal.pageSize.width - 60,
                    doc.internal.pageSize.height - 10,
                )
            },
            footStyles: {
                fillColor: [200, 200, 200],
                textColor: [0, 0, 0],
                fontStyle: "bold",
            },
        })

        doc.save(`balance_comprobacion_${getCurrentDateTime().replace(/[/:]/g, "-")}.pdf`)
    })

    document.getElementById("btnActualizar").addEventListener("click", loadData)
})

function getCookie(name) {
    let cookieValue = null
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";")
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim()
            if (cookie.substring(0, name.length + 1) === name + "=") {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
                break
            }
        }
    }
    return cookieValue
}


*/

/*
const { jsPDF } = window.jspdf
let gridOptions

function getCurrentDateTime() {
  const now = new Date()
  return now.toLocaleString("es-EC", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  })
}

const loadData = async () => {
  try {
    const fechaInicio = document.querySelector('input[name="fecha_inicio"]').value
    const fechaFin = document.querySelector('input[name="fecha_fin"]').value

    if (!fechaInicio || !fechaFin) {
      throw new Error("Las fechas de inicio y fin son requeridas")
    }

    const response = await fetch(window.location.pathname, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: new URLSearchParams({
        action: "searchdata_psm",
        fecha_inicio: fechaInicio,
        fecha_fin: fechaFin,
      }),
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    if (data.error) {
      throw new Error(data.error)
    }

    // Process data to create tree structure
    const processedData = data.map((item) => ({
      ...item,
      // Format display name
      displayName: `${item.codigo} - ${item.nombre}`,
    }))

    gridOptions.api.setRowData(processedData)
  } catch (error) {
    console.error("Error realizando la petición AJAX:", error)
    alert(`Error al cargar los datos: ${error.message}`)
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const columnDefs = [
    {
      headerName: "Cuenta",
      field: "displayName",
      width: 300,
      cellRenderer: "agGroupCellRenderer",
      showRowGroup: true,
      cellRendererParams: {
        suppressCount: true,
        innerRenderer: (params) => {
          return params.value
        },
      },
    },
    {
      headerName: "Saldo Anterior",
      children: [
        {
          headerName: "Debe",
          field: "saldo_anterior_debe",
          width: 120,
          valueFormatter: (params) => Number(params.value || 0).toFixed(2),
          cellClass: "numeric-cell",
          aggFunc: "sum",
        },
        {
          headerName: "Haber",
          field: "saldo_anterior_haber",
          width: 120,
          valueFormatter: (params) => Number(params.value || 0).toFixed(2),
          cellClass: "numeric-cell",
          aggFunc: "sum",
        },
      ],
    },
    {
      headerName: "Movimientos",
      children: [
        {
          headerName: "Debe",
          field: "debe",
          width: 120,
          valueFormatter: (params) => Number(params.value || 0).toFixed(2),
          cellClass: "numeric-cell",
          aggFunc: "sum",
        },
        {
          headerName: "Haber",
          field: "haber",
          width: 120,
          valueFormatter: (params) => Number(params.value || 0).toFixed(2),
          cellClass: "numeric-cell",
          aggFunc: "sum",
        },
      ],
    },
    {
      headerName: "Saldo Actual",
      children: [
        {
          headerName: "Deudor",
          width: 120,
          valueGetter: (params) => {
            if (!params.data) return 0
            const total = params.data.saldo_actual_debe - params.data.saldo_actual_haber
            return total > 0 ? total : 0
          },
          valueFormatter: (params) => Number(params.value || 0).toFixed(2),
          cellClass: "numeric-cell",
          aggFunc: "sum",
        },
        {
          headerName: "Acreedor",
          width: 120,
          valueGetter: (params) => {
            if (!params.data) return 0
            const total = params.data.saldo_actual_haber - params.data.saldo_actual_debe
            return total > 0 ? total : 0
          },
          valueFormatter: (params) => Number(params.value || 0).toFixed(2),
          cellClass: "numeric-cell",
          aggFunc: "sum",
        },
      ],
    },
  ]

  gridOptions = {
    columnDefs,
    defaultColDef: {
      sortable: true,
      filter: true,
      resizable: true,
      suppressMenu: true,
    },
    treeData: true,
    getDataPath: (data) => {
      const path = []
      let code = data.codigo

      // Build path based on code length
      while (code.length > 0) {
        path.push(code)
        code = code.slice(0, -2) // Remove last two digits
        if (code.length === 1) {
          path.push(code)
          break
        }
      }

      return path.reverse()
    },
    groupDefaultExpanded: 1,
    suppressAggFuncInHeader: true,
    animateRows: true,
    rowClass: (params) => {
      if (params.node.group) return "group-row"
      return "custom-row"
    },
    getRowStyle: (params) => {
      if (params.node.footer) {
        return {
          "background-color": "#e6f3ff",
          "font-weight": "bold",
        }
      }
      if (params.node.group) {
        const level = params.node.level
        return {
          "background-color": level === 0 ? "#f0f0f0" : "#f5f5f5",
          "font-weight": "bold",
          "font-size": level === 0 ? "1.1em" : "inherit",
        }
      }
      return params.node.rowIndex % 2 === 0 ? { "background-color": "#ffffff" } : { "background-color": "#f8f8f8" }
    },
    onGridReady: (params) => {
      params.api.sizeColumnsToFit()
    },
    groupIncludeFooter: true,
    groupFooterAggNodes: "filtered",
  }

  // Add CSS styles
  const styleElement = document.createElement("style")
  styleElement.textContent = `
        .ag-theme-alpine {
            --ag-header-height: 40px;
            --ag-header-background-color: #f5f7f7;
            --ag-header-foreground-color: #181d1f;
            --ag-header-cell-hover-background-color: #e6e6e6;
            --ag-row-hover-color: #f0f0f0;
            --ag-selected-row-background-color: #b7e4ff;
        }
        .numeric-cell {
            text-align: right;
        }
        .custom-row {
            border-bottom: 1px solid #e2e2e2;
        }
        .group-row {
            background-color: #f5f5f5 !important;
            font-weight: bold;
            border-bottom: 1px solid #e2e2e2;
        }
        .ag-row-group {
            font-weight: bold;
        }
        .ag-row-footer {
            background-color: #e6f3ff !important;
            font-weight: bold;
        }
    `
  document.head.appendChild(styleElement)

  const eGridDiv = document.querySelector("#myGrid")
  new agGrid.Grid(eGridDiv, gridOptions)

  loadData()

  document.getElementById("btnActualizar").addEventListener("click", loadData)

  // Export to Excel
  document.getElementById("exportExcel").addEventListener("click", () => {
    const params = {
      fileName: `balance_comprobacion_${getCurrentDateTime().replace(/[/:]/g, "-")}.xlsx`,
      sheetName: "Balance de Comprobación",
    }
    gridOptions.api.exportDataAsExcel(params)
  })

  // Export to PDF
  document.getElementById("exportPdf").addEventListener("click", () => {
    const doc = new jsPDF("l", "pt", "a4")

    doc.setFontSize(18)
    doc.text("Balance de Comprobación", doc.internal.pageSize.width / 2, 40, { align: "center" })

    const fechaInicio = document.querySelector('input[name="fecha_inicio"]').value
    const fechaFin = document.querySelector('input[name="fecha_fin"]').value

    doc.setFontSize(12)
    doc.text(`Del ${fechaInicio} al ${fechaFin}`, doc.internal.pageSize.width / 2, 60, { align: "center" })

    const columnDefs = gridOptions.columnApi.getAllDisplayedColumns()
    const visibleColumns = columnDefs.filter((column) => column.isVisible())

    const tableData = []
    gridOptions.api.forEachNodeAfterFilterAndSort((node) => {
      if (node.data) {
        const rowData = {}
        visibleColumns.forEach((column) => {
          rowData[column.getColDef().headerName] = node.data[column.getColId()]
        })
        tableData.push(rowData)
      }
    })

    doc.autoTable({
      startY: 80,
      head: [visibleColumns.map((column) => column.getColDef().headerName)],
      body: tableData.map((row) => visibleColumns.map((column) => row[column.getColDef().headerName])),
      theme: "grid",
      styles: { fontSize: 8, cellPadding: 2 },
      columnStyles: visibleColumns.reduce((styles, column, index) => {
        styles[index] = { cellWidth: "auto" }
        return styles
      }, {}),
      didDrawPage: (data) => {
        doc.text(`Página ${data.pageNumber}`, data.settings.margin.left, doc.internal.pageSize.height - 10)
      },
    })

    doc.save(`balance_comprobacion_${getCurrentDateTime().replace(/[/:]/g, "-")}.pdf`)
  })
})

function getCookie(name) {
  let cookieValue = null
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";")
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim()
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}

*/

/*const { jsPDF } = window.jspdf
let gridOptions

function getCurrentDateTime() {
  const now = new Date()
  return now.toLocaleString("es-EC", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  })
}

const loadCuentas = async () => {
  try {
    const response = await fetch(window.location.pathname, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: new URLSearchParams({
        action: "get_cuentas",
      }),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const cuentas = await response.json()
    const selectInicio = document.querySelector('select[name="cuenta_inicio"]')
    const selectFin = document.querySelector('select[name="cuenta_fin"]')

    cuentas.forEach((cuenta) => {
      const option = new Option(`${cuenta.codigo} - ${cuenta.nombre}`, cuenta.codigo)
      selectInicio.add(option.cloneNode(true))
      selectFin.add(option)
    })

    // Establecer valores por defecto
    selectInicio.value = cuentas[0].codigo
    selectFin.value = cuentas[cuentas.length - 1].codigo
  } catch (error) {
    console.error("Error cargando las cuentas:", error)
    alert(`Error al cargar las cuentas: ${error.message}`)
  }
}

function showLoadingMessage() {
  const loadingDiv = document.createElement("div")
  loadingDiv.id = "loading-overlay"
  loadingDiv.innerHTML = `
    <div class="loading-content">
      <div class="loading-spinner"></div>
      <div class="loading-text">Procesando datos...</div>
    </div>
  `
  document.body.appendChild(loadingDiv)
}

function hideLoadingMessage() {
  const loadingDiv = document.getElementById("loading-overlay")
  if (loadingDiv) {
    loadingDiv.remove()
  }
}

const loadData = async () => {
  try {
    showLoadingMessage() // Show loading message before starting

    const fechaInicioElement = document.querySelector('input[name="fecha_inicio"]')
    const fechaFinElement = document.querySelector('input[name="fecha_fin"]')
    const cuentaInicioElement = document.querySelector('select[name="cuenta_inicio"]')
    const cuentaFinElement = document.querySelector('select[name="cuenta_fin"]')

    if (!fechaInicioElement || !fechaFinElement || !cuentaInicioElement || !cuentaFinElement) {
      throw new Error("No se encontraron todos los elementos necesarios en el formulario")
    }

    const fechaInicio = fechaInicioElement.value
    const fechaFin = fechaFinElement.value
    const cuentaInicio = cuentaInicioElement.value
    const cuentaFin = cuentaFinElement.value

    if (!fechaInicio || !fechaFin) {
      throw new Error("Las fechas de inicio y fin son requeridas")
    }

    const response = await fetch(window.location.pathname, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: new URLSearchParams({
        action: "searchdata_psm",
        fecha_inicio: fechaInicio,
        fecha_fin: fechaFin,
        cuenta_inicio: cuentaInicio,
        cuenta_fin: cuentaFin,
      }),
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    if (data.error) {
      throw new Error(data.error)
    }

    // Process data to create tree structure
    const processedData = data.map((item) => ({
      ...item,
      displayName: `${"  ".repeat(item.nivel - 1)}${item.codigo} ${item.nombre}`,
    }))

    gridOptions.api.setRowData(processedData)
  } catch (error) {
    console.error("Error realizando la petición AJAX:", error)
    alert(`Error al cargar los datos: ${error.message}`)
  } finally {
    hideLoadingMessage() // Hide loading message when done
  }
}

document.addEventListener("DOMContentLoaded", () => {
  // Set default dates to today
  const today = new Date().toISOString().split("T")[0]
  const fechaInicioElement = document.querySelector('input[name="fecha_inicio"]')
  const fechaFinElement = document.querySelector('input[name="fecha_fin"]')
  if (fechaInicioElement) fechaInicioElement.value = today
  if (fechaFinElement) fechaFinElement.value = today

  const columnDefs = [
    {
      headerName: "CÓDIGO",
      field: "codigo",
      width: 100,
      sort: "asc",
      sortable: true,
      headerClass: "header-blue",
      rowDrag: false,
    },
    {
      headerName: "NOMBRE CUENTA",
      field: "displayName",
      width: 400,
      headerClass: "header-blue",
    },
    {
      headerName: "SALDO ANTERIOR",
      headerClass: "header-blue",
      children: [
        {
          headerName: "DEBE",
          field: "debe_ant",
          width: 120,
          valueFormatter: (params) => Number(params.value || 0).toFixed(2),
          cellClass: "numeric-cell",
          headerClass: "header-blue",
        },
        {
          headerName: "HABER",
          field: "haber_ant",
          width: 120,
          valueFormatter: (params) => Number(params.value || 0).toFixed(2),
          cellClass: "numeric-cell",
          headerClass: "header-blue",
        },
      ],
    },
    {
      headerName: "SALDO MES",
      headerClass: "header-blue",
      children: [
        {
          headerName: "DEBE",
          field: "debe_mes",
          width: 120,
          valueFormatter: (params) => Number(params.value || 0).toFixed(2),
          cellClass: "numeric-cell",
          headerClass: "header-blue",
        },
        {
          headerName: "HABER",
          field: "haber_mes",
          width: 120,
          valueFormatter: (params) => Number(params.value || 0).toFixed(2),
          cellClass: "numeric-cell",
          headerClass: "header-blue",
        },
      ],
    },
    {
      headerName: "SALDO ACTUAL",
      headerClass: "header-blue",
      children: [
        {
          headerName: "DEBE",
          field: "debe_act",
          width: 120,
          valueFormatter: (params) => Number(params.value || 0).toFixed(2),
          cellClass: "numeric-cell",
          headerClass: "header-blue",
        },
        {
          headerName: "HABER",
          field: "haber_act",
          width: 120,
          valueFormatter: (params) => Number(params.value || 0).toFixed(2),
          cellClass: "numeric-cell",
          headerClass: "header-blue",
        },
      ],
    },
    {
      headerName: "TIPO",
      field: "tipo",
      width: 80,
      headerClass: "header-blue",
    },
  ]

  gridOptions = {
    columnDefs,
    defaultColDef: {
      sortable: false,
      resizable: true,
      suppressMenu: true,
    },
    rowData: [],
    suppressAggFuncInHeader: true,
    animateRows: true,
    getRowStyle: (params) => {
      const nivel = params.data?.nivel || 1
      return {
        backgroundColor: nivel === 1 ? "#f0f0f0" : nivel === 2 ? "#f5f5f5" : "#ffffff",
        fontWeight: nivel <= 2 ? "bold" : "normal",
        fontSize: nivel === 1 ? "1.1em" : "inherit",
      }
    },
    onGridReady: (params) => {
      params.api.sizeColumnsToFit()
    },
  }

  // Update CSS styles to match the image
  const styleElement = document.createElement("style")
  styleElement.textContent = `
    .ag-theme-alpine {
      --ag-header-height: 30px;
      --ag-header-foreground-color: white;
      --ag-header-background-color: #f5f7f7;
      --ag-header-cell-hover-background-color: #0ea5e9;
      --ag-row-hover-color: #f0f0f0;
      --ag-selected-row-background-color: #b7e4ff;
      --ag-alpine-active-color: #0ea5e9;
    }
    .header-blue {
      background-color: #0ea5e9 !important;
      color: white !important;
    }
    .header-gray {
      background-color: #AEAEAE !important;
      color: white !important;
    }
    .ag-header-group-cell {
      background-color: #0ea5e9 !important;
      color: white !important;
    }
    .numeric-cell {
      text-align: right;
    }
    .ag-row {
      border-bottom: 1px solid #e2e2e2;
    }
    .ag-header-cell-text {
      font-weight: 500;
    }
    .ag-header-group-cell-label {
      justify-content: center;
    }
    .ag-header-cell-label {
      justify-content: center;
    }
    #loading-overlay {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background-color: rgba(255, 255, 255, 0.8);
      display: flex;
      justify-content: center;
      align-items: center;
      z-index: 9999;
    }

    .loading-content {
      background-color: white;
      padding: 20px;
      border-radius: 8px;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
      text-align: center;
    }

    .loading-spinner {
      border: 4px solid #f3f3f3;
      border-top: 4px solid #0ea5e9;
      border-radius: 50%;
      width: 40px;
      height: 40px;
      animation: spin 1s linear infinite;
      margin: 0 auto 10px auto;
    }

    .loading-text {
      color: #333;
      font-size: 16px;
      font-weight: 500;
    }

    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
  `
  document.head.appendChild(styleElement)

  const eGridDiv = document.querySelector("#myGrid")
  new agGrid.Grid(eGridDiv, gridOptions)

  loadCuentas()
    .then(() => {
      loadData()
    })
    .catch((error) => {
      console.error("Error al cargar las cuentas:", error)
      alert(`Error al cargar las cuentas: ${error.message}`)
    })

  const btnActualizar = document.getElementById("btnActualizar")
  if (btnActualizar) {
    btnActualizar.addEventListener("click", loadData)
  } else {
    console.error("No se encontró el botón de actualizar")
  }

  // Export to Excel
  document.getElementById("exportExcel").addEventListener("click", () => {
    const currentDateTime = getCurrentDateTime()
    const fechaInicio = document.querySelector('input[name="fecha_inicio"]').value
    const fechaFin = document.querySelector('input[name="fecha_fin"]').value

    const params = {
      fileName: `balance_comprobacion_${getCurrentDateTime().replace(/[/:]/g, "-")}.xlsx`,
      sheetName: "Balance de Comprobación",
      customHeader: [
        ["PESQUERA SAN MIGUEL C. LTDA."],
        ["BALANCE DE COMPROBACIÓN"],
        [`Del ${fechaInicio} al ${fechaFin}`],
        [`Generado el: ${currentDateTime}`],
        [], // Empty row for spacing
      ],
    }
    gridOptions.api.exportDataAsExcel(params)
  })

  // Export to PDF
  document.getElementById("exportPdf").addEventListener("click", () => {
    const doc = new jsPDF("l", "pt", "a4")
    const currentDateTime = getCurrentDateTime()
    const fechaInicio = document.querySelector('input[name="fecha_inicio"]').value
    const fechaFin = document.querySelector('input[name="fecha_fin"]').value

    // Configure font
    doc.setFont("helvetica")

    // Company name
    doc.setFontSize(16)
    doc.text("PESQUERA SAN MIGUEL C. LTDA.", doc.internal.pageSize.width / 2, 40, { align: "center" })

    // Report title
    doc.setFontSize(14)
    doc.text("BALANCE DE COMPROBACIÓN", doc.internal.pageSize.width / 2, 60, { align: "center" })

    // Date range
    doc.setFontSize(12)
    doc.text(`Del ${fechaInicio} al ${fechaFin}`, doc.internal.pageSize.width / 2, 80, { align: "center" })

    // Generation timestamp
    doc.setFontSize(10)
    doc.text(`Generado el: ${currentDateTime}`, doc.internal.pageSize.width - 40, 100, { align: "right" })

    const rows = []
    gridOptions.api.forEachNodeAfterFilterAndSort((node) => {
      if (node.data) {
        rows.push([
          node.data.codigo,
          node.data.nombre,
          Number(node.data.debe_ant).toFixed(2),
          Number(node.data.haber_ant).toFixed(2),
          Number(node.data.debe_mes).toFixed(2),
          Number(node.data.haber_mes).toFixed(2),
          Number(node.data.debe_act).toFixed(2),
          Number(node.data.haber_act).toFixed(2),
          node.data.tipo,
        ])
      }
    })

    doc.autoTable({
      startY: 120, // Increased to accommodate header
      head: [
        ["CÓDIGO", "NOMBRE CUENTA", "DEBE_ANT", "HABER_ANT", "DEBE_MES", "HABER_MES", "DEBE_ACT", "HABER_ACT", "TIPO"],
      ],
      body: rows,
      theme: "grid",
      styles: { fontSize: 8, cellPadding: 2 },
      columnStyles: {
        0: { cellWidth: 60 },
        1: { cellWidth: 200 },
        2: { cellWidth: 70, halign: "right" },
        3: { cellWidth: 70, halign: "right" },
        4: { cellWidth: 70, halign: "right" },
        5: { cellWidth: 70, halign: "right" },
        6: { cellWidth: 70, halign: "right" },
        7: { cellWidth: 70, halign: "right" },
        8: { cellWidth: 40, halign: "center" },
      },
      didDrawPage: (data) => {
        // Add page number at the bottom
        doc.setFontSize(8)
        doc.text(`Página ${data.pageNumber}`, data.settings.margin.left, doc.internal.pageSize.height - 10)
      },
    })

    doc.save(`balance_comprobacion_${getCurrentDateTime().replace(/[/:]/g, "-")}.pdf`)
  })
})

function getCookie(name) {
  let cookieValue = null
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";")
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim()
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}*/

/*
// CODIGO QUE SALEN LAS CUENTAS COMPLETAS HASTA CON CEROS
const { jsPDF } = window.jspdf
let gridOptions

function getCurrentDateTime() {
  const now = new Date()
  return now.toLocaleString("es-EC", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  })
}

const loadCuentas = async () => {
  try {
    const response = await fetch(window.location.pathname, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: new URLSearchParams({
        action: "get_cuentas",
      }),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const cuentas = await response.json()
    const selectInicio = document.querySelector('select[name="cuenta_inicio"]')
    const selectFin = document.querySelector('select[name="cuenta_fin"]')

    cuentas.forEach((cuenta) => {
      const option = new Option(`${cuenta.codigo} - ${cuenta.nombre}`, cuenta.codigo)
      selectInicio.add(option.cloneNode(true))
      selectFin.add(option)
    })

    // Establecer valores por defecto
    selectInicio.value = cuentas[0].codigo
    selectFin.value = cuentas[cuentas.length - 1].codigo
  } catch (error) {
    console.error("Error cargando las cuentas:", error)
    alert(`Error al cargar las cuentas: ${error.message}`)
  }
}

function showLoadingMessage() {
  const loadingDiv = document.createElement("div")
  loadingDiv.id = "loading-overlay"
  loadingDiv.innerHTML = `
    <div class="loading-content">
      <div class="loading-spinner"></div>
      <div class="loading-text">Procesando datos...</div>
    </div>
  `
  document.body.appendChild(loadingDiv)
}

function hideLoadingMessage() {
  const loadingDiv = document.getElementById("loading-overlay")
  if (loadingDiv) {
    loadingDiv.remove()
  }
}

const loadData = async () => {
  try {
    showLoadingMessage() // Show loading message before starting

    const fechaInicioElement = document.querySelector('input[name="fecha_inicio"]')
    const fechaFinElement = document.querySelector('input[name="fecha_fin"]')
    const cuentaInicioElement = document.querySelector('select[name="cuenta_inicio"]')
    const cuentaFinElement = document.querySelector('select[name="cuenta_fin"]')

    if (!fechaInicioElement || !fechaFinElement || !cuentaInicioElement || !cuentaFinElement) {
      throw new Error("No se encontraron todos los elementos necesarios en el formulario")
    }

    const fechaInicio = fechaInicioElement.value
    const fechaFin = fechaFinElement.value
    const cuentaInicio = cuentaInicioElement.value
    const cuentaFin = cuentaFinElement.value

    if (!fechaInicio || !fechaFin) {
      throw new Error("Las fechas de inicio y fin son requeridas")
    }

    const response = await fetch(window.location.pathname, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: new URLSearchParams({
        action: "searchdata_psm",
        fecha_inicio: fechaInicio,
        fecha_fin: fechaFin,
        cuenta_inicio: cuentaInicio,
        cuenta_fin: cuentaFin,
      }),
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    if (data.error) {
      throw new Error(data.error)
    }

    // Process data to create tree structure
    //const processedData = data.map((item) => ({
    //  ...item,
    //  displayName: `${"  ".repeat(item.nivel - 1)}${item.codigo} ${item.nombre}`,
    //}))

    gridOptions.api.setRowData(data)
  } catch (error) {
    console.error("Error realizando la petición AJAX:", error)
    alert(`Error al cargar los datos: ${error.message}`)
  } finally {
    hideLoadingMessage() // Hide loading message when done
  }
}

document.addEventListener("DOMContentLoaded", () => {
  // Set default dates to today
  const today = new Date().toISOString().split("T")[0]
  const fechaInicioElement = document.querySelector('input[name="fecha_inicio"]')
  const fechaFinElement = document.querySelector('input[name="fecha_fin"]')
  if (fechaInicioElement) fechaInicioElement.value = today
  if (fechaFinElement) fechaFinElement.value = today

  const columnDefs = [
    {
      headerName: "CÓDIGO",
      field: "codigo",
      width: 80,
      sortable: true,
      headerClass: "header-blue",
      valueFormatter: (params) => {
        return params.value.toString()
      },
    },
    {
      headerName: "NOMBRE CUENTA",
      field: "nombre",
      width: 350,
      headerClass: "header-blue",
      cellRenderer: (params) => {
        const nivel = params.data.nivel || 1
        const indent = "&nbsp;".repeat((nivel - 1) * 4)
        return `${indent}${params.value}`
      },
    },
    {
      headerName: "SALDO ANTERIOR",
      headerClass: "header-blue",
      children: [
        {
          headerName: "DEBE",
          field: "debe_ant",
          width: 100,
          valueFormatter: (params) => Number(params.value || 0).toFixed(2),
          cellClass: "numeric-cell",
          headerClass: "header-blue",
          aggFunc: "sum",
        },
        {
          headerName: "HABER",
          field: "haber_ant",
          width: 100,
          valueFormatter: (params) => Number(params.value || 0).toFixed(2),
          cellClass: "numeric-cell",
          headerClass: "header-blue",
          aggFunc: "sum",
        },
      ],
    },
    {
      headerName: "SALDO MES",
      headerClass: "header-blue",
      children: [
        {
          headerName: "DEBE",
          field: "debe_mes",
          width: 100,
          valueFormatter: (params) => Number(params.value || 0).toFixed(2),
          cellClass: "numeric-cell",
          headerClass: "header-blue",
          aggFunc: "sum",
        },
        {
          headerName: "HABER",
          field: "haber_mes",
          width: 100,
          valueFormatter: (params) => Number(params.value || 0).toFixed(2),
          cellClass: "numeric-cell",
          headerClass: "header-blue",
          aggFunc: "sum",
        },
      ],
    },
    {
      headerName: "SALDO ACTUAL",
      headerClass: "header-blue",
      children: [
        {
          headerName: "DEBE",
          field: "debe_act",
          width: 100,
          valueFormatter: (params) => Number(params.value || 0).toFixed(2),
          cellClass: "numeric-cell",
          headerClass: "header-blue",
          aggFunc: "sum",
        },
        {
          headerName: "HABER",
          field: "haber_act",
          width: 100,
          valueFormatter: (params) => Number(params.value || 0).toFixed(2),
          cellClass: "numeric-cell",
          headerClass: "header-blue",
          aggFunc: "sum",
        },
      ],
    },
    {
      headerName: "TIPO",
      field: "tipo",
      width: 60,
      headerClass: "header-blue",
      cellStyle: { textAlign: "center" },
    },
  ]

  gridOptions = {
    columnDefs,
    defaultColDef: {
      sortable: false,
      resizable: true,
      suppressMenu: true,
    },
    rowData: [],
    suppressAggFuncInHeader: true,
    animateRows: true,
    getRowStyle: (params) => {
      const nivel = params.data?.nivel || 1
      return {
        backgroundColor: nivel === 1 ? "#f0f0f0" : "#ffffff",
        fontWeight: nivel === 1 ? "bold" : "normal",
      }
    },
    onGridReady: (params) => {
      params.api.sizeColumnsToFit()
    },
  }

  // Update CSS styles
  const styleElement = document.createElement("style")
  styleElement.textContent = `
    .ag-theme-alpine {
      --ag-header-height: 30px;
      --ag-header-foreground-color: white;
      --ag-header-background-color: #f5f7f7;
      --ag-header-cell-hover-background-color: #00b0f0;
      --ag-row-hover-color: #f0f0f0;
      --ag-selected-row-background-color: #e6f3ff;
      --ag-odd-row-background-color: #ffffff;
      --ag-row-border-color: #d9d9d9;
      --ag-font-size: 11px;
    }
    .header-blue {
      background-color: #00b0f0 !important;
      color: white !important;
    }
    .ag-header-group-cell {
      background-color: #00b0f0 !important;
      color: white !important;
    }
    .numeric-cell {
      text-align: right;
    }
    .ag-row {
      border-bottom: 1px solid #e2e2e2;
    }
    .ag-row-even {
      background-color: #ffffff;
    }
    .ag-row-odd {
      background-color: #f8f8f8;
    }
    .ag-header-cell-text {
      font-weight: bold;
    }
    .ag-header-group-cell-label {
      justify-content: center;
    }
    .ag-header-cell-label {
      justify-content: center;
    }
    /!* Style for the last row (totals) *!/
    .ag-row-last {
      background-color: #e5f6fd !important;
      font-weight: bold !important;
    }
    #loading-overlay {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background-color: rgba(255, 255, 255, 0.8);
      display: flex;
      justify-content: center;
      align-items: center;
      z-index: 9999;
    }

    .loading-content {
      background-color: white;
      padding: 20px;
      border-radius: 8px;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
      text-align: center;
    }

    .loading-spinner {
      border: 4px solid #f3f3f3;
      border-top: 4px solid #0ea5e9;
      border-radius: 50%;
      width: 40px;
      height: 40px;
      animation: spin 1s linear infinite;
      margin: 0 auto 10px auto;
    }

    .loading-text {
      color: #333;
      font-size: 16px;
      font-weight: 500;
    }

    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
  `
  document.head.appendChild(styleElement)

  const eGridDiv = document.querySelector("#myGrid")
  new agGrid.Grid(eGridDiv, gridOptions)

  loadCuentas()
    .then(() => {
      loadData()
    })
    .catch((error) => {
      console.error("Error al cargar las cuentas:", error)
      alert(`Error al cargar las cuentas: ${error.message}`)
    })

  const btnActualizar = document.getElementById("btnActualizar")
  if (btnActualizar) {
    btnActualizar.addEventListener("click", loadData)
  } else {
    console.error("No se encontró el botón de actualizar")
  }

  // Export to Excel
  document.getElementById("exportExcel").addEventListener("click", () => {
    const currentDateTime = getCurrentDateTime()
    const fechaInicio = document.querySelector('input[name="fecha_inicio"]').value
    const fechaFin = document.querySelector('input[name="fecha_fin"]').value

    // Create empty cells array for proper column spanning
    const emptyCells = Array(8).fill("")

    const params = {
      fileName: `balance_comprobacion_${getCurrentDateTime().replace(/[/:]/g, "-")}.xlsx`,
      sheetName: "Balance de Comprobación",
      processRowGroupCallback: (params) => params.node.key,
      processHeaderCallback: (params) => params.column.getColDef().headerName,
      processDataCallback: (params) => {
        if (params.column.getColId() === "codigo") {
          return {
            value: "'" + params.value,
            type: "String",
          }
        }
        if (
          ["debe_ant", "haber_ant", "debe_mes", "haber_mes", "debe_act", "haber_act"].includes(params.column.getColId())
        ) {
          return {
            value: params.value,
            type: "Number",
            numberFormat: "#,##0.00",
          }
        }
        return params.value
      },
      prependContent: [
        ["PESQUERA SAN MIGUEL C. LTDA.", ...emptyCells],
        ["BALANCE DE COMPROBACIÓN", ...emptyCells],
        [`Del ${fechaInicio} al ${fechaFin}`, ...emptyCells],
        [`Generado el: ${currentDateTime}`, ...emptyCells],
        [], // Empty row before headers
      ],
      rowHeight: 30,
      headerRowHeight: 30,
      fontSize: 12,
      cellStyles: {
        0: {
          // First row (company name)
          font: { bold: true, size: 14 },
          alignment: { horizontal: "center" },
        },
        1: {
          // Second row (report title)
          font: { bold: true, size: 12 },
          alignment: { horizontal: "center" },
        },
        2: {
          // Third row (date range)
          font: { size: 11 },
          alignment: { horizontal: "center" },
        },
        3: {
          // Fourth row (generation timestamp)
          font: { size: 10 },
          alignment: { horizontal: "right" },
        },
      },
    }

    gridOptions.api.exportDataAsExcel(params)
  })

  // Export to PDF
  document.getElementById("exportPdf").addEventListener("click", () => {
    const doc = new jsPDF("l", "pt", "a4")
    const currentDateTime = getCurrentDateTime()
    const fechaInicio = document.querySelector('input[name="fecha_inicio"]').value
    const fechaFin = document.querySelector('input[name="fecha_fin"]').value

    // Configure font
    doc.setFont("helvetica")

    // Company name
    doc.setFontSize(16)
    doc.text("PESQUERA SAN MIGUEL C. LTDA.", doc.internal.pageSize.width / 2, 40, { align: "center" })

    // Report title
    doc.setFontSize(14)
    doc.text("BALANCE DE COMPROBACIÓN", doc.internal.pageSize.width / 2, 60, { align: "center" })

    // Date range
    doc.setFontSize(12)
    doc.text(`Del ${fechaInicio} al ${fechaFin}`, doc.internal.pageSize.width / 2, 80, { align: "center" })

    // Generation timestamp
    doc.setFontSize(10)
    doc.text(`Generado el: ${currentDateTime}`, doc.internal.pageSize.width - 40, 100, { align: "right" })

    const rows = []
    gridOptions.api.forEachNodeAfterFilterAndSort((node) => {
      if (node.data) {
        rows.push([
          node.data.codigo,
          node.data.nombre,
          Number(node.data.debe_ant).toFixed(2),
          Number(node.data.haber_ant).toFixed(2),
          Number(node.data.debe_mes).toFixed(2),
          Number(node.data.haber_mes).toFixed(2),
          Number(node.data.debe_act).toFixed(2),
          Number(node.data.haber_act).toFixed(2),
          node.data.tipo,
        ])
      }
    })

    doc.autoTable({
      startY: 120, // Increased to accommodate header
      head: [
        ["CÓDIGO", "NOMBRE CUENTA", "DEBE_ANT", "HABER_ANT", "DEBE_MES", "HABER_MES", "DEBE_ACT", "HABER_ACT", "TIPO"],
      ],
      body: rows,
      theme: "grid",
      styles: { fontSize: 8, cellPadding: 2 },
      columnStyles: {
        0: { cellWidth: 60 },
        1: { cellWidth: 200 },
        2: { cellWidth: 70, halign: "right" },
        3: { cellWidth: 70, halign: "right" },
        4: { cellWidth: 70, halign: "right" },
        5: { cellWidth: 70, halign: "right" },
        6: { cellWidth: 70, halign: "right" },
        7: { cellWidth: 70, halign: "right" },
        8: { cellWidth: 40, halign: "center" },
      },
      didDrawPage: (data) => {
        // Add page number at the bottom
        doc.setFontSize(8)
        doc.text(`Página ${data.pageNumber}`, data.settings.margin.left, doc.internal.pageSize.height - 10)
      },
    })

    doc.save(`balance_comprobacion_${getCurrentDateTime().replace(/[/:]/g, "-")}.pdf`)
  })
})

function getCookie(name) {
  let cookieValue = null
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";")
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim()
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}
*/


/*// codigo que sale excluidos los valores mayores a 0, van los que tienen valores nomas
const { jsPDF } = window.jspdf
let gridOptions

function getCurrentDateTime() {
  const now = new Date()
  return now.toLocaleString("es-EC", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  })
}

const loadCuentas = async () => {
  try {
    const response = await fetch(window.location.pathname, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: new URLSearchParams({
        action: "get_cuentas",
      }),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const cuentas = await response.json()
    const selectInicio = document.querySelector('select[name="cuenta_inicio"]')
    const selectFin = document.querySelector('select[name="cuenta_fin"]')

    cuentas.forEach((cuenta) => {
      const option = new Option(`${cuenta.codigo} - ${cuenta.nombre}`, cuenta.codigo)
      selectInicio.add(option.cloneNode(true))
      selectFin.add(option)
    })

    // Establecer valores por defecto
    selectInicio.value = cuentas[0].codigo
    selectFin.value = cuentas[cuentas.length - 1].codigo
  } catch (error) {
    console.error("Error cargando las cuentas:", error)
    alert(`Error al cargar las cuentas: ${error.message}`)
  }
}

function showLoadingMessage() {
  const loadingDiv = document.createElement("div")
  loadingDiv.id = "loading-overlay"
  loadingDiv.innerHTML = `
    <div class="loading-content">
      <div class="loading-spinner"></div>
      <div class="loading-text">Procesando datos...</div>
    </div>
  `
  document.body.appendChild(loadingDiv)
}

function hideLoadingMessage() {
  const loadingDiv = document.getElementById("loading-overlay")
  if (loadingDiv) {
    loadingDiv.remove()
  }
}

function updateTotals(data) {
  const totals = {
    debe_ant: 0,
    haber_ant: 0,
    debe_mes: 0,
    haber_mes: 0,
    debe_act: 0,
    haber_act: 0,
  }

  // Only sum parent accounts (codes starting with 1-6)
  data.forEach((item) => {
    if (["1", "2", "3", "4", "5", "6"].includes(item.codigo.split(".")[0])) {
      totals.debe_ant += Number.parseFloat(item.debe_ant || 0)
      totals.haber_ant += Number.parseFloat(item.haber_ant || 0)
      totals.debe_mes += Number.parseFloat(item.debe_mes || 0)
      totals.haber_mes += Number.parseFloat(item.haber_mes || 0)
      totals.debe_act += Number.parseFloat(item.debe_act || 0)
      totals.haber_act += Number.parseFloat(item.haber_act || 0)
    }
  })

  const totalRow = [
    {
      codigo: "",
      nombre: "Total de las cuentas",
      debe_ant: totals.debe_ant.toFixed(2),
      haber_ant: totals.haber_ant.toFixed(2),
      debe_mes: totals.debe_mes.toFixed(2),
      haber_mes: totals.haber_mes.toFixed(2),
      debe_act: totals.debe_act.toFixed(2),
      haber_act: totals.haber_act.toFixed(2),
      tipo: "",
    },
  ]

  gridOptions.api.setPinnedBottomRowData(totalRow)
  return totals
}

const loadData = async () => {
  try {
    showLoadingMessage()

    const fechaInicioElement = document.querySelector('input[name="fecha_inicio"]')
    const fechaFinElement = document.querySelector('input[name="fecha_fin"]')
    const cuentaInicioElement = document.querySelector('select[name="cuenta_inicio"]')
    const cuentaFinElement = document.querySelector('select[name="cuenta_fin"]')

    if (!fechaInicioElement || !fechaFinElement || !cuentaInicioElement || !cuentaFinElement) {
      throw new Error("No se encontraron todos los elementos necesarios en el formulario")
    }

    const fechaInicio = fechaInicioElement.value
    const fechaFin = fechaFinElement.value
    const cuentaInicio = cuentaInicioElement.value
    const cuentaFin = cuentaFinElement.value

    if (!fechaInicio || !fechaFin) {
      throw new Error("Las fechas de inicio y fin son requeridas")
    }

    const response = await fetch(window.location.pathname, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: new URLSearchParams({
        action: "searchdata_psm",
        fecha_inicio: fechaInicio,
        fecha_fin: fechaFin,
        cuenta_inicio: cuentaInicio,
        cuenta_fin: cuentaFin,
      }),
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    if (data.error) {
      throw new Error(data.error)
    }

    // Add this check to ensure correct values
    data.forEach((item) => {
      ;["debe_ant", "haber_ant", "debe_mes", "haber_mes", "debe_act", "haber_act"].forEach((field) => {
        item[field] = Number.parseFloat(item[field] || 0).toFixed(2)
      })
    })

    // Filter data to show only rows with values greater than zero
    const filteredData = data.filter(
      (item) =>
        Math.abs(item.debe_ant) > 0 ||
        Math.abs(item.haber_ant) > 0 ||
        Math.abs(item.debe_mes) > 0 ||
        Math.abs(item.haber_mes) > 0 ||
        Math.abs(item.debe_act) > 0 ||
        Math.abs(item.haber_act) > 0,
    )

    // Get the selected account type
    const tipoSelect = document.querySelector('select[name="tipo_cuenta"]')
    const tipoSeleccionado = tipoSelect ? tipoSelect.value : ""

    // Apply type filter if a type is selected
    const dataFiltrada = filteredData.filter((item) => {
      if (!tipoSeleccionado) return true // Show all if no type selected
      return item.tipo === tipoSeleccionado
    })

    updateTotals(dataFiltrada)
    gridOptions.api.setRowData(dataFiltrada)
  } catch (error) {
    console.error("Error realizando la petición AJAX:", error)
    alert(`Error al cargar los datos: ${error.message}`)
  } finally {
    hideLoadingMessage()
  }
}

document.addEventListener("DOMContentLoaded", () => {
  // Set default dates to today
  const today = new Date().toISOString().split("T")[0]
  const fechaInicioElement = document.querySelector('input[name="fecha_inicio"]')
  const fechaFinElement = document.querySelector('input[name="fecha_fin"]')
  if (fechaInicioElement) fechaInicioElement.value = today
  if (fechaFinElement) fechaFinElement.value = today

  const columnDefs = [
    {
      headerName: "CÓDIGO",
      field: "codigo",
      width: 80,
      sortable: true,
      headerClass: "header-blue",
      valueFormatter: (params) => {
        return params.value.toString()
      },
    },
    {
      headerName: "NOMBRE CUENTA",
      field: "nombre",
      width: 350,
      headerClass: "header-blue",
      cellRenderer: (params) => {
        const nivel = params.data.nivel || 1
        const indent = "&nbsp;".repeat((nivel - 1) * 4)
        return `${indent}${params.value}`
      },
    },
    {
      headerName: "SALDO ANTERIOR",
      headerClass: "header-blue",
      children: [
        {
          headerName: "DEBE",
          field: "debe_ant",
          width: 100,
          valueFormatter: (params) => Number.parseFloat(params.value || 0).toFixed(2),
          cellClass: "numeric-cell",
          headerClass: "header-blue",
          aggFunc: "sum",
          showColumnHeader: true, // Add this line
        },
        {
          headerName: "HABER",
          field: "haber_ant",
          width: 100,
          valueFormatter: (params) => Number.parseFloat(params.value || 0).toFixed(2),
          cellClass: "numeric-cell",
          headerClass: "header-blue",
          aggFunc: "sum",
          showColumnHeader: true, // Add this line
        },
      ],
    },
    {
      headerName: "SALDO MES",
      headerClass: "header-blue",
      children: [
        {
          headerName: "DEBE",
          field: "debe_mes",
          width: 100,
          valueFormatter: (params) => Number.parseFloat(params.value || 0).toFixed(2),
          cellClass: "numeric-cell",
          headerClass: "header-blue",
          aggFunc: "sum",
        },
        {
          headerName: "HABER",
          field: "haber_mes",
          width: 100,
          valueFormatter: (params) => Number.parseFloat(params.value || 0).toFixed(2),
          cellClass: "numeric-cell",
          headerClass: "header-blue",
          aggFunc: "sum",
        },
      ],
    },
    {
      headerName: "SALDO ACTUAL",
      headerClass: "header-blue",
      children: [
        {
          headerName: "DEBE",
          field: "debe_act",
          width: 100,
          valueFormatter: (params) => Number.parseFloat(params.value || 0).toFixed(2),
          cellClass: "numeric-cell",
          headerClass: "header-blue",
          aggFunc: "sum",
        },
        {
          headerName: "HABER",
          field: "haber_act",
          width: 100,
          valueFormatter: (params) => Number.parseFloat(params.value || 0).toFixed(2),
          cellClass: "numeric-cell",
          headerClass: "header-blue",
          aggFunc: "sum",
        },
      ],
    },
    {
      headerName: "TIPO",
      field: "tipo",
      width: 60,
      headerClass: "header-blue",
      cellStyle: { textAlign: "center" },
    },
  ]

  gridOptions = {
    columnDefs,
    defaultColDef: {
      sortable: false,
      resizable: true,
      suppressMenu: true,
    },
    rowData: [],
    suppressAggFuncInHeader: true,
    animateRows: true,
    getRowStyle: (params) => {
      const nivel = params.data?.nivel || 1
      return {
        backgroundColor: nivel === 1 ? "#f0f0f0" : "#ffffff",
        fontWeight: nivel === 1 ? "bold" : "normal",
      }
    },
    onGridReady: (params) => {
      params.api.sizeColumnsToFit()
    },
    // Add pinnedBottom configuration
    pinnedBottomRowData: [
      {
        codigo: "",
        nombre: "Total de las cuentas",
        debe_ant: 0,
        haber_ant: 0,
        debe_mes: 0,
        haber_mes: 0,
        debe_act: 0,
        haber_act: 0,
        tipo: "",
      },
    ],
  }

  // Update CSS styles
  const styleElement = document.createElement("style")
  styleElement.textContent = `
    .ag-theme-alpine {
      --ag-header-height: 30px;
      --ag-header-foreground-color: white;
      --ag-header-background-color: #f5f7f7;
      --ag-header-cell-hover-background-color: #00b0f0;
      --ag-row-hover-color: #f0f0f0;
      --ag-selected-row-background-color: #e6f3ff;
      --ag-odd-row-background-color: #ffffff;
      --ag-row-border-color: #d9d9d9;
      --ag-font-size: 11px;
    }
    .header-blue {
      background-color: #00b0f0 !important;
      color: white !important;
    }
    .ag-header-group-cell {
      background-color: #00b0f0 !important;
      color: white !important;
    }
    .numeric-cell {
      text-align: right;
    }
    .ag-row {
      border-bottom: 1px solid #e2e2e2;
    }
    .ag-row-even {
      background-color: #ffffff;
    }
    .ag-row-odd {
      background-color: #f8f8f8;
    }
    .ag-header-cell-text {
      font-weight: bold;
    }
    .ag-header-group-cell-label {
      justify-content: center;
    }
    .ag-header-cell-label {
      justify-content: center;
    }
    /!* Style for the last row (totals) *!/
    .ag-row-last {
      background-color: #e5f6fd !important;
      font-weight: bold !important;
    }
    #loading-overlay {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background-color: rgba(255, 255, 255, 0.8);
      display: flex;
      justify-content: center;
      align-items: center;
      z-index: 9999;
    }

    .loading-content {
      background-color: white;
      padding: 20px;
      border-radius: 8px;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
      text-align: center;
    }

    .loading-spinner {
      border: 4px solid #f3f3f3;
      border-top: 4px solid #0ea5e9;
      border-radius: 50%;
      width: 40px;
      height: 40px;
      animation: spin 1s linear infinite;
      margin: 0 auto 10px auto;
    }

    .loading-text {
      color: #333;
      font-size: 16px;
      font-weight: 500;
    }

    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }

    .ag-header-cell {
      overflow: visible !important;
    }
  `
  document.head.appendChild(styleElement)

  const eGridDiv = document.querySelector("#myGrid")
  new agGrid.Grid(eGridDiv, gridOptions)

  loadCuentas()
    .then(() => {
      loadData()
    })
    .catch((error) => {
      console.error("Error al cargar las cuentas:", error)
      alert(`Error al cargar las cuentas: ${error.message}`)
    })

  const btnActualizar = document.getElementById("btnActualizar")
  if (btnActualizar) {
    btnActualizar.addEventListener("click", loadData)
  } else {
    console.error("No se encontró el botón de actualizar")
  }

  // Add after the btnActualizar event listener
  const tipoSelect = document.getElementById("tipo_cuenta")
  if (tipoSelect) {
    tipoSelect.addEventListener("change", loadData)
  } else {
    console.error("No se encontró el selector de tipo de cuenta")
  }

  // Export to Excel
  document.getElementById("exportExcel").addEventListener("click", () => {
    const currentDateTime = getCurrentDateTime()
    const fechaInicio = document.querySelector('input[name="fecha_inicio"]').value
    const fechaFin = document.querySelector('input[name="fecha_fin"]').value

    // Create empty cells array for proper column spanning
    const emptyCells = Array(8).fill("")

    const params = {
      fileName: `balance_comprobacion_${getCurrentDateTime().replace(/[/:]/g, "-")}.xlsx`,
      sheetName: "Balance de Comprobación",
      processRowGroupCallback: (params) => params.node.key,
      processHeaderCallback: (params) => params.column.getColDef().headerName,
      processDataCallback: (params) => {
        if (params.column.getColId() === "codigo") {
          return {
            value: "'" + params.value,
            type: "String",
          }
        }
        if (
          ["debe_ant", "haber_ant", "debe_mes", "haber_mes", "debe_act", "haber_act"].includes(params.column.getColId())
        ) {
          return {
            value: params.value,
            type: "Number",
            numberFormat: "#,##0.00",
          }
        }
        return params.value
      },
      prependContent: [
        ["PESQUERA SAN MIGUEL C. LTDA.", ...emptyCells],
        ["BALANCE DE COMPROBACIÓN", ...emptyCells],
        [`Del ${fechaInicio} al ${fechaFin}`, ...emptyCells],
        [`Generado el: ${currentDateTime}`, ...emptyCells],
        [], // Empty row before headers
      ],
      rowHeight: 30,
      headerRowHeight: 30,
      fontSize: 12,
      cellStyles: {
        0: {
          // First row (company name)
          font: { bold: true, size: 14 },
          alignment: { horizontal: "center" },
        },
        1: {
          // Second row (report title)
          font: { bold: true, size: 12 },
          alignment: { horizontal: "center" },
        },
        2: {
          // Third row (date range)
          font: { size: 11 },
          alignment: { horizontal: "center" },
        },
        3: {
          // Fourth row (generation timestamp)
          font: { size: 10 },
          alignment: { horizontal: "right" },
        },
      },
    }

    const rows = []
    const totals = {
      debe_ant: 0,
      haber_ant: 0,
      debe_mes: 0,
      haber_mes: 0,
      debe_act: 0,
      haber_act: 0,
    }

    gridOptions.api.forEachNodeAfterFilterAndSort((node) => {
      if (node.data) {
        rows.push([
          node.data.codigo,
          node.data.nombre,
          Number(node.data.debe_ant).toFixed(2),
          Number(node.data.haber_ant).toFixed(2),
          Number(node.data.debe_mes).toFixed(2),
          Number(node.data.haber_mes).toFixed(2),
          Number(node.data.debe_act).toFixed(2),
          Number(node.data.haber_act).toFixed(2),
          node.data.tipo,
        ])

        // Only sum parent accounts (codes starting with 1-6)
        if (["1", "2", "3", "4", "5", "6"].includes(node.data.codigo.split(".")[0])) {
          totals.debe_ant += Number(node.data.debe_ant) || 0
          totals.haber_ant += Number(node.data.haber_ant) || 0
          totals.debe_mes += Number(node.data.debe_mes) || 0
          totals.haber_mes += Number(node.data.haber_mes) || 0
          totals.debe_act += Number(node.data.debe_act) || 0
          totals.haber_act += Number(node.data.haber_act) || 0
        }
      }
    })

    // Add totals row
    rows.push([
      "",
      "Total de las cuentas",
      totals.debe_ant.toFixed(2),
      totals.haber_ant.toFixed(2),
      totals.debe_mes.toFixed(2),
      totals.haber_mes.toFixed(2),
      totals.debe_act.toFixed(2),
      totals.haber_act.toFixed(2),
      "",
    ])

    gridOptions.api.exportDataAsExcel(params)
  })

  // Export to PDF
  document.getElementById("exportPdf").addEventListener("click", () => {
    const doc = new jsPDF("l", "pt", "a4")
    const currentDateTime = getCurrentDateTime()
    const fechaInicio = document.querySelector('input[name="fecha_inicio"]').value
    const fechaFin = document.querySelector('input[name="fecha_fin"]').value

    // Configure font
    doc.setFont("helvetica")

    // Company name
    doc.setFontSize(16)
    doc.text("PESQUERA SAN MIGUEL C. LTDA.", doc.internal.pageSize.width / 2, 40, { align: "center" })

    // Report title
    doc.setFontSize(14)
    doc.text("BALANCE DE COMPROBACIÓN", doc.internal.pageSize.width / 2, 60, { align: "center" })

    // Date range
    doc.setFontSize(12)
    doc.text(`Del ${fechaInicio} al ${fechaFin}`, doc.internal.pageSize.width / 2, 80, { align: "center" })

    // Generation timestamp
    doc.setFontSize(10)
    doc.text(`Generado el: ${currentDateTime}`, doc.internal.pageSize.width - 40, 100, { align: "right" })

    const rows = []
    const totals = {
      debe_ant: 0,
      haber_ant: 0,
      debe_mes: 0,
      haber_mes: 0,
      debe_act: 0,
      haber_act: 0,
    }

    gridOptions.api.forEachNodeAfterFilterAndSort((node) => {
      if (node.data) {
        rows.push([
          node.data.codigo,
          node.data.nombre,
          Number(node.data.debe_ant).toFixed(2),
          Number(node.data.haber_ant).toFixed(2),
          Number(node.data.debe_mes).toFixed(2),
          Number(node.data.haber_mes).toFixed(2),
          Number(node.data.debe_act).toFixed(2),
          Number(node.data.haber_act).toFixed(2),
          node.data.tipo,
        ])

        // Accumulate totals only for parent accounts (codes 1-6)
        if (["1", "2", "3", "4", "5", "6"].includes(node.data.codigo.split(".")[0])) {
          totals.debe_ant += Number(node.data.debe_ant) || 0
          totals.haber_ant += Number(node.data.haber_ant) || 0
          totals.debe_mes += Number(node.data.debe_mes) || 0
          totals.haber_mes += Number(node.data.haber_mes) || 0
          totals.debe_act += Number(node.data.debe_act) || 0
          totals.haber_act += Number(node.data.haber_act) || 0
        }
      }
    })

    // Add totals row
    rows.push([
      "",
      "Total de las cuentas",
      totals.debe_ant.toFixed(2),
      totals.haber_ant.toFixed(2),
      totals.debe_mes.toFixed(2),
      totals.haber_mes.toFixed(2),
      totals.debe_act.toFixed(2),
      totals.haber_act.toFixed(2),
      "",
    ])

    doc.autoTable({
      startY: 120,
      head: [
        [
          { content: "CÓDIGO", rowSpan: 2, styles: { fillColor: [255, 218, 185] } },
          { content: "NOMBRE CUENTA", rowSpan: 2, styles: { fillColor: [255, 218, 185] } },
          { content: "SALDO ANTERIOR", colSpan: 2, styles: { fillColor: [255, 218, 185] } },
          { content: "SALDO MES", colSpan: 2, styles: { fillColor: [255, 218, 185] } },
          { content: "SALDO ACTUAL", colSpan: 2, styles: { fillColor: [255, 218, 185] } },
          { content: "TIPO", rowSpan: 2, styles: { fillColor: [255, 218, 185] } },
        ],
        [
          "",
          "",
          { content: "DEBE", styles: { fillColor: [255, 218, 185] } },
          { content: "HABER", styles: { fillColor: [255, 218, 185] } },
          { content: "DEBE", styles: { fillColor: [255, 218, 185] } },
          { content: "HABER", styles: { fillColor: [255, 218, 185] } },
          { content: "DEBE", styles: { fillColor: [255, 218, 185] } },
          { content: "HABER", styles: { fillColor: [255, 218, 185] } },
          "",
        ],
      ],
      body: rows,
      theme: "grid",
      styles: {
        fontSize: 8,
        cellPadding: 2,
        halign: "center",
        valign: "middle",
        lineWidth: 0.5,
      },
      columnStyles: {
        0: { cellWidth: 60, halign: "left" },
        1: { cellWidth: 200, halign: "left" },
        2: { cellWidth: 70, halign: "right" },
        3: { cellWidth: 70, halign: "right" },
        4: { cellWidth: 70, halign: "right" },
        5: { cellWidth: 70, halign: "right" },
        6: { cellWidth: 70, halign: "right" },
        7: { cellWidth: 70, halign: "right" },
        8: { cellWidth: 40, halign: "center" },
      },
      headStyles: {
        fillColor: [255, 218, 185],
        textColor: [0, 0, 0],
        fontSize: 8,
        fontStyle: "bold",
        halign: "center",
        valign: "middle",
      },
      // Style for the totals row
      didParseCell: (data) => {
        if (data.row.index === rows.length - 1) {
          data.cell.styles.fontStyle = "bold"
          data.cell.styles.fillColor = [240, 240, 240]
        }
      },
      didDrawPage: (data) => {
        // Add page number at the bottom
        doc.setFontSize(8)
        doc.text(`Página ${data.pageNumber}`, data.settings.margin.left, doc.internal.pageSize.height - 10)
      },
    })

    doc.save(`balance_comprobacion_${getCurrentDateTime().replace(/[/:]/g, "-")}.pdf`)
  })
})

function getCookie(name) {
  let cookieValue = null
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";")
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim()
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}*/

// CASI BIEN
/*// codigo que sale excluidos los valores mayores a 0, van los que tienen valores nomas
const { jsPDF } = window.jspdf
let gridOptions

function getCurrentDateTime() {
  const now = new Date()
  return now.toLocaleString("es-EC", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  })
}

const loadCuentas = async () => {
  try {
    const response = await fetch(window.location.pathname, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: new URLSearchParams({
        action: "get_cuentas",
      }),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const cuentas = await response.json()
    const selectInicio = document.querySelector('select[name="cuenta_inicio"]')
    const selectFin = document.querySelector('select[name="cuenta_fin"]')

    cuentas.forEach((cuenta) => {
      const option = new Option(`${cuenta.codigo} - ${cuenta.nombre}`, cuenta.codigo)
      selectInicio.add(option.cloneNode(true))
      selectFin.add(option)
    })

    // Establecer valores por defecto
    selectInicio.value = cuentas[0].codigo
    selectFin.value = cuentas[cuentas.length - 1].codigo
  } catch (error) {
    console.error("Error cargando las cuentas:", error)
    alert(`Error al cargar las cuentas: ${error.message}`)
  }
}

function showLoadingMessage() {
  const loadingDiv = document.createElement("div")
  loadingDiv.id = "loading-overlay"
  loadingDiv.innerHTML = `
    <div class="loading-content">
      <div class="loading-spinner"></div>
      <div class="loading-text">Procesando datos...</div>
    </div>
  `
  document.body.appendChild(loadingDiv)
}

function hideLoadingMessage() {
  const loadingDiv = document.getElementById("loading-overlay")
  if (loadingDiv) {
    loadingDiv.remove()
  }
}

function updateTotals(data) {
  const totals = {
    debe_ant: 0,
    haber_ant: 0,
    debe_mes: 0,
    haber_mes: 0,
    debe_act: 0,
    haber_act: 0,
  }

  // Only sum parent accounts (codes starting with 1-6)
  data.forEach((item) => {
    if (["1", "2", "3", "4", "5", "6"].includes(item.codigo.split(".")[0])) {
      totals.debe_ant += Number.parseFloat(item.debe_ant || 0)
      totals.haber_ant += Number.parseFloat(item.haber_ant || 0)
      totals.debe_mes += Number.parseFloat(item.debe_mes || 0)
      totals.haber_mes += Number.parseFloat(item.haber_mes || 0)
      totals.debe_act += Number.parseFloat(item.debe_act || 0)
      totals.haber_act += Number.parseFloat(item.haber_act || 0)
    }
  })

  // Verify overall balance
  const totalDebeAnt = totals.debe_ant
  const totalHaberAnt = totals.haber_ant
  const totalDebeMes = totals.debe_mes
  const totalHaberMes = totals.haber_mes
  const totalDebeAct = totals.debe_act
  const totalHaberAct = totals.haber_act

  console.log("Balance verification:")
  console.log(`Saldo Anterior: DEBE=${totalDebeAnt.toFixed(2)}, HABER=${totalHaberAnt.toFixed(2)}`)
  console.log(`Saldo Mes: DEBE=${totalDebeMes.toFixed(2)}, HABER=${totalHaberMes.toFixed(2)}`)
  console.log(`Saldo Actual: DEBE=${totalDebeAct.toFixed(2)}, HABER=${totalHaberAct.toFixed(2)}`)

  if (Math.abs(totalDebeAct - totalHaberAct) > 0.01) {
    console.warn("Balance de Comprobación is not balanced!")
  }

  const totalRow = [
    {
      codigo: "",
      nombre: "Total de las cuentas",
      debe_ant: totalDebeAnt.toFixed(2),
      haber_ant: totalHaberAnt.toFixed(2),
      debe_mes: totalDebeMes.toFixed(2),
      haber_mes: totalHaberMes.toFixed(2),
      debe_act: totalDebeAct.toFixed(2),
      haber_act: totalHaberAct.toFixed(2),
      tipo: "",
    },
  ]

  gridOptions.api.setPinnedBottomRowData(totalRow)
  return totals
}

const loadData = async () => {
  try {
    showLoadingMessage()

    const fechaInicioElement = document.querySelector('input[name="fecha_inicio"]')
    const fechaFinElement = document.querySelector('input[name="fecha_fin"]')
    const cuentaInicioElement = document.querySelector('select[name="cuenta_inicio"]')
    const cuentaFinElement = document.querySelector('select[name="cuenta_fin"]')

    if (!fechaInicioElement || !fechaFinElement || !cuentaInicioElement || !cuentaFinElement) {
      throw new Error("No se encontraron todos los elementos necesarios en el formulario")
    }

    const fechaInicio = fechaInicioElement.value
    const fechaFin = fechaFinElement.value
    const cuentaInicio = cuentaInicioElement.value
    const cuentaFin = cuentaFinElement.value

    if (!fechaInicio || !fechaFin) {
      throw new Error("Las fechas de inicio y fin son requeridas")
    }

    const response = await fetch(window.location.pathname, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: new URLSearchParams({
        action: "searchdata_psm",
        fecha_inicio: fechaInicio,
        fecha_fin: fechaFin,
        cuenta_inicio: cuentaInicio,
        cuenta_fin: cuentaFin,
      }),
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    if (data.error) {
      throw new Error(data.error)
    }

    // Parse all values to ensure they're numbers
    data.forEach((item) => {
      ;["debe_ant", "haber_ant", "debe_mes", "haber_mes"].forEach((field) => {
        item[field] = Number.parseFloat(item[field] || 0)
      })

      // Calculate Saldo Actual
      const debeActual = item.debe_ant + item.debe_mes - item.haber_ant - item.haber_mes
      const haberActual = item.haber_ant + item.haber_mes - item.debe_ant - item.debe_mes

      item.debe_act = debeActual > 0 ? debeActual.toFixed(2) : "0.00"
      item.haber_act = haberActual > 0 ? haberActual.toFixed(2) : "0.00"
      // Format all values to 2 decimal places after calculations
      ;["debe_ant", "haber_ant", "debe_mes", "haber_mes", "debe_act", "haber_act"].forEach((field) => {
        item[field] = Number(item[field]).toFixed(2)
      })
    })

    // Verify balance for each account
    data.forEach((item) => {
      const debeTotal = Number(item.debe_act)
      const haberTotal = Number(item.haber_act)

      // For Balance de Comprobación, we keep both DEBE and HABER values
      // The verification is done by ensuring totals match at the account level
      if (Math.abs(debeTotal - haberTotal) > 0.01) {
        console.warn(`Account ${item.codigo} is not balanced: DEBE=${debeTotal}, HABER=${haberTotal}`)
      }
    })

    // Filter data to show only rows with values greater than zero
    const filteredData = data.filter(
      (item) =>
        Math.abs(item.debe_ant) > 0 ||
        Math.abs(item.haber_ant) > 0 ||
        Math.abs(item.debe_mes) > 0 ||
        Math.abs(item.haber_mes) > 0 ||
        Math.abs(item.debe_act) > 0 ||
        Math.abs(item.haber_act) > 0,
    )

    // Get the selected account type
    const tipoSelect = document.querySelector('select[name="tipo_cuenta"]')
    const tipoSeleccionado = tipoSelect ? tipoSelect.value : ""

    // Apply type filter if a type is selected
    const dataFiltrada = filteredData.filter((item) => {
      if (!tipoSeleccionado) return true // Show all if no type selected
      return item.tipo === tipoSeleccionado
    })

    updateTotals(dataFiltrada)
    gridOptions.api.setRowData(dataFiltrada)
  } catch (error) {
    console.error("Error realizando la petición AJAX:", error)
    alert(`Error al cargar los datos: ${error.message}`)
  } finally {
    hideLoadingMessage()
  }
}

document.addEventListener("DOMContentLoaded", () => {
  // Set default dates to today
  const today = new Date().toISOString().split("T")[0]
  const fechaInicioElement = document.querySelector('input[name="fecha_inicio"]')
  const fechaFinElement = document.querySelector('input[name="fecha_fin"]')
  if (fechaInicioElement) fechaInicioElement.value = today
  if (fechaFinElement) fechaFinElement.value = today

  const columnDefs = [
    {
      headerName: "CÓDIGO",
      field: "codigo",
      width: 80,
      sortable: true,
      headerClass: "header-blue",
      valueFormatter: (params) => {
        return params.value.toString()
      },
    },
    {
      headerName: "NOMBRE CUENTA",
      field: "nombre",
      width: 350,
      headerClass: "header-blue",
      cellRenderer: (params) => {
        const nivel = params.data.nivel || 1
        const indent = "&nbsp;".repeat((nivel - 1) * 4)
        return `${indent}${params.value}`
      },
    },
    {
      headerName: "SALDO ANTERIOR",
      headerClass: "header-blue",
      children: [
        {
          headerName: "DEBE",
          field: "debe_ant",
          width: 100,
          valueFormatter: (params) => Number.parseFloat(params.value || 0).toFixed(2),
          cellClass: "numeric-cell",
          headerClass: "header-blue",
          aggFunc: "sum",
          showColumnHeader: true, // Add this line
        },
        {
          headerName: "HABER",
          field: "haber_ant",
          width: 100,
          valueFormatter: (params) => Number.parseFloat(params.value || 0).toFixed(2),
          cellClass: "numeric-cell",
          headerClass: "header-blue",
          aggFunc: "sum",
          showColumnHeader: true, // Add this line
        },
      ],
    },
    {
      headerName: "SALDO MES",
      headerClass: "header-blue",
      children: [
        {
          headerName: "DEBE",
          field: "debe_mes",
          width: 100,
          valueFormatter: (params) => Number.parseFloat(params.value || 0).toFixed(2),
          cellClass: "numeric-cell",
          headerClass: "header-blue",
          aggFunc: "sum",
        },
        {
          headerName: "HABER",
          field: "haber_mes",
          width: 100,
          valueFormatter: (params) => Number.parseFloat(params.value || 0).toFixed(2),
          cellClass: "numeric-cell",
          headerClass: "header-blue",
          aggFunc: "sum",
        },
      ],
    },
    {
      headerName: "SALDO ACTUAL",
      headerClass: "header-blue",
      children: [
        {
          headerName: "DEBE",
          field: "debe_act",
          width: 100,
          valueFormatter: (params) => Number.parseFloat(params.value || 0).toFixed(2),
          cellClass: "numeric-cell",
          headerClass: "header-blue",
          aggFunc: "sum",
        },
        {
          headerName: "HABER",
          field: "haber_act",
          width: 100,
          valueFormatter: (params) => Number.parseFloat(params.value || 0).toFixed(2),
          cellClass: "numeric-cell",
          headerClass: "header-blue",
          aggFunc: "sum",
        },
      ],
    },
    {
      headerName: "TIPO",
      field: "tipo",
      width: 60,
      headerClass: "header-blue",
      cellStyle: { textAlign: "center" },
    },
  ]

  gridOptions = {
    columnDefs,
    defaultColDef: {
      sortable: false,
      resizable: true,
      suppressMenu: true,
    },
    rowData: [],
    suppressAggFuncInHeader: true,
    animateRows: true,
    getRowStyle: (params) => {
      const nivel = params.data?.nivel || 1
      return {
        backgroundColor: nivel === 1 ? "#f0f0f0" : "#ffffff",
        fontWeight: nivel === 1 ? "bold" : "normal",
      }
    },
    onGridReady: (params) => {
      params.api.sizeColumnsToFit()
    },
    // Add pinnedBottom configuration
    pinnedBottomRowData: [
      {
        codigo: "",
        nombre: "Total de las cuentas",
        debe_ant: 0,
        haber_ant: 0,
        debe_mes: 0,
        haber_mes: 0,
        debe_act: 0,
        haber_act: 0,
        tipo: "",
      },
    ],
  }

  // Update CSS styles
  const styleElement = document.createElement("style")
  styleElement.textContent = `
    .ag-theme-alpine {
      --ag-header-height: 30px;
      --ag-header-foreground-color: white;
      --ag-header-background-color: #f5f7f7;
      --ag-header-cell-hover-background-color: #00b0f0;
      --ag-row-hover-color: #f0f0f0;
      --ag-selected-row-background-color: #e6f3ff;
      --ag-odd-row-background-color: #ffffff;
      --ag-row-border-color: #d9d9d9;
      --ag-font-size: 11px;
    }
    .header-blue {
      background-color: #00b0f0 !important;
      color: white !important;
    }
    .ag-header-group-cell {
      background-color: #00b0f0 !important;
      color: white !important;
    }
    .numeric-cell {
      text-align: right;
    }
    .ag-row {
      border-bottom: 1px solid #e2e2e2;
    }
    .ag-row-even {
      background-color: #ffffff;
    }
    .ag-row-odd {
      background-color: #f8f8f8;
    }
    .ag-header-cell-text {
      font-weight: bold;
    }
    .ag-header-group-cell-label {
      justify-content: center;
    }
    .ag-header-cell-label {
      justify-content: center;
    }
    /!* Style for the last row (totals) *!/
    .ag-row-last {
      background-color: #e5f6fd !important;
      font-weight: bold !important;
    }
    #loading-overlay {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background-color: rgba(255, 255, 255, 0.8);
      display: flex;
      justify-content: center;
      align-items: center;
      z-index: 9999;
    }

    .loading-content {
      background-color: white;
      padding: 20px;
      border-radius: 8px;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
      text-align: center;
    }

    .loading-spinner {
      border: 4px solid #f3f3f3;
      border-top: 4px solid #0ea5e9;
      border-radius: 50%;
      width: 40px;
      height: 40px;
      animation: spin 1s linear infinite;
      margin: 0 auto 10px auto;
    }

    .loading-text {
      color: #333;
      font-size: 16px;
      font-weight: 500;
    }

    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }

    .ag-header-cell {
      overflow: visible !important;
    }
  `
  document.head.appendChild(styleElement)

  const eGridDiv = document.querySelector("#myGrid")
  new agGrid.Grid(eGridDiv, gridOptions)

  loadCuentas()
    .then(() => {
      loadData()
    })
    .catch((error) => {
      console.error("Error al cargar las cuentas:", error)
      alert(`Error al cargar las cuentas: ${error.message}`)
    })

  const btnActualizar = document.getElementById("btnActualizar")
  if (btnActualizar) {
    btnActualizar.addEventListener("click", loadData)
  } else {
    console.error("No se encontró el botón de actualizar")
  }

  // Add after the btnActualizar event listener
  const tipoSelect = document.getElementById("tipo_cuenta")
  if (tipoSelect) {
    tipoSelect.addEventListener("change", loadData)
  } else {
    console.error("No se encontró el selector de tipo de cuenta")
  }

  // Export to Excel
  document.getElementById("exportExcel").addEventListener("click", () => {
    const currentDateTime = getCurrentDateTime()
    const fechaInicio = document.querySelector('input[name="fecha_inicio"]').value
    const fechaFin = document.querySelector('input[name="fecha_fin"]').value

    // Create empty cells array for proper column spanning
    const emptyCells = Array(8).fill("")

    const params = {
      fileName: `balance_comprobacion_${getCurrentDateTime().replace(/[/:]/g, "-")}.xlsx`,
      sheetName: "Balance de Comprobación",
      processRowGroupCallback: (params) => params.node.key,
      processHeaderCallback: (params) => params.column.getColDef().headerName,
      processDataCallback: (params) => {
        if (params.column.getColId() === "codigo") {
          return {
            value: "'" + params.value,
            type: "String",
          }
        }
        if (
          ["debe_ant", "haber_ant", "debe_mes", "haber_mes", "debe_act", "haber_act"].includes(params.column.getColId())
        ) {
          return {
            value: params.value,
            type: "Number",
            numberFormat: "#,##0.00",
          }
        }
        return params.value
      },
      prependContent: [
        ["PESQUERA SAN MIGUEL C. LTDA.", ...emptyCells],
        ["BALANCE DE COMPROBACIÓN", ...emptyCells],
        [`Del ${fechaInicio} al ${fechaFin}`, ...emptyCells],
        [`Generado el: ${currentDateTime}`, ...emptyCells],
        [], // Empty row before headers
      ],
      rowHeight: 30,
      headerRowHeight: 30,
      fontSize: 12,
      cellStyles: {
        0: {
          // First row (company name)
          font: { bold: true, size: 14 },
          alignment: { horizontal: "center" },
        },
        1: {
          // Second row (report title)
          font: { bold: true, size: 12 },
          alignment: { horizontal: "center" },
        },
        2: {
          // Third row (date range)
          font: { size: 11 },
          alignment: { horizontal: "center" },
        },
        3: {
          // Fourth row (generation timestamp)
          font: { size: 10 },
          alignment: { horizontal: "right" },
        },
      },
    }

    const rows = []
    const totals = {
      debe_ant: 0,
      haber_ant: 0,
      debe_mes: 0,
      haber_mes: 0,
      debe_act: 0,
      haber_act: 0,
    }

    gridOptions.api.forEachNodeAfterFilterAndSort((node) => {
      if (node.data) {
        rows.push([
          node.data.codigo,
          node.data.nombre,
          Number(node.data.debe_ant).toFixed(2),
          Number(node.data.haber_ant).toFixed(2),
          Number(node.data.debe_mes).toFixed(2),
          Number(node.data.haber_mes).toFixed(2),
          Number(node.data.debe_act).toFixed(2),
          Number(node.data.haber_act).toFixed(2),
          node.data.tipo,
        ])

        // Only sum parent accounts (codes starting with 1-6)
        if (["1", "2", "3", "4", "5", "6"].includes(node.data.codigo.split(".")[0])) {
          totals.debe_ant += Number(node.data.debe_ant) || 0
          totals.haber_ant += Number(node.data.haber_ant) || 0
          totals.debe_mes += Number(node.data.debe_mes) || 0
          totals.haber_mes += Number(node.data.haber_mes) || 0
          totals.debe_act += Number(node.data.debe_act) || 0
          totals.haber_act += Number(node.data.haber_act) || 0
        }
      }
    })

    // Add totals row
    rows.push([
      "",
      "Total de las cuentas",
      totals.debe_ant.toFixed(2),
      totals.haber_ant.toFixed(2),
      totals.debe_mes.toFixed(2),
      totals.haber_mes.toFixed(2),
      totals.debe_act.toFixed(2),
      totals.haber_act.toFixed(2),
      "",
    ])

    gridOptions.api.exportDataAsExcel(params)
  })

  // Export to PDF
  document.getElementById("exportPdf").addEventListener("click", () => {
    const doc = new jsPDF("l", "pt", "a4")
    const currentDateTime = getCurrentDateTime()
    const fechaInicio = document.querySelector('input[name="fecha_inicio"]').value
    const fechaFin = document.querySelector('input[name="fecha_fin"]').value

    // Configure font
    doc.setFont("helvetica")

    // Company name
    doc.setFontSize(16)
    doc.text("PESQUERA SAN MIGUEL C. LTDA.", doc.internal.pageSize.width / 2, 40, { align: "center" })

    // Report title
    doc.setFontSize(14)
    doc.text("BALANCE DE COMPROBACIÓN", doc.internal.pageSize.width / 2, 60, { align: "center" })

    // Date range
    doc.setFontSize(12)
    doc.text(`Del ${fechaInicio} al ${fechaFin}`, doc.internal.pageSize.width / 2, 80, { align: "center" })

    // Generation timestamp
    doc.setFontSize(10)
    doc.text(`Generado el: ${currentDateTime}`, doc.internal.pageSize.width - 40, 100, { align: "right" })

    const rows = []
    const totals = {
      debe_ant: 0,
      haber_ant: 0,
      debe_mes: 0,
      haber_mes: 0,
      debe_act: 0,
      haber_act: 0,
    }

    gridOptions.api.forEachNodeAfterFilterAndSort((node) => {
      if (node.data) {
        rows.push([
          node.data.codigo,
          node.data.nombre,
          Number(node.data.debe_ant).toFixed(2),
          Number(node.data.haber_ant).toFixed(2),
          Number(node.data.debe_mes).toFixed(2),
          Number(node.data.haber_mes).toFixed(2),
          Number(node.data.debe_act).toFixed(2),
          Number(node.data.haber_act).toFixed(2),
          node.data.tipo,
        ])

        // Accumulate totals only for parent accounts (codes 1-6)
        if (["1", "2", "3", "4", "5", "6"].includes(node.data.codigo.split(".")[0])) {
          totals.debe_ant += Number(node.data.debe_ant) || 0
          totals.haber_ant += Number(node.data.haber_ant) || 0
          totals.debe_mes += Number(node.data.debe_mes) || 0
          totals.haber_mes += Number(node.data.haber_mes) || 0
          totals.debe_act += Number(node.data.debe_act) || 0
          totals.haber_act += Number(node.data.haber_act) || 0
        }
      }
    })

    // Add totals row
    rows.push([
      "",
      "Total de las cuentas",
      totals.debe_ant.toFixed(2),
      totals.haber_ant.toFixed(2),
      totals.debe_mes.toFixed(2),
      totals.haber_mes.toFixed(2),
      totals.debe_act.toFixed(2),
      totals.haber_act.toFixed(2),
      "",
    ])

    doc.autoTable({
      startY: 120,
      head: [
        [
          { content: "CÓDIGO", rowSpan: 2, styles: { fillColor: [255, 218, 185] } },
          { content: "NOMBRE CUENTA", rowSpan: 2, styles: { fillColor: [255, 218, 185] } },
          { content: "SALDO ANTERIOR", colSpan: 2, styles: { fillColor: [255, 218, 185] } },
          { content: "SALDO MES", colSpan: 2, styles: { fillColor: [255, 218, 185] } },
          { content: "SALDO ACTUAL", colSpan: 2, styles: { fillColor: [255, 218, 185] } },
          { content: "TIPO", rowSpan: 2, styles: { fillColor: [255, 218, 185] } },
        ],
        [
          "",
          "",
          { content: "DEBE", styles: { fillColor: [255, 218, 185] } },
          { content: "HABER", styles: { fillColor: [255, 218, 185] } },
          { content: "DEBE", styles: { fillColor: [255, 218, 185] } },
          { content: "HABER", styles: { fillColor: [255, 218, 185] } },
          { content: "DEBE", styles: { fillColor: [255, 218, 185] } },
          { content: "HABER", styles: { fillColor: [255, 218, 185] } },
          "",
        ],
      ],
      body: rows,
      theme: "grid",
      styles: {
        fontSize: 8,
        cellPadding: 2,
        halign: "center",
        valign: "middle",
        lineWidth: 0.5,
      },
      columnStyles: {
        0: { cellWidth: 60, halign: "left" },
        1: { cellWidth: 200, halign: "left" },
        2: { cellWidth: 70, halign: "right" },
        3: { cellWidth: 70, halign: "right" },
        4: { cellWidth: 70, halign: "right" },
        5: { cellWidth: 70, halign: "right" },
        6: { cellWidth: 70, halign: "right" },
        7: { cellWidth: 70, halign: "right" },
        8: { cellWidth: 40, halign: "center" },
      },
      headStyles: {
        fillColor: [255, 218, 185],
        textColor: [0, 0, 0],
        fontSize: 8,
        fontStyle: "bold",
        halign: "center",
        valign: "middle",
      },
      // Style for the totals row
      didParseCell: (data) => {
        if (data.row.index === rows.length - 1) {
          data.cell.styles.fontStyle = "bold"
          data.cell.styles.fillColor = [240, 240, 240]
        }
      },
      didDrawPage: (data) => {
        // Add page number at the bottom
        doc.setFontSize(8)
        doc.text(`Página ${data.pageNumber}`, data.settings.margin.left, doc.internal.pageSize.height - 10)
      },
    })

    doc.save(`balance_comprobacion_${getCurrentDateTime().replace(/[/:]/g, "-")}.pdf`)
  })
})

function getCookie(name) {
  let cookieValue = null
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";")
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim()
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}*/


const { jsPDF } = window.jspdf
let gridOptions

const loadData = async () => {
  try {
    showLoadingMessage()

    const fechaInicioElement = document.querySelector('input[name="fecha_inicio"]')
    const fechaFinElement = document.querySelector('input[name="fecha_fin"]')
    const cuentaInicioElement = document.querySelector('select[name="cuenta_inicio"]')
    const cuentaFinElement = document.querySelector('select[name="cuenta_fin"]')

    if (!fechaInicioElement || !fechaFinElement || !cuentaInicioElement || !cuentaFinElement) {
      throw new Error("No se encontraron todos los elementos necesarios en el formulario")
    }

    const fechaInicio = fechaInicioElement.value
    const fechaFin = fechaFinElement.value
    const cuentaInicio = cuentaInicioElement.value
    const cuentaFin = cuentaFinElement.value

    if (!fechaInicio || !fechaFin) {
      throw new Error("Las fechas de inicio y fin son requeridas")
    }

    const response = await fetch(window.location.pathname, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: new URLSearchParams({
        action: "searchdata_psm",
        fecha_inicio: fechaInicio,
        fecha_fin: fechaFin,
        cuenta_inicio: cuentaInicio,
        cuenta_fin: cuentaFin,
      }),
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    if (data.error) {
      throw new Error(data.error)
    }

    // Filter out accounts with all zero values
    const filteredData = data.filter(
      (account) =>
        account.debe_ant !== 0 ||
        account.haber_ant !== 0 ||
        account.debe_mes !== 0 ||
        account.haber_mes !== 0 ||
        account.debe_act !== 0 ||
        account.haber_act !== 0,
    )

    gridOptions.api.setRowData(filteredData)
    updateTotals(gridOptions.api)
  } catch (error) {
    console.error("Error realizando la petición AJAX:", error)
    alert(`Error al cargar los datos: ${error.message}`)
  } finally {
    hideLoadingMessage()
  }
}

function getCurrentDateTime() {
  const now = new Date()
  return now.toLocaleString("es-EC", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  })
}

const loadCuentas = async () => {
  try {
    const response = await fetch(window.location.pathname, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: new URLSearchParams({
        action: "get_cuentas",
      }),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const cuentas = await response.json()
    const selectInicio = document.querySelector('select[name="cuenta_inicio"]')
    const selectFin = document.querySelector('select[name="cuenta_fin"]')

    cuentas.forEach((cuenta) => {
      const option = new Option(`${cuenta.codigo} - ${cuenta.nombre}`, cuenta.codigo)
      selectInicio.add(option.cloneNode(true))
      selectFin.add(option)
    })

    // Establecer valores por defecto
    selectInicio.value = cuentas[0].codigo
    selectFin.value = cuentas[cuentas.length - 1].codigo
  } catch (error) {
    console.error("Error cargando las cuentas:", error)
    alert(`Error al cargar las cuentas: ${error.message}`)
  }
}

function showLoadingMessage() {
  const loadingDiv = document.createElement("div")
  loadingDiv.id = "loading-overlay"
  loadingDiv.innerHTML = `
    <div class="loading-content">
      <div class="loading-spinner"></div>
      <div class="loading-text">Procesando datos...</div>
    </div>
  `
  document.body.appendChild(loadingDiv)
}

function hideLoadingMessage() {
  const loadingDiv = document.getElementById("loading-overlay")
  if (loadingDiv) {
    loadingDiv.remove()
  }
}

document.addEventListener("DOMContentLoaded", () => {
  // Set default dates to today
  const today = new Date().toISOString().split("T")[0]
  const fechaInicioElement = document.querySelector('input[name="fecha_inicio"]')
  const fechaFinElement = document.querySelector('input[name="fecha_fin"]')
  if (fechaInicioElement) fechaInicioElement.value = today
  if (fechaFinElement) fechaFinElement.value = today

  const columnDefs = [
    {
      headerName: "CÓDIGO",
      field: "codigo",
      width: 80,
      sortable: true,
      headerClass: "header-blue",
      valueFormatter: (params) => {
        return params.value.toString()
      },
    },
    {
      headerName: "NOMBRE CUENTA",
      field: "nombre",
      width: 350,
      headerClass: "header-blue",
    },
    {
      headerName: "SALDO ANTERIOR",
      headerClass: "header-blue",
      children: [
        {
          headerName: "DEBE",
          field: "debe_ant",
          width: 100,
          valueFormatter: (params) => Number(params.value || 0).toFixed(2),
          cellClass: "numeric-cell",
          headerClass: "header-blue",
          aggFunc: "sum",
        },
        {
          headerName: "HABER",
          field: "haber_ant",
          width: 100,
          valueFormatter: (params) => Number(params.value || 0).toFixed(2),
          cellClass: "numeric-cell",
          headerClass: "header-blue",
          aggFunc: "sum",
        },
      ],
    },
    {
      headerName: "SALDO MES",
      headerClass: "header-blue",
      children: [
        {
          headerName: "DEBE",
          field: "debe_mes",
          width: 100,
          valueFormatter: (params) => Number(params.value || 0).toFixed(2),
          cellClass: "numeric-cell",
          headerClass: "header-blue",
          aggFunc: "sum",
        },
        {
          headerName: "HABER",
          field: "haber_mes",
          width: 100,
          valueFormatter: (params) => Number(params.value || 0).toFixed(2),
          cellClass: "numeric-cell",
          headerClass: "header-blue",
          aggFunc: "sum",
        },
      ],
    },
    {
      headerName: "SALDO ACTUAL",
      headerClass: "header-blue",
      children: [
        {
          headerName: "DEBE",
          field: "debe_act",
          width: 100,
          valueFormatter: (params) => Number(params.value || 0).toFixed(2),
          cellClass: "numeric-cell",
          headerClass: "header-blue",
          aggFunc: "sum",
        },
        {
          headerName: "HABER",
          field: "haber_act",
          width: 100,
          valueFormatter: (params) => Number(params.value || 0).toFixed(2),
          cellClass: "numeric-cell",
          headerClass: "header-blue",
          aggFunc: "sum",
        },
      ],
    },
    {
      headerName: "TIPO",
      field: "tipo",
      width: 60,
      headerClass: "header-blue",
      cellStyle: { textAlign: "center" },
    },
  ]

  // Actualizar las opciones del grid
  gridOptions = {
    columnDefs,
    defaultColDef: {
      sortable: false,
      resizable: true,
      suppressMenu: true,
    },
    rowData: [],
    suppressAggFuncInHeader: true,
    animateRows: true,
    getRowStyle: (params) => {
      const nivel = params.data?.nivel || 1
      return {
        backgroundColor: nivel === 1 ? "#f0f0f0" : "#ffffff",
        fontWeight: nivel === 1 ? "bold" : "normal",
      }
    },
    suppressRowGroupPanel: true, // Asegurarse de que no se muestre el panel de agrupación
    groupDisplayType: null, // No mostrar columna de grupo
    pinnedBottomRowData: [],
    onGridReady: (params) => {
      params.api.sizeColumnsToFit()
      // Calcular y actualizar totales
      updateTotals(params.api)
    },
    onFilterChanged: (params) => {
      // Actualizar totales cuando cambie el filtro
      updateTotals(params.api)
    },
  }

  // Update CSS styles
  const styleElement = document.createElement("style")
  styleElement.textContent = `
    .ag-theme-alpine {
      --ag-header-height: 30px;
      --ag-header-foreground-color: white;
      --ag-header-background-color: #f5f7f7;
      --ag-header-cell-hover-background-color: #00b0f0;
      --ag-row-hover-color: #f0f0f0;
      --ag-selected-row-background-color: #e6f3ff;
      --ag-odd-row-background-color: #ffffff;
      --ag-row-border-color: #d9d9d9;
      --ag-font-size: 11px;
    }
    .header-blue {
      background-color: #00b0f0 !important;
      color: white !important;
    }
    .ag-header-group-cell {
      background-color: #00b0f0 !important;
      color: white !important;
    }
    .numeric-cell {
      text-align: right;
    }
    .ag-row {
      border-bottom: 1px solid #e2e2e2;
    }
    .ag-row-even {
      background-color: #ffffff;
    }
    .ag-row-odd {
      background-color: #f8f8f8;
    }
    .ag-header-cell-text {
      font-weight: bold;
    }
    .ag-header-group-cell-label {
      justify-content: center;
    }
    .ag-header-cell-label {
      justify-content: center;
    }
    /* Style for the last row (totals) */
    .ag-row-last {
      background-color: #e5f6fd !important;
      font-weight: bold !important;
    }
    #loading-overlay {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background-color: rgba(255, 255, 255, 0.8);
      display: flex;
      justify-content: center;
      align-items: center;
      z-index: 9999;
    }

    .loading-content {
      background-color: white;
      padding: 20px;
      border-radius: 8px;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
      text-align: center;
    }

    .loading-spinner {
      border: 4px solid #f3f3f3;
      border-top: 4px solid #0ea5e9;
      border-radius: 50%;
      width: 40px;
      height: 40px;
      animation: spin 1s linear infinite;
      margin: 0 auto 10px auto;
    }

    .loading-text {
      color: #333;
      font-size: 16px;
      font-weight: 500;
    }

    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
    .ag-theme-alpine .ag-icon-tree-closed,
    .ag-theme-alpine .ag-icon-tree-open {
      color: #00b0f0 !important;
    }

    .ag-theme-alpine .ag-row-group {
      cursor: pointer;
    }
    .ag-theme-alpine .ag-icon-tree-closed::before {
      content: '\\u25B6'; /* Right-pointing triangle */
      color: #00b0f0;
      font-size: 12px;
    }

    .ag-theme-alpine .ag-icon-tree-open::before {
      content: '\\u25BC'; /* Down-pointing triangle */
      color: #00b0f0;
      font-size: 12px;
    }

    .ag-theme-alpine .ag-cell {
      display: flex;
      align-items: center;
      white-space: pre !important;  /* Asegura que se preserven los espacios */
    }
    .ag-theme-alpine .ag-row-pinned {
      background-color: #f0f0f0 !important;
      font-weight: bold !important;
    }
  `
  document.head.appendChild(styleElement)

  const eGridDiv = document.querySelector("#myGrid")
  new agGrid.Grid(eGridDiv, gridOptions)

  loadCuentas()
    .then(() => {
      loadData()
    })
    .catch((error) => {
      console.error("Error al cargar las cuentas:", error)
      alert(`Error al cargar las cuentas: ${error.message}`)
    })

  const btnActualizar = document.getElementById("btnActualizar")
  if (btnActualizar) {
    btnActualizar.addEventListener("click", loadData)
  } else {
    console.error("No se encontró el botón de actualizar")
  }

  // Export to Excel
  document.getElementById("exportExcel").addEventListener("click", () => {
    const currentDateTime = getCurrentDateTime()
    const fechaInicio = document.querySelector('input[name="fecha_inicio"]').value
    const fechaFin = document.querySelector('input[name="fecha_fin"]').value

    // Create empty cells array for proper column spanning
    const emptyCells = Array(9).fill("")

    const params = {
      fileName: `balance_comprobacion_${getCurrentDateTime().replace(/[/:]/g, "-")}.xlsx`,
      sheetName: "Balance de Comprobación",
      processRowGroupCallback: (params) => params.node.key,
      processHeaderCallback: (params) => params.column.getColDef().headerName,
      processDataCallback: (params) => {
        if (params.column.getColId() === "codigo") {
          return {
            value: "'" + params.value,
            type: "String",
          }
        }
        if (params.column.getColId() === "nombre") {
          return {
            value: params.value,
            type: "String",
            style: {
              alignment: { indent: Math.floor((params.value.length - params.value.trimLeft().length) / 2) },
            },
          }
        }
        if (
          ["debe_ant", "haber_ant", "debe_mes", "haber_mes", "debe_act", "haber_act"].includes(params.column.getColId())
        ) {
          return {
            value: params.value,
            type: "Number",
            numberFormat: "#,##0.00",
          }
        }
        return params.value
      },
      prependContent: [
        ["PESQUERA SAN MIGUEL C. LTDA.", ...emptyCells],
        ["BALANCE DE COMPROBACIÓN", ...emptyCells],
        [`Del ${fechaInicio} al ${fechaFin}`, ...emptyCells],
        [`Generado el: ${currentDateTime}`, ...emptyCells],
        [], // Empty row before headers
      ],
      rowHeight: 30,
      headerRowHeight: 30,
      fontSize: 12,
      cellStyles: {
        0: {
          // First row (company name)
          font: { bold: true, size: 14 },
          alignment: { horizontal: "center" },
        },
        1: {
          // Second row (report title)
          font: { bold: true, size: 12 },
          alignment: { horizontal: "center" },
        },
        2: {
          // Third row (date range)
          font: { size: 11 },
          alignment: { horizontal: "center" },
        },
        3: {
          // Fourth row (generation timestamp)
          font: { size: 10 },
          alignment: { horizontal: "right" },
        },
      },
      onlySelected: false,
      allColumns: true,
      shouldRowBeSkipped: (params) => {
        const data = params.node.data
        return !(data.debe_ant || data.haber_ant || data.debe_mes || data.haber_mes || data.debe_act || data.haber_act)
      },
    }

    gridOptions.api.exportDataAsExcel(params)
  })

  // Export to PDF
  document.getElementById("exportPdf").addEventListener("click", () => {
    const doc = new jsPDF("l", "pt", "a4")
    const currentDateTime = getCurrentDateTime()
    const fechaInicio = document.querySelector('input[name="fecha_inicio"]').value
    const fechaFin = document.querySelector('input[name="fecha_fin"]').value

    // Configure font
    doc.setFont("helvetica")

    // Company name
    doc.setFontSize(16)
    doc.text("PESQUERA SAN MIGUEL C. LTDA.", doc.internal.pageSize.width / 2, 40, { align: "center" })

    // Report title
    doc.setFontSize(14)
    doc.text("BALANCE DE COMPROBACIÓN", doc.internal.pageSize.width / 2, 60, { align: "center" })

    // Date range
    doc.setFontSize(12)
    doc.text(`Del ${fechaInicio} al ${fechaFin}`, doc.internal.pageSize.width / 2, 80, { align: "center" })

    // Generation timestamp
    doc.setFontSize(10)
    doc.text(`Generado el: ${currentDateTime}`, doc.internal.pageSize.width - 40, 100, { align: "right" })

    const rows = []
    gridOptions.api.forEachNodeAfterFilterAndSort((node) => {
      if (node.data) {
        const data = node.data
        if (data.debe_ant || data.haber_ant || data.debe_mes || data.haber_mes || data.debe_act || data.haber_act) {
          rows.push([
            data.codigo,
            data.nombre,
            Number(data.debe_ant).toFixed(2),
            Number(data.haber_ant).toFixed(2),
            Number(data.debe_mes).toFixed(2),
            Number(data.haber_mes).toFixed(2),
            Number(data.debe_act).toFixed(2),
            Number(data.haber_act).toFixed(2),
            data.tipo,
          ])
        }
      }
    })

    doc.autoTable({
      startY: 120,
      head: [
        ["CÓDIGO", "NOMBRE CUENTA", "DEBE_ANT", "HABER_ANT", "DEBE_MES", "HABER_MES", "DEBE_ACT", "HABER_ACT", "TIPO"],
      ],
      body: rows,
      theme: "grid",
      styles: { fontSize: 8, cellPadding: 2 },
      columnStyles: {
        0: { cellWidth: 60 },
        1: {
          cellWidth: 200,
          cellPadding: { left: 0 }, // Importante para preservar la indentación
          whiteSpace: "pre", // Preservar espacios
        },
        2: { cellWidth: 70, halign: "right" },
        3: { cellWidth: 70, halign: "right" },
        4: { cellWidth: 70, halign: "right" },
        5: { cellWidth: 70, halign: "right" },
        6: { cellWidth: 70, halign: "right" },
        7: { cellWidth: 70, halign: "right" },
        8: { cellWidth: 40, halign: "center" },
      },
      didDrawPage: (data) => {
        // Add page number at the bottom
        doc.setFontSize(8)
        doc.text(`Página ${data.pageNumber}`, data.settings.margin.left, doc.internal.pageSize.height - 10)
      },
    })

    doc.save(`balance_comprobacion_${getCurrentDateTime().replace(/[/:]/g, "-")}.pdf`)
  })
})

function getCookie(name) {
  let cookieValue = null
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";")
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim()
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}

function updateTotals(gridApi) {
  // Obtener todas las filas visibles (después del filtrado)
  const visibleNodes = []
  gridApi.forEachNodeAfterFilter((node) => {
    if (node.data) {
      visibleNodes.push(node.data)
    }
  })

  // Calcular totales
  const totals = {
    codigo: "",
    nombre: "Total de las cuentas",
    tipo: "",
    debe_ant: 0,
    haber_ant: 0,
    debe_mes: 0,
    haber_mes: 0,
    debe_act: 0,
    haber_act: 0,
  }

  visibleNodes.forEach((row) => {
    totals.debe_ant += Number(row.debe_ant || 0)
    totals.haber_ant += Number(row.haber_ant || 0)
    totals.debe_mes += Number(row.debe_mes || 0)
    totals.haber_mes += Number(row.haber_mes || 0)
    totals.debe_act += Number(row.debe_act || 0)
    totals.haber_act += Number(row.haber_act || 0)
  })

  // Actualizar la fila de totales
  gridApi.setPinnedBottomRowData([totals])
}








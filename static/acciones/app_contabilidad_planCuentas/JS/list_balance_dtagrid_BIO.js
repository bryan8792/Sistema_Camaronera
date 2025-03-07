/*document.addEventListener('DOMContentLoaded', () => {
    const columnDefs = [
        {colId: 'cuenta.codigo', field: 'cuenta.codigo', rowGroup: true, hide: true},
        {colId: 'cuenta.nombre', field: 'cuenta.nombre', rowGroup: true, hide: true},
        {headerName: 'Cuenta Codigo', showRowGroup: 'cuenta.codigo', cellRenderer: 'agGroupCellRenderer',},
        {headerName: 'Cuenta Nombre', showRowGroup: 'cuenta.nombre', cellRenderer: 'agGroupCellRenderer',},
        {headerName: 'Debe', field: 'debe',
            valueFormatter: params => parseFloat(params.value || 0).toFixed(2),
            aggFunc: 'sum'
        },
        {headerName: 'Haber', field: 'haber',
            valueFormatter: params => parseFloat(params.value || 0).toFixed(2),
            aggFunc: 'sum'
        },
        {headerName: 'Debe', field: 'debe',
            valueFormatter: params => parseFloat(params.value || 0).toFixed(2),
            aggFunc: 'sum'
        },
        {headerName: 'Haber', field: 'haber',
            valueFormatter: params => parseFloat(params.value || 0).toFixed(2),
            aggFunc: 'sum'
        },
        {headerName: 'Total Debe',
            valueGetter: params => {
                const debe = parseFloat(params.node.aggData?.debe || 0);
                const haber = parseFloat(params.node.aggData?.haber || 0);
                return debe > haber ? (debe - haber).toFixed(2) : "0.00";
            },
            valueFormatter: params => parseFloat(params.value || 0).toFixed(2),
            cellClass: 'total-cell',
        },
        {headerName: 'Total Haber',
            valueGetter: params => {
                const debe = parseFloat(params.node.aggData?.debe || 0);
                const haber = parseFloat(params.node.aggData?.haber || 0);
                return haber > debe ? (haber - debe).toFixed(2) : "0.00";
            },
            valueFormatter: params => parseFloat(params.value || 0).toFixed(2),
            cellClass: 'total-cell',
        }
    ];

    const gridOptions = {
        columnDefs: columnDefs,
        // groupDisplayType: 'groupRows',
        groupDisplayType: 'custom',
        defaultColDef: {
            sortable: true,
            filter: true,
            resizable: true,
        },
        autoGroupColumnDef: {
            headerName: 'Grupo',
            cellRendererParams: {
                suppressCount: true,
                innerRenderer: params => {
                    // Validar si el nodo actual es una agrupación
                    if (params.node.group) {
                        const codigo = params.node.key || ''; // Clave del grupo (código)
                        const nombre = params.node.aggData ? params.node.aggData['cuenta.nombre'] || '' : ''; // Nombre del grupo
                        return `<strong>${codigo}</strong> - ${nombre}`;
                    } else {
                        // Fallback para nodos sin agrupación
                        return params.value || '';
                    }
                }
            },
        },
        groupIncludeFooter: true,
        animateRows: true,
        suppressAggFuncInHeader: true,
    };

    const eGridDiv = document.querySelector('#myGrid');
    new agGrid.Grid(eGridDiv, gridOptions);

    // Función para cargar los datos
    const loadData = async () => {
        try {
            const response = await fetch( window.location.pathname, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    'action': 'searchdata_bio',
                }),
            });

            const rawData = await response.json();

            if (rawData.error) {
                console.error('Error al cargar los datos:', rawData.error);
                return;
            }

            // Procesar datos: asegurarse de que los valores sean numéricos
            const processedData = rawData.map(item => ({
                ...item,
                debe: parseFloat(item.debe || 0),
                haber: parseFloat(item.haber || 0),
            }));

            // ** Resultado **
            console.log('Datos procesados:', processedData);

            // Establece los datos en la grid
            gridOptions.api.setRowData(processedData);
        } catch (error) {
            console.error('Error realizando la petición AJAX:', error);
        }
    };

    // Llama a la función para cargar los datos
    loadData();

    document.getElementById('exportExcel').addEventListener('click', () => {
        const rowData = [];
        gridOptions.api.forEachNodeAfterFilterAndSort((node) => {
            const data = node.group
                ? {
                      Grupo: node.key,
                      TotalDebe: node.aggData.debe.toFixed(2),
                      TotalHaber: node.aggData.haber.toFixed(2),
                  }
                : {
                      CuentaCodigo: node.data['cuenta.codigo'],
                      CuentaNombre: node.data['cuenta.nombre'],
                      Debe: node.data.debe.toFixed(2),
                      Haber: node.data.haber.toFixed(2),
                  };
            rowData.push(data);
        });

        const worksheet = XLSX.utils.json_to_sheet(rowData);
        const workbook = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(workbook, worksheet, 'Datos');
        XLSX.writeFile(workbook, 'export.xlsx');
    });

    document.getElementById('exportPdf').addEventListener('click', () => {
        const doc = new jspdf.jsPDF();
        const groupedData = [];

        gridOptions.api.forEachNodeAfterFilterAndSort((node) => {
            if (node.group) {
                groupedData.push([`Grupo: ${node.key}`, '', '', '', `Debe: ${node.aggData.debe.toFixed(2)}`, `Haber: ${node.aggData.haber.toFixed(2)}`]);
            } else {
                groupedData.push([
                    node.data['cuenta.codigo'],
                    node.data['cuenta.nombre'],
                    node.data.debe.toFixed(2),
                    node.data.haber.toFixed(2),
                    '',
                    ''
                ]);
            }
        });

        doc.text('Exportación a PDF', 10, 10);

        doc.autoTable({
            head: [['Cuenta Código', 'Cuenta Nombre', 'Debe', 'Haber', 'Total Debe', 'Total Haber']],
            body: groupedData,
            startY: 20
        });

        // Guarda el PDF
        doc.save('balance.pdf');
    });

});*/

// codigo que sale excluidos los valores mayores a 0, van los que tienen valores nomas
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
        action: "searchdata_bio",
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
        ["BIOCASCAJAL CIA. LTDA.", ...emptyCells],
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
}









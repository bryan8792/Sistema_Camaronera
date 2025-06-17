// Variables globales
var tbl_transaccionPlan
var tblSearchPlan
var deb = 0.0,
  hab = 0.0
var date_now = new Date().toISOString().split("T")[0]
const fecha_actual = new Date()

// Variables globales para paginación y optimización
var currentPage = 1
var totalPages = 1
var isLoadingMore = false
var allPlanData = [] // Array para almacenar todos los datos cargados
var currentSearchTerm = ""
var planCuentasCache = null
var lastLoadTime = null
var CACHE_DURATION = 3600000 // 1 hora en milisegundos
var isLoadingPlan = false

// Variables para búsqueda mejorada
var isSearchActive = false
var originalSearchTerm = ""

// Estilos CSS completos
const compactStyles = `
.search-container {
  background-color: #f8f9fa;
  border-radius: 6px;
  padding: 10px;
  border: 1px solid #dee2e6;
  margin-bottom: 10px;
}

.buscar-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

.search-buttons {
  display: flex;
  align-items: center;
}

.search-status {
  text-align: center;
  padding: 5px;
}

.table-warning {
  background-color: #fff3cd !important;
}

.table-success {
  background-color: #d4edda !important;
  border-color: #c3e6cb !important;
}

.table-info {
  background-color: #d1ecf1 !important;
  border-color: #bee5eb !important;
}

mark {
  background-color: #ffeb3b;
  padding: 1px 2px;
  border-radius: 2px;
}

#tblSearchPlan tbody tr.table-warning:hover {
  background-color: #ffeaa7 !important;
}

#tblSearchPlan tbody tr.table-success:hover {
  background-color: #c3e6cb !important;
}

#tblSearchPlan tbody tr.table-info:hover {
  background-color: #bee5eb !important;
}

.buscar-label {
  font-weight: bold;
  color: #495057;
  white-space: nowrap;
  margin: 0;
}

.buscar-input {
  flex: 1;
  min-width: 200px;
}

#load-more-indicator {
  background-color: #f8f9fa;
  border-top: 1px solid #dee2e6;
}

#load-more-indicator td {
  padding: 15px !important;
}

.dataTables_scrollBody::-webkit-scrollbar {
  width: 8px;
}

.dataTables_scrollBody::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.dataTables_scrollBody::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.dataTables_scrollBody::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.spinner-border-sm {
  width: 1rem;
  height: 1rem;
}

.btn-xs {
  padding: 0.15rem 0.3rem;
  font-size: 0.7rem;
  line-height: 1;
  border-radius: 0.2rem;
}

#tblSearchPlan tbody tr:hover {
  background-color: #f5f5f5;
}

.text-danger i {
  font-size: 2rem;
  color: #dc3545;
}

.btn-sm {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
}

.temporary-alert {
  margin-bottom: 10px;
}

.search-buttons .btn {
  margin-left: 5px;
}
`

var $ = window.jQuery

var vents = {
  items: {
    codigo: 0,
    comprobante: "",
    tip_cuenta: "",
    direccion: "",
    descripcion: "",
    ruc: "",
    fecha: "",
    products: [],
  },
  get_ids: function () {
    var ids = []
    $.each(this.items.products, (key, value) => {
      ids.push(value.id)
    })
    return ids
  },
  calculate_invoice: function () {
    var debe = 0.0,
      haber = 0.0,
      detalle = ""
    $.each(this.items.products, (pos, dict) => {
      dict.pos = pos
      detalle = dict.detalle
      debe += Number.parseFloat(dict.debe || 0)
      haber += Number.parseFloat(dict.haber || 0)
    })
    this.items.detalle = detalle
    this.items.debe = debe
    this.items.haber = haber
    calculos_prod(this.items.products, debe, haber)
  },
  add: function (item) {
    this.items.products.push(item)
    this.list()
  },
  list: function () {
    this.calculate_invoice()

    if ($.fn.DataTable.isDataTable("#tbl_transaccionPlan")) {
      $("#tbl_transaccionPlan").DataTable().destroy()
      $("#tbl_transaccionPlan tbody").empty()
    }

    tbl_transaccionPlan = $("#tbl_transaccionPlan").DataTable({
      language: {
        lengthMenu: "Mostrar _MENU_",
        zeroRecords: "Sin resultados",
        info: "_START_ al _END_ de _TOTAL_",
        infoEmpty: "0 registros",
        infoFiltered: "(de _MAX_)",
        sSearch: "Buscar:",
        oPaginate: {
          sFirst: "«",
          sLast: "»",
          sNext: "›",
          sPrevious: "‹",
        },
        sProcessing: "...",
      },
      dom: "rtip",
      bPaginate: false,
      responsive: true,
      autoWidth: false,
      bFilter: false,
      scrollY: "535px",
      destroy: true,
      data: this.items.products,
      columns: [
        { data: "id", width: "3%" },
        { data: "codigo", width: "10%" },
        { data: "nombre", width: "20%" },
        { data: "detalle", width: "47%" },
        { data: "debe", width: "10%" },
        { data: "haber", width: "10%" },
      ],
      columnDefs: [
        {
          targets: [0],
          class: "text-center",
          orderable: false,
          render: (data, type, row) =>
            '<a rel="remove" class="btn btn-danger btn-xs btn-flat" style="color: white;"><i class="fas fa-trash-alt"></i></a>',
        },
        {
          targets: [1],
          class: "text-left",
          orderable: false,
          render: (data, type, row) => data,
        },
        {
          targets: [2],
          class: "text-left",
          orderable: false,
          render: (data, type, row) => data,
        },
        {
          targets: [-3],
          class: "text-center",
          orderable: false,
          render: (data, type, row) =>
            '<input type="text" name="detalle" class="form-control form-control-sm text-center border-0" autocomplete="off" value="' +
            (row.detalle != null ? row.detalle : "") +
            '">',
        },
        {
          targets: [-2],
          class: "text-center",
          orderable: false,
          render: (data, type, row) =>
            '<input type="text" name="debe" class="form-control form-control-sm text-center border-0" autocomplete="off" value="' +
            Number.parseFloat(row.debe > 0 ? row.debe : 0).toFixed(2) +
            '">',
        },
        {
          targets: [-1],
          class: "text-center",
          orderable: false,
          render: (data, type, row) =>
            '<input type="text" name="haber" class="form-control form-control-sm text-center border-0" autocomplete="off" value="' +
            Number.parseFloat(row.haber > 0 ? row.haber : 0).toFixed(2) +
            '">',
        },
      ],
      rowCallback(row, data, index) {
        var tr = $(row).closest("tr")

        tr.find('input[name="debe"]').blur(() => {
          vents.calculate_invoice()
        })

        tr.find('input[name="haber"]').blur(() => {
          vents.calculate_invoice()
        })
      },
      initComplete: (settings, json) => {
        // Inicialización completa
      },
    })
  },
}

function formatRepo(repo) {
  if (repo.loading) {
    return repo.text
  }

  var option = $(
    '<div class="wrapper container p-1">' +
      '<div class="row">' +
      '<div class="col-lg-1">' +
      "<i class='fa fa-sort-amount-down-alt'></i>" +
      "</div>" +
      '<div class="col-lg-11">' +
      '<p class="mb-0 small">' +
      "<b>Codigo:</b> " +
      repo.codigo +
      " | " +
      "<b>Nombre:</b> " +
      repo.nombre +
      " | " +
      "<b>Nivel:</b> " +
      repo.nivel +
      (repo.cuenta_padre ? " | <b>Cuenta Padre:</b> " + repo.cuenta_padre : "") +
      "</p>" +
      "</div>" +
      "</div>" +
      "</div>",
  )

  return option
}

// Función optimizada para cargar el plan de cuentas con paginación
function loadPlanCuentasBIO(resetData = true, searchTerm = "") {
  if (resetData) {
    currentPage = 1
    allPlanData = []
    currentSearchTerm = searchTerm

    $("#table-tree").html(
      '<tr><td colspan="4" class="text-center"><div class="spinner-border text-primary spinner-border-sm" role="status"></div><p class="mt-1 small">Cargando datos...</p></td></tr>',
    )
  }

  // Verificar caché
  if (
    currentPage === 1 &&
    !searchTerm &&
    planCuentasCache !== null &&
    new Date().getTime() - lastLoadTime < CACHE_DURATION
  ) {
    console.log("Usando datos en caché para la primera página")
    allPlanData = [...planCuentasCache]
    renderPlanCuentasOptimized()
    return
  }

  if (isLoadingPlan || isLoadingMore) return

  if (currentPage === 1) {
    isLoadingPlan = true
  } else {
    isLoadingMore = true
  }

  var ids = vents.get_ids()

  $.ajax({
    url: window.location.pathname,
    type: "POST",
    data: {
      action: "search_plan",
      ids: JSON.stringify(ids),
      empresa: "BIO",
      page: currentPage,
      page_size: 500,
      search: searchTerm || "",
    },
    dataType: "json",
    timeout: 30000,
    headers: {
      "X-CSRFToken": getCookie("csrftoken"),
    },
    success: (response) => {
      console.log(`Página ${currentPage} cargada:`, response)

      if (response.error) {
        console.error("Error del servidor:", response.error)
        showErrorMessage(response.error)
        return
      }

      const data = response.data || response
      const pagination = response.pagination

      if (pagination) {
        totalPages = pagination.total_pages
      } else {
        totalPages = 1
      }

      if (currentPage === 1) {
        allPlanData = [...data]
        if (!searchTerm) {
          planCuentasCache = [...data]
          lastLoadTime = new Date().getTime()
        }
      } else {
        allPlanData = [...allPlanData, ...data]
      }

      renderPlanCuentasOptimized()

      console.log(`Total de registros cargados: ${allPlanData.length}`)
    },
    error: (error) => {
      console.error("Error al cargar datos:", error)
      showErrorMessage("Error al cargar los datos. Por favor, intente nuevamente.")
    },
    complete: () => {
      isLoadingPlan = false
      isLoadingMore = false
    },
  })
}

// Nueva función para cargar todas las cuentas y posicionar en la encontrada
function loadPlanCuentasAndPosition(searchTerm) {
  currentPage = 1
  allPlanData = []

  $("#table-tree").html(
    '<tr><td colspan="4" class="text-center"><div class="spinner-border text-primary spinner-border-sm" role="status"></div><p class="mt-1 small">Buscando cuenta y cargando plan completo...</p></td></tr>',
  )

  if (isLoadingPlan) return
  isLoadingPlan = true

  var ids = vents.get_ids()

  $.ajax({
    url: window.location.pathname,
    type: "POST",
    data: {
      action: "search_plan",
      ids: JSON.stringify(ids),
      empresa: "BIO",
      page: 1,
      page_size: 5000, // Cargar muchos más registros para encontrar la secuencia
      search: "", // No filtrar en el servidor
    },
    dataType: "json",
    timeout: 60000, // Más tiempo para cargar más datos
    headers: {
      "X-CSRFToken": getCookie("csrftoken"),
    },
    success: (response) => {
      console.log("Datos cargados para posicionamiento:", response)

      if (response.error) {
        console.error("Error del servidor:", response.error)
        showErrorMessage(response.error)
        return
      }

      const data = response.data || response
      allPlanData = [...data]

      // Buscar la posición de la cuenta específica
      const foundIndex = findAccountPosition(searchTerm)

      if (foundIndex !== -1) {
        // Renderizar desde la posición encontrada
        renderFromPosition(foundIndex, searchTerm)
      } else {
        // Si no se encuentra, mostrar todo pero resaltar coincidencias parciales
        renderPlanCuentasOptimized()
        updateSearchStatus(`Cuenta "${searchTerm}" no encontrada exactamente. Mostrando coincidencias parciales.`)
      }
    },
    error: (error) => {
      console.error("Error al cargar datos:", error)
      showErrorMessage("Error al cargar los datos. Por favor, intente nuevamente.")
    },
    complete: () => {
      isLoadingPlan = false
    },
  })
}

// Función para encontrar la posición exacta de una cuenta
function findAccountPosition(searchTerm) {
  for (let i = 0; i < allPlanData.length; i++) {
    if (allPlanData[i].codigo === searchTerm) {
      return i
    }
  }

  // Si no encuentra exacta, buscar la más cercana
  for (let i = 0; i < allPlanData.length; i++) {
    if (allPlanData[i].codigo.startsWith(searchTerm)) {
      return i
    }
  }

  return -1
}

// Función para renderizar desde una posición específica
function renderFromPosition(startIndex, searchTerm) {
  // Tomar un rango de cuentas desde la posición encontrada
  const rangeSize = 50 // Mostrar 50 cuentas desde la posición encontrada
  const endIndex = Math.min(startIndex + rangeSize, allPlanData.length)
  const displayData = allPlanData.slice(startIndex, endIndex)

  // Limpiar tabla
  $("#table-tree").empty()

  if ($.fn.DataTable.isDataTable("#tblSearchPlan")) {
    $("#tblSearchPlan").DataTable().destroy()
    $("#tblSearchPlan tbody").empty()
  }

  // Generar HTML para el rango de datos
  var html = ""
  for (var i = 0; i < displayData.length; i++) {
    var item = displayData[i]
    var actualIndex = startIndex + i

    // Resaltar la cuenta buscada y las siguientes
    var shouldHighlight = item.codigo === searchTerm
    var isNext = item.codigo > searchTerm && item.codigo.startsWith(searchTerm.substring(0, 8)) // Misma serie

    var rowClass = shouldHighlight ? "table-success" : isNext ? "table-info" : ""

    html += `
            <tr data-id="${item.id}" data-index="${actualIndex}" class="${rowClass}">
                <td>${item.codigo}</td>
                <td>${item.tipo_cuenta || ""}</td>
                <td>${item.nombre}</td>
                <td class="text-center">
                    ${
                      item.tipo_cuenta === "GENERAL" || item.tipo_cuenta === "G" || item.tipo_cuenta === "GEN"
                        ? '<a rel="neg" class="btn btn-danger btn-xs btn-flat" style="color: white;"><i class="fas fa-times"></i></a>'
                        : '<a rel="add" class="btn btn-success btn-xs btn-flat" style="color: white;"><i class="fas fa-plus"></i></a>'
                    }
                </td>
            </tr>
        `
  }

  $("#table-tree").html(html)

  // Reinicializar DataTable
  initializeDataTableForRange()

  // Actualizar estado
  updateSearchStatus(`Cuenta "${searchTerm}" encontrada. Mostrando ${displayData.length} cuentas desde esta posición.`)

  // Scroll a la cuenta encontrada
  setTimeout(() => {
    scrollToFoundAccount(searchTerm)
  }, 500)
}

// Función para renderizar los datos con resaltado mejorado
function renderPlanCuentasOptimized() {
  if (currentPage === 1) {
    $("#table-tree").empty()

    if ($.fn.DataTable.isDataTable("#tblSearchPlan")) {
      $("#tblSearchPlan").DataTable().destroy()
      $("#tblSearchPlan tbody").empty()
    }
  }

  var html = ""
  for (var i = 0; i < allPlanData.length; i++) {
    var item = allPlanData[i]

    var shouldHighlight = false
    if (originalSearchTerm && originalSearchTerm.length > 0) {
      shouldHighlight =
        item.codigo.toLowerCase().includes(originalSearchTerm.toLowerCase()) ||
        item.nombre.toLowerCase().includes(originalSearchTerm.toLowerCase()) ||
        (item.tipo_cuenta && item.tipo_cuenta.toLowerCase().includes(originalSearchTerm.toLowerCase()))
    }

    var rowClass = shouldHighlight ? "table-warning" : ""

    html += `
            <tr data-id="${item.id}" class="${rowClass}">
                <td>${highlightText(item.codigo, originalSearchTerm)}</td>
                <td>
                  ${highlightText(item.tipo_cuenta === "GENERAL" ? "GEN" : "DET", originalSearchTerm)}
                </td>
                <td>${highlightText(item.nombre, originalSearchTerm)}</td>
                <td class="text-center">
                    ${
                      item.tipo_cuenta === "GENERAL" || item.tipo_cuenta === "G" || item.tipo_cuenta === "GEN"
                        ? '<a rel="neg" class="btn btn-danger btn-xs btn-flat" style="color: white;"><i class="fas fa-times"></i></a>'
                        : '<a rel="add" class="btn btn-success btn-xs btn-flat" style="color: white;"><i class="fas fa-plus"></i></a>'
                    }
                </td>
            </tr>
        `
  }

  $("#table-tree").html(html)

  if (currentPage === 1) {
    initializeDataTable()
  }

  // Actualizar estado de búsqueda
  if (isSearchActive && currentSearchTerm) {
    const foundCount = allPlanData.length
    updateSearchStatus(`Búsqueda: "${originalSearchTerm}" - ${foundCount} resultado(s) encontrado(s)`)
  } else if (isSearchActive && !currentSearchTerm) {
    updateSearchStatus(
      `Búsqueda: "${originalSearchTerm}" - Mostrando todas las cuentas (${allPlanData.length} registros)`,
    )
  }

  if (currentPage < totalPages) {
    addLoadMoreIndicator()
  } else {
    removeLoadMoreIndicator()
  }

  // Scroll al primer resultado resaltado
  if (shouldHighlight && originalSearchTerm) {
    setTimeout(() => {
      scrollToFirstHighlighted()
    }, 500)
  }
}

// Función para resaltar texto
function highlightText(text, searchTerm) {
  if (!searchTerm || !text) return text

  const regex = new RegExp(`(${searchTerm})`, "gi")
  return text.replace(regex, "<mark>$1</mark>")
}

// Función para scroll al primer resultado resaltado
function scrollToFirstHighlighted() {
  const $firstHighlighted = $("#tblSearchPlan tbody tr.table-warning").first()
  if ($firstHighlighted.length > 0) {
    const scrollContainer = $("#tblSearchPlan_wrapper .dataTables_scrollBody")
    const elementTop = $firstHighlighted.position().top
    const containerHeight = scrollContainer.height()
    const scrollTop = elementTop - containerHeight / 2

    scrollContainer.animate(
      {
        scrollTop: scrollTop,
      },
      300,
    )
  }
}

// Función para hacer scroll a la cuenta encontrada
function scrollToFoundAccount(searchTerm) {
  const $foundRow = $("#tblSearchPlan tbody tr.table-success").first()
  if ($foundRow.length > 0) {
    const scrollContainer = $("#tblSearchPlan_wrapper .dataTables_scrollBody")
    const elementTop = $foundRow.position().top

    scrollContainer.animate(
      {
        scrollTop: elementTop - 50, // Dejar un poco de espacio arriba
      },
      500,
    )
  }
}

// Función para inicializar DataTable con altura fija
function initializeDataTable() {
  tblSearchPlan = $("#tblSearchPlan").DataTable({
    ordering: false,
    searching: false,
    paging: false,
    scrollY: "850px",
    scrollCollapse: true,
    autoWidth: false,
    language: {
      zeroRecords: "Sin resultados",
      sInfo: "_START_-_END_ de _TOTAL_",
      infoEmpty: "Tabla vacía",
      sSearch: "Buscar:",
    },
    dom: "rtip",
    destroy: true,
    deferRender: true,
    initComplete: () => {
      setTimeout(() => {
        setupScrollInfinito()
        setupCustomSearchImproved()
      }, 100)
    },
  })
}

// Función para inicializar DataTable para rango específico
function initializeDataTableForRange() {
  tblSearchPlan = $("#tblSearchPlan").DataTable({
    ordering: false,
    searching: false,
    paging: false,
    scrollY: "850px",
    scrollCollapse: true,
    autoWidth: false,
    language: {
      zeroRecords: "Sin resultados",
      sInfo: "_START_-_END_ de _TOTAL_",
      infoEmpty: "Tabla vacía",
    },
    dom: "rtip",
    destroy: true,
    deferRender: true,
  })
}

// Función para configurar scroll infinito
function setupScrollInfinito() {
  const scrollContainer = $("#tblSearchPlan_wrapper .dataTables_scrollBody")

  scrollContainer.off("scroll.infinito").on("scroll.infinito", function () {
    const scrollTop = $(this).scrollTop()
    const scrollHeight = $(this)[0].scrollHeight
    const clientHeight = $(this).height()

    if (scrollTop + clientHeight >= scrollHeight * 0.8) {
      loadMoreData()
    }
  })
}

// Función para cargar más datos
function loadMoreData() {
  if (isLoadingMore || currentPage >= totalPages) return

  console.log(`Cargando página ${currentPage + 1} de ${totalPages}`)

  showLoadingMoreIndicator()

  currentPage++
  loadPlanCuentasBIO(false, currentSearchTerm)
}

// Función para agregar indicador de "cargar más"
function addLoadMoreIndicator() {
  if ($("#load-more-indicator").length === 0) {
    const totalText =
      isSearchActive && currentSearchTerm
        ? `Mostrando ${allPlanData.length} resultados de búsqueda.`
        : `Mostrando ${allPlanData.length} registros.`

    const indicator = `
            <tr id="load-more-indicator">
                <td colspan="4" class="text-center p-2">
                    <small class="text-muted">
                        ${totalText}
                        Haz scroll hacia abajo para cargar más...
                    </small>
                </td>
            </tr>
        `
    $("#table-tree").append(indicator)
  }
}

// Función para mostrar indicador de carga
function showLoadingMoreIndicator() {
  $("#load-more-indicator").html(`
        <td colspan="4" class="text-center p-2">
            <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
            <small class="text-muted ml-2">Cargando más registros...</small>
        </td>
    `)
}

// Función para remover indicador de carga
function removeLoadMoreIndicator() {
  $("#load-more-indicator").remove()
}

// Función para configurar búsqueda personalizada mejorada SIN MODAL
function setupCustomSearchImproved() {
  const $searchContainer = $("<div>").addClass("search-container mb-3")

  const $buscarContainer = $("<div>").addClass("buscar-container")
  const $buscarLabel = $("<label>").addClass("buscar-label").text("BUSCAR:")
  const $buscarInput = $("<input>")
    .attr("type", "search")
    .addClass("form-control form-control-sm buscar-input")
    .attr("placeholder", "Buscar cuenta específica (ej: 201030101104)...")
    .attr("id", "searchPlanInput")

  const $buttonContainer = $("<div>").addClass("search-buttons ml-2")

  const $clearButton = $("<button>")
    .attr("type", "button")
    .addClass("btn btn-sm btn-warning")
    .attr("id", "clearSearchBtn")
    .html('<i class="fas fa-times"></i> Limpiar')
    .css("display", "none")

  const $showAllButton = $("<button>")
    .attr("type", "button")
    .addClass("btn btn-sm btn-success ml-1")
    .attr("id", "showAllBtn")
    .html('<i class="fas fa-eye"></i> Mostrar Todas')
    .css("display", "none")

  // Nuevo botón para buscar desde posición encontrada
  const $continueButton = $("<button>")
    .attr("type", "button")
    .addClass("btn btn-sm btn-info ml-1")
    .attr("id", "continueFromBtn")
    .html('<i class="fas fa-arrow-down"></i> Continuar desde aquí')
    .css("display", "none")

  $buttonContainer.append($clearButton).append($showAllButton).append($continueButton)
  $buscarContainer.append($buscarLabel).append($buscarInput).append($buttonContainer)
  $searchContainer.append($buscarContainer)

  const $searchStatus = $("<div>").addClass("search-status mt-2").attr("id", "searchStatus").css("display", "none")

  $searchContainer.append($searchStatus)

  // Agregar ANTES de la tabla, no dentro de un modal
  $("#tblSearchPlan_wrapper").prepend($searchContainer)

  // Eventos de búsqueda mejorados
  let searchTimeout
  $buscarInput.on("input", function () {
    const searchTerm = $(this).val().trim()

    clearTimeout(searchTimeout)
    searchTimeout = setTimeout(() => {
      if (searchTerm !== currentSearchTerm) {
        if (searchTerm.length > 0) {
          console.log("Realizando búsqueda:", searchTerm)
          performSearchAndPosition(searchTerm)
        } else {
          clearSearch()
        }
      }
    }, 500)
  })

  $clearButton.on("click", () => {
    clearSearch()
  })

  $showAllButton.on("click", () => {
    showAllAccountsFromPosition()
  })

  $continueButton.on("click", () => {
    continueFromFoundPosition()
  })

  $buscarInput.on("keypress", function (e) {
    if (e.which === 13) {
      e.preventDefault()
      const searchTerm = $(this).val().trim()
      if (searchTerm.length > 0) {
        performSearchAndPosition(searchTerm)
      }
    }
  })
}

// Nueva función para buscar y posicionar (no filtrar)
function performSearchAndPosition(searchTerm) {
  isSearchActive = true
  originalSearchTerm = searchTerm
  currentSearchTerm = "" // No filtrar, solo buscar posición

  $("#clearSearchBtn, #showAllBtn, #continueFromBtn").show()

  updateSearchStatus(`Buscando posición de: "${searchTerm}"...`)

  // Cargar todas las cuentas pero buscar la posición específica
  loadPlanCuentasAndPosition(searchTerm)
}

// Función para mostrar todas las cuentas desde la posición encontrada
function showAllAccountsFromPosition() {
  console.log("Mostrando todas las cuentas desde la posición encontrada...")

  // Encontrar el índice de la cuenta original
  const foundIndex = findAccountPosition(originalSearchTerm)

  if (foundIndex !== -1) {
    // Mostrar más cuentas desde esa posición
    const rangeSize = 200 // Mostrar 200 cuentas
    const endIndex = Math.min(foundIndex + rangeSize, allPlanData.length)
    const displayData = allPlanData.slice(foundIndex, endIndex)

    renderExpandedRange(displayData, foundIndex)
    updateSearchStatus(`Mostrando ${displayData.length} cuentas desde "${originalSearchTerm}".`)
  }
}

// Función para continuar desde la posición encontrada
function continueFromFoundPosition() {
  console.log("Continuando desde la posición encontrada...")

  const foundIndex = findAccountPosition(originalSearchTerm)

  if (foundIndex !== -1) {
    // Mostrar cuentas siguientes
    const startIndex = foundIndex + 1 // Empezar desde la siguiente
    const rangeSize = 100
    const endIndex = Math.min(startIndex + rangeSize, allPlanData.length)
    const displayData = allPlanData.slice(startIndex, endIndex)

    renderExpandedRange(displayData, startIndex)
    updateSearchStatus(`Mostrando ${displayData.length} cuentas siguientes a "${originalSearchTerm}".`)
  }
}

// Función para renderizar rango expandido
function renderExpandedRange(displayData, startIndex) {
  $("#table-tree").empty()

  if ($.fn.DataTable.isDataTable("#tblSearchPlan")) {
    $("#tblSearchPlan").DataTable().destroy()
    $("#tblSearchPlan tbody").empty()
  }

  var html = ""
  for (var i = 0; i < displayData.length; i++) {
    var item = displayData[i]
    var actualIndex = startIndex + i

    html += `
            <tr data-id="${item.id}" data-index="${actualIndex}">
                <td>${item.codigo}</td>
                <td>${item.tipo_cuenta || ""}</td>
                <td>${item.nombre}</td>
                <td class="text-center">
                    ${
                      item.tipo_cuenta === "GENERAL" || item.tipo_cuenta === "G" || item.tipo_cuenta === "GEN"
                        ? '<a rel="neg" class="btn btn-danger btn-xs btn-flat" style="color: white;"><i class="fas fa-times"></i></a>'
                        : '<a rel="add" class="btn btn-success btn-xs btn-flat" style="color: white;"><i class="fas fa-plus"></i></a>'
                    }
                </td>
            </tr>
        `
  }

  $("#table-tree").html(html)
  initializeDataTableForRange()
}

// Función mejorada para limpiar búsqueda
function clearSearch() {
  isSearchActive = false
  currentSearchTerm = ""
  originalSearchTerm = ""

  $("#searchPlanInput").val("")
  $("#clearSearchBtn, #showAllBtn, #continueFromBtn").hide()
  $("#searchStatus").hide()

  console.log("Limpiando búsqueda - cargando todas las cuentas")
  loadPlanCuentasBIO(true, "")
}

// Función para actualizar el estado de búsqueda
function updateSearchStatus(message) {
  const $status = $("#searchStatus")
  $status.html(`<small class="text-info"><i class="fas fa-info-circle"></i> ${message}</small>`)
  $status.show()
}

// Función para mostrar mensajes de error
function showErrorMessage(message) {
  $("#table-tree").html(`
        <tr>
            <td colspan="4" class="text-center text-danger p-3">
                <i class="fas fa-exclamation-triangle mb-2"></i>
                <p class="mb-2">${message}</p>
                <button class="btn btn-sm btn-primary" onclick="loadPlanCuentasBIO(true)">
                    <i class="fas fa-redo"></i> Reintentar
                </button>
            </td>
        </tr>
    `)
}

// Función para mostrar mensajes temporales
function showTemporaryMessage(message, type = "info") {
  const alertClass =
    type === "success"
      ? "alert-success"
      : type === "warning"
        ? "alert-warning"
        : type === "error"
          ? "alert-danger"
          : "alert-info"

  const $alert = $(`
    <div class="alert ${alertClass} alert-dismissible fade show temporary-alert" role="alert">
      <i class="fas fa-${type === "success" ? "check" : "info"}-circle"></i> ${message}
      <button type="button" class="close" data-dismiss="alert">
        <span>&times;</span>
      </button>
    </div>
  `)

  // Agregar al inicio del contenedor de la tabla
  $(".table-responsive").prepend($alert)

  setTimeout(() => {
    $alert.fadeOut(() => $alert.remove())
  }, 3000)
}

// FUNCIÓN COMPLETAMENTE CORREGIDA - NO EJECUTAR EN MODO EDICIÓN
function generarCodigoSecuencial(tipoCuenta) {
  const action = $('input[name="action"]').val()

  if (action === 'edit') {
    console.log("MODO EDICIÓN: NO SE EJECUTA GENERACIÓN DE CÓDIGO")
    const codigoOriginal = $('input[name="codigo"]').val()
    console.log("Código original mantenido:", codigoOriginal)
    return Promise.resolve(codigoOriginal)
  }

  // SOLO EN MODO CREACIÓN
  console.log("MODO CREACIÓN: Generando nuevo código...")
  $('input[name="codigo"]').val("Generando...")

  const fechaActual = new Date()
  let mes = fechaActual.getMonth() + 1
  mes = mes < 10 ? "0" + mes : mes.toString()

  let digitoTipo = "1"
  const tipoCuentaTexto = $('select[name="tip_cuenta"] option:selected').text().trim()

  if (tipoCuentaTexto === "COMPROBANTE PAGO") {
    digitoTipo = "2"
  } else if (tipoCuentaTexto === "INGRESO A CAJA") {
    digitoTipo = "3"
  } else if (tipoCuentaTexto === "EGRESO DE CAJA") {
    digitoTipo = "4"
  }

  return new Promise((resolve, reject) => {
    $.ajax({
      url: window.location.pathname,
      type: "POST",
      data: {
        action: "obtener_ultima_secuencia",
        mes: mes,
        tipo: digitoTipo,
      },
      dataType: "json",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
      success: (response) => {
        if (response.es_edicion) {
          console.log("Respuesta de edición - manteniendo código original")
          resolve(response.codigo_original)
          return
        }

        let ultimaSecuencia = 0
        if (response.secuencia !== undefined) {
          ultimaSecuencia = Number.parseInt(response.secuencia)
        }

        const siguienteSecuencia = ultimaSecuencia + 1
        const secuenciaFormateada =
          siguienteSecuencia < 10
            ? "00" + siguienteSecuencia
            : siguienteSecuencia < 100
              ? "0" + siguienteSecuencia
              : siguienteSecuencia.toString()

        const codigoFinal = mes + digitoTipo + secuenciaFormateada
        resolve(codigoFinal)
      },
      error: (error) => {
        console.error("Error al obtener secuencia:", error)
        const codigoFinal = mes + digitoTipo + "001"
        resolve(codigoFinal)
      },
    })
  })
}

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

// FUNCIÓN CORREGIDA - NO EJECUTAR EN MODO EDICIÓN
function actualizarCodigo() {
  const action = $('input[name="action"]').val()

  if (action === 'edit') {
    console.log("MODO EDICIÓN: NO se actualiza el código")
    return Promise.resolve()
  }

  console.log("MODO CREACIÓN: Actualizando código...")
  const tipoCuenta = $('select[name="tip_cuenta"]').val()

  return generarCodigoSecuencial(tipoCuenta)
    .then((codigo) => {
      $('input[name="codigo"]').val(codigo)
      return codigo
    })
    .catch((error) => {
      console.error("Error al generar código:", error)
      const fechaActual = new Date()
      let mes = fechaActual.getMonth() + 1
      mes = mes < 10 ? "0" + mes : mes.toString()
      const codigoPredeterminado = mes + "1001"
      $('input[name="codigo"]').val(codigoPredeterminado)
      return codigoPredeterminado
    })
}

function depurarSelect() {
  console.log("=== DEPURACIÓN DEL SELECT ===")
  const select = $('select[name="tip_cuenta"]')
  console.log("Valor seleccionado:", select.val())
  console.log("Texto seleccionado:", select.find("option:selected").text())

  console.log("Opciones disponibles:")
  select.find("option").each(function (index) {
    console.log(`Opción ${index}: valor="${$(this).val()}", texto="${$(this).text()}"`)
  })
}

function preseleccionarEmpresaBIO() {
  console.log("Intentando preseleccionar empresa BIO...")
  var empresaSelect = $('select[name="empresa"]')

  var encontrada = false
  empresaSelect.find("option").each(function () {
    if ($(this).text().includes("BIOCASCAJAL") || $(this).text() === "BIO") {
      empresaSelect.val($(this).val()).trigger("change")
      encontrada = true
      console.log("Empresa BIO seleccionada por texto:", $(this).text())
      return false
    }
  })

  if (!encontrada) {
    empresaSelect.find("option").each(function () {
      var valor = $(this).val()
      if (valor && (valor === "BIO" || valor.includes("BIO"))) {
        empresaSelect.val(valor).trigger("change")
        console.log("Empresa BIO seleccionada por valor:", valor)
        return false
      }
    })
  }
}

$(document).ready(() => {
  // Agregar estilos
  $("<style>").text(compactStyles).appendTo("head")

  preseleccionarEmpresaBIO()

  setTimeout(depurarSelect, 1000)

  // CORRECCIÓN PRINCIPAL: Solo generar código en modo creación
  setTimeout(function() {
    const action = $('input[name="action"]').val()
    console.log("Acción detectada:", action)

    if (action === 'create') {
      console.log("MODO CREACIÓN: Generando código inicial")
      actualizarCodigo()
    } else if (action === 'edit') {
      console.log("MODO EDICIÓN: Manteniendo código original")
      const codigoOriginal = $('input[name="codigo"]').val()
      console.log("Código original:", codigoOriginal)

      // IMPORTANTE: Hacer el campo readonly y evitar cambios
      $('input[name="codigo"]').prop('readonly', true)
        .css('background-color', '#f8f9fa')
        .css('border', '1px solid #ced4da')
        .attr('title', 'Código original - No se puede modificar en edición')

      // BLOQUEAR CUALQUIER INTENTO DE CAMBIO
      $('input[name="codigo"]').on('focus', function() {
        $(this).blur()
        console.log("Campo código bloqueado en modo edición")
      })
    }
  }, 1500)

  $(".select2").select2({
    theme: "bootstrap4",
    language: "es",
  })

  // Cargar plan de cuentas automáticamente
  loadPlanCuentasBIO()

  $("#btnBuscarPlanBIO").on("click", () => {
    loadPlanCuentasBIO(true)
  })

  // Evento mejorado para agregar cuenta
  $(document).on("click", '#tblSearchPlan tbody a[rel="add"]', function () {
    var row = $(this).closest("tr")
    var dataId = row.data("id")

    var item = null
    for (var i = 0; i < allPlanData.length; i++) {
      if (allPlanData[i].id == dataId) {
        item = allPlanData[i]
        break
      }
    }

    if (!item) {
      console.error("No se pudo encontrar el item con ID:", dataId)
      alerta_error("Error al obtener los datos de la cuenta.")
      return
    }

    var newItem = {
      id: item.id,
      codigo: item.codigo,
      nombre: item.nombre,
      tipo_cuenta: item.tipo_cuenta,
      detalle: $('input[name="descripcion"]').val() || "",
      debe: 0.0,
      haber: 0.0,
    }

    vents.add(newItem)

    allPlanData = allPlanData.filter((data) => data.id != dataId)

    row.remove()

    // Actualizar contador si hay búsqueda activa
    if (isSearchActive) {
      const foundCount = allPlanData.length
      updateSearchStatus(`Búsqueda: "${originalSearchTerm}" - ${foundCount} resultado(s) encontrado(s)`)
    }

    if (currentPage < totalPages) {
      addLoadMoreIndicator()
    }

    showTemporaryMessage(`Cuenta ${item.codigo} agregada correctamente`, "success")
  })

  // CORRECCIÓN: BLOQUEAR COMPLETAMENTE cambios de código en edición
  $('select[name="tip_cuenta"]').off('change').on('change', function() {
    const action = $('input[name="action"]').val()
    console.log("Cambio en tipo de cuenta, acción:", action)

    if (action === 'create') {
      console.log("MODO CREACIÓN: Actualizando código por cambio de tipo")
      actualizarCodigo()
    } else {
      console.log("MODO EDICIÓN: CAMBIO BLOQUEADO - No se actualiza el código")
      // ABSOLUTAMENTE NADA en modo edición
    }
  })

  $("#tbl_transaccionPlan tbody")
    .on("click", 'a[rel="remove"]', function () {
      var tr = tbl_transaccionPlan.cell($(this).closest("td, li")).index()
      vents.items.products.splice(tr.row, 1)
      vents.list()
    })
    .on("change", 'input[name="debe"]', function () {
      var debe = Number.parseFloat($(this).val())
      var tr = tbl_transaccionPlan.cell($(this).closest("td, li")).index()
      vents.items.products[tr.row].debe = debe
      vents.calculate_invoice()
    })
    .on("change", 'input[name="haber"]', function () {
      var haber = Number.parseFloat($(this).val())
      var tr = tbl_transaccionPlan.cell($(this).closest("td, li")).index()
      vents.items.products[tr.row].haber = haber
      vents.calculate_invoice()
    })
    .on("change", 'input[name="detalle"]', function () {
      var detalle = $(this).val()
      var tr = tbl_transaccionPlan.cell($(this).closest("td, li")).index()
      vents.items.products[tr.row].detalle = detalle
      vents.calculate_invoice()
    })

  $("#btnSave").on("click", (event) => {
    event.preventDefault()
    var items = vents.items.products
    if (items.length === 0) {
      alerta_error("Debe ingresar al menos un item")
      return false
    }

    $.ajax({
      url: window.location.pathname,
      data: {
        action: $('input[name="action"]').val(),
        codigo: $('input[name="codigo"]').val(),
        tip_cuenta: $('select[name="tip_cuenta"]').val(),
        fecha: $('input[name="fecha"]').val(),
        descripcion: $('input[name="descripcion"]').val(),
        empresa: $('select[name="empresa"]').val(),
        comprobante: $('input[name="comprobante"]').val(),
        direccion: $('textarea[name="direccion"]').val(),
        items: JSON.stringify(items),
      },
      type: "POST",
      dataType: "json",
      success: (request) => {
        if (!request.hasOwnProperty("error")) {
          location.href = "/planCuentas/transaccionbio/listar/"
          return false
        }
        alert(request.error)
      },
      error: (jqXHR, textStatus, errorThrown) => {
        alert(errorThrown + " " + textStatus)
      },
    })
  })

  $('select[name="search"]')
    .select2({
      theme: "bootstrap4",
      language: "es",
      allowClear: true,
      ajax: {
        delay: 250,
        type: "POST",
        url: window.location.pathname,
        data: (params) => {
          var queryParameters = {
            term: params.term,
            action: "search_autocomplete",
            ids: JSON.stringify(vents.get_ids()),
          }
          return queryParameters
        },
        processResults: (data) => ({
          results: data,
        }),
      },
      placeholder: "Ingrese una Cuenta a Buscar",
      minimumInputLength: 1,
      templateResult: formatRepo,
    })
    .on("select2:select", function (e) {
      var data = e.params.data

      if (data.tipo_cuenta === "GENERAL") {
        return false
      }

      if (!data.id || isNaN(Number.parseInt(data.id))) {
        console.error("ID de cuenta inválido:", data.id)
        alerta_error("Error: ID de cuenta inválido. Por favor, seleccione otra cuenta.")
        return false
      }

      var item = {
        id: data.id,
        codigo: data.codigo,
        nombre: data.text || data.nombre,
        tipo_cuenta: data.tipo_cuenta,
        detalle: $('input[name="descripcion"]').val() || "",
        debe: 0.0,
        haber: 0.0,
      }

      vents.add(item)
      $(this).val("").trigger("change.select2")
    })

  vents.list()

  // Precarga de datos
  setTimeout(() => {
    if (!planCuentasCache) {
      $.ajax({
        url: window.location.pathname,
        type: "POST",
        data: {
          action: "search_plan",
          ids: JSON.stringify([]),
          empresa: "BIO",
          page: 1,
          page_size: 200,
        },
        dataType: "json",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
        },
        success: (response) => {
          const data = response.data || response
          if (data) {
            planCuentasCache = data
            lastLoadTime = new Date().getTime()
            console.log("Datos precargados exitosamente:", data.length, "registros")
          }
        },
        error: (error) => {
          console.log("Error en precarga (no crítico):", error)
        },
      })
    }
  }, 2000)
})

function calculos_prod(json, debe, haber) {
  deb = debe
  hab = haber
  if (deb === hab) {
    $('input[name="debe_resp"]').val(deb.toFixed(2))
    $('input[name="haber_resp"]').val(hab.toFixed(2))
    $('input[name="proceso"]').val("OPERACION BALANCEADA !CORRECTA!")
    var cal_diff = debe - haber
    $('input[name="resultado"]').val(cal_diff.toFixed(2))
    document.getElementById("btnSave").disabled = false
  } else if (hab > deb) {
    $('input[name="debe_resp"]').val(deb.toFixed(2))
    $('input[name="haber_resp"]').val(hab.toFixed(2))
    $('input[name="proceso"]').val("EL HABER ES MAYOR AL DEBE !!!ERROR!!!")
    var cal_diff_haber = haber - debe
    $('input[name="resultado"]').val(cal_diff_haber.toFixed(2))
    document.getElementById("btnSave").disabled = true
  } else if (hab < deb) {
    $('input[name="debe_resp"]').val(deb.toFixed(2))
    $('input[name="haber_resp"]').val(hab.toFixed(2))
    $('input[name="proceso"]').val("EL DEBE ES MAYOR AL HABER !!!ERROR!!!")
    var cal_diff_debe = debe - haber
    $('input[name="resultado"]').val(cal_diff_debe.toFixed(2))
    document.getElementById("btnSave").disabled = true
  } else {
    $('input[name="proceso"]').val("PROCESO A REALIZAR")
  }
}

function alerta_error(message) {
  if (typeof window.Swal !== "undefined") {
    window.Swal.fire({
      title: "Error",
      text: message,
      icon: "error",
    })
  } else {
    alert(message)
  }
}
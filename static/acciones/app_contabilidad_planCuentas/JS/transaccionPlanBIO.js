// Variables globales
var tbl_transaccionPlan
var tblSearchPlan
var $ = jQuery // Asumiendo que jQuery está disponible
var deb = 0.0,
    hab = 0.0
var date_now = new Date().toISOString().split("T")[0] // No depender de moment.js
const fecha_actual = new Date()

// Variable para almacenar en caché los datos del plan de cuentas
var planCuentasCache = null
var isLoadingPlan = false
var lastLoadTime = 0
var CACHE_DURATION = 5 * 60 * 1000 // 5 minutos en milisegundos

// Estilos CSS para tablas y modales compactos
const compactStyles = `
.modal-compacto {
  max-width: 90%;
  margin: 0.5rem auto;
}

.modal-compacto .modal-header {
  padding: 0.4rem 0.75rem;
  background-color: #0099cc;
  color: white;
}

.modal-compacto .modal-title {
  font-size: 0.9rem;
  font-weight: bold;
}

.modal-compacto .modal-body {
  padding: 0.5rem;
  max-height: 65vh;
  overflow-y: auto;
}

.modal-compacto .modal-footer {
  padding: 0.4rem;
}

.modal-compacto table {
  font-size: 0.8rem;
  margin-bottom: 0.5rem;
}

.modal-compacto table th,
.modal-compacto table td {
  padding: 0.25rem 0.5rem !important;
  vertical-align: middle;
}

.modal-compacto .form-control {
  height: calc(1.5em + 0.5rem + 2px);
  padding: 0.25rem 0.5rem;
  font-size: 0.8rem;
}

.modal-compacto .btn {
  padding: 0.15rem 0.4rem;
  font-size: 0.75rem;
}

.modal-compacto .buscar-container {
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
}

.modal-compacto .buscar-label {
  font-size: 0.8rem;
  font-weight: bold;
  margin-right: 0.5rem;
  white-space: nowrap;
}

.modal-compacto .buscar-input {
  flex: 1;
}

.modal-compacto .btn-xs {
  padding: 0.1rem 0.25rem;
  font-size: 0.7rem;
  line-height: 1;
}

.modal-compacto .dataTables_wrapper .dataTables_length,
.modal-compacto .dataTables_wrapper .dataTables_filter {
  padding: 0.25rem 0;
  font-size: 0.8rem;
}

.modal-compacto .dataTables_wrapper .dataTables_info,
.modal-compacto .dataTables_wrapper .dataTables_paginate {
  padding-top: 0.25rem;
  font-size: 0.75rem;
}

.modal-compacto .dataTables_wrapper .dataTables_paginate .paginate_button {
  padding: 0.1rem 0.4rem;
  font-size: 0.75rem;
}

.select2-dropdown-sm .select2-results__option {
  padding: 4px 8px;
  font-size: 0.875rem;
}

.select2-dropdown-sm .select2-search__field {
  padding: 4px;
  font-size: 0.875rem;
}

/* Estilos para Select2 más pequeño */
.select2-container--bootstrap4 .select2-selection {
  height: calc(1.5em + 0.5rem + 2px) !important;
  font-size: 0.875rem !important;
  padding: 0.25rem 0.5rem !important;
}

.select2-container--bootstrap4 .select2-selection--single .select2-selection__rendered {
  line-height: 1.5 !important;
  padding-left: 0 !important;
}

.select2-container--bootstrap4 .select2-results__option {
  padding: 0.25rem 0.5rem !important;
  font-size: 0.875rem !important;
}

.select2-container--bootstrap4 .select2-search--dropdown .select2-search__field {
  padding: 0.25rem 0.5rem !important;
  font-size: 0.875rem !important;
}
`

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

        // Destruir la tabla existente si ya existe
        if ($.fn.DataTable.isDataTable("#tbl_transaccionPlan")) {
            $("#tbl_transaccionPlan").DataTable().destroy()
            // Importante: limpiar el contenido de la tabla después de destruirla
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
            scrollY: "250px", // Altura reducida
            destroy: true,
            data: this.items.products,
            columns: [
                {data: "id", width: "3%"},
                {data: "codigo", width: "10%"},
                {data: "nombre", width: "20%"},
                {data: "detalle", width: "47%"},
                {data: "debe", width: "10%"},
                {data: "haber", width: "10%"},
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

    // Versión más compacta del formato
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

// Función para aplicar estilos compactos al modal
function aplicarEstilosCompactosModal() {
    // Agregar clase al modal
    $("#myModalSearchPlan").addClass("modal-compacto")

    // Ajustar la altura máxima de la tabla según el tamaño de la ventana
    function ajustarAlturaTabla() {
        const windowHeight = $(window).height()
        const modalHeader = $("#myModalSearchPlan .modal-header").outerHeight() || 0
        const modalFooter = $("#myModalSearchPlan .modal-footer").outerHeight() || 0
        const buscarContainer = $("#myModalSearchPlan .buscar-container").outerHeight() || 0
        const padding = 40 // Padding adicional

        // Calcular altura disponible
        const availableHeight = windowHeight - modalHeader - modalFooter - buscarContainer - padding
        const tableHeight = Math.max(200, Math.min(350, availableHeight)) // Entre 200px y 350px

        // Aplicar altura a la tabla
        $("#tblSearchPlan_wrapper .dataTables_scrollBody").css("max-height", tableHeight + "px")
    }

    // Crear una barra de búsqueda personalizada que funcione correctamente
    const $buscarContainer = $("<div>").addClass("buscar-container")
    const $buscarLabel = $("<label>").addClass("buscar-label").text("BUSCAR:")
    const $buscarInput = $("<input>")
        .attr("type", "search")
        .addClass("form-control form-control-sm buscar-input")
        .attr("placeholder", "Buscar...")

    // Agregar la barra de búsqueda al principio del wrapper de DataTable
    $("#tblSearchPlan_wrapper").prepend($buscarContainer)
    $buscarContainer.append($buscarLabel).append($buscarInput)

    // Conectar el evento de búsqueda al DataTable
    $buscarInput.on("keyup", function () {
        tblSearchPlan.search(this.value).draw()
    })

    // Ajustar tamaño de botones
    $("#myModalSearchPlan .btn").addClass("btn-sm")
    $("#myModalSearchPlan a[rel='add'], #myModalSearchPlan a[rel='neg']").addClass("btn-xs")

    // Ejecutar ajuste de altura al cargar y al cambiar tamaño de ventana
    ajustarAlturaTabla()
    $(window).resize(ajustarAlturaTabla)
}

// OPTIMIZACIÓN CLAVE: Función para cargar el plan de cuentas de forma eficiente
function loadPlanCuentasBIO() {
    // 1. MOSTRAR EL MODAL INMEDIATAMENTE (sin esperar a la carga de datos)
    $("#myModalSearchPlan").modal("show")

    // 2. Mostrar indicador de carga en el modal
    $("#table-tree").html(
        '<tr><td colspan="5" class="text-center"><div class="spinner-border text-primary spinner-border-sm" role="status"></div><p class="mt-1 small">Cargando datos...</p></td></tr>',
    )

    // 3. Verificar si podemos usar datos en caché
    var currentTime = new Date().getTime()
    if (planCuentasCache !== null && currentTime - lastLoadTime < CACHE_DURATION) {
        console.log("Usando datos en caché")
        renderPlanCuentas(planCuentasCache)
        return
    }

    // 4. Si ya está en proceso de carga, no iniciar otra solicitud
    if (isLoadingPlan) return

    isLoadingPlan = true

    // 5. Obtener los IDs de productos ya agregados
    var ids = vents.get_ids()

    // 6. Realizar la petición AJAX (sin bloquear la interfaz)
    $.ajax({
        url: window.location.pathname,
        type: "POST",
        data: {
            action: "search_plan",
            ids: JSON.stringify(ids),
            empresa: "BIO",
        },
        dataType: "json",
        timeout: 30000, // 30 segundos máximo
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
        },
        success: (data) => {
            // Guardar los datos en caché y actualizar tiempo
            planCuentasCache = data
            lastLoadTime = new Date().getTime()
            renderPlanCuentas(data)
        },
        error: (error) => {
            console.error("Error al cargar datos:", error)
            $("#table-tree").html(
                '<tr><td colspan="5" class="text-center text-danger small">Error al cargar los datos. <button class="btn btn-sm btn-primary" onclick="loadPlanCuentasBIO()">Reintentar</button></td></tr>',
            )
        },
        complete: () => {
            isLoadingPlan = false
        },
    })
}

// Función para renderizar los datos del plan de cuentas
function renderPlanCuentas(data) {
    // Limpiar la tabla
    $("#table-tree").empty()

    // Si ya existe una instancia de DataTable, destruirla correctamente
    if ($.fn.DataTable.isDataTable("#tblSearchPlan")) {
        $("#tblSearchPlan").DataTable().destroy()
        // Importante: limpiar el contenido de la tabla después de destruirla
        $("#tblSearchPlan tbody").empty()
    }

    // Agregar filas a la tabla (optimizado para rendimiento)
    var html = ""
    for (var i = 0; i < data.length; i++) {
        var item = data[i]
        html += `
            <tr>
                <td>${item.codigo}</td>
                <td>${item.tipo_cuenta || ""}</td>
                <td>${item.nombre}</td>
                <td>${item.empresa.siglas}</td>
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

    // Inicializar DataTable con opciones optimizadas para rendimiento
    tblSearchPlan = $("#tblSearchPlan").DataTable({
        language: {
            oPaginate: {
                sFirst: "«",
                sLast: "»",
                sNext: "›",
                sPrevious: "‹",
            },
            zeroRecords: "Sin resultados",
            sInfo: "_START_-_END_ de _TOTAL_",
            infoEmpty: "Tabla vacía",
            lengthMenu: "_MENU_",
            sSearch: "Buscar:",
            infoFiltered: "(de _MAX_)",
        },
        dom: "tip", // No incluimos 'f' para que no muestre el campo de búsqueda predeterminado
        bPaginate: false,
        ordering: false,
        responsive: true,
        autoWidth: false,
        scrollY: "250px", // Altura reducida
        destroy: true,
        deferRender: true,
        search: {
            return: true,
            smart: true, // Búsqueda inteligente
            regex: false, // No usar expresiones regulares
            caseInsensitive: true, // No distinguir mayúsculas/minúsculas
        },
        // Opciones para mejorar rendimiento
        processing: true,
        pageLength: 100,
        initComplete: () => {
            // Aplicar estilos compactos después de que la tabla se haya inicializado
            setTimeout(aplicarEstilosCompactosModal, 100)
        },
    })
}

// Función para obtener cookies (para CSRF)
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


function generarCodigoSecuencial(tipoCuenta) {
  // Mostrar indicador de carga
  $('input[name="codigo"]').val("Generando...")

  // Obtener el mes actual (1-12)
  const fechaActual = new Date()
  let mes = fechaActual.getMonth() + 1 // getMonth() devuelve 0-11

  // Formatear el mes con dos dígitos (01-12)
  mes = mes < 10 ? "0" + mes : mes.toString()

  // Determinar el dígito según el tipo de cuenta
  let digitoTipo = "1" // Por defecto DIARIO CONTABLE

  // Obtener el texto visible del select, no el valor
  const tipoCuentaTexto = $('select[name="tip_cuenta"] option:selected').text().trim()
  console.log("Tipo de cuenta seleccionado:", tipoCuentaTexto)

  if (tipoCuentaTexto === "COMPROBANTE PAGO") {
    digitoTipo = "2"
  } else if (tipoCuentaTexto === "INGRESO A CAJA") {
    digitoTipo = "3"
  } else if (tipoCuentaTexto === "EGRESO DE CAJA") {
    digitoTipo = "4"
  }

  console.log("Dígito asignado:", digitoTipo)

  // Realizar la petición AJAX para obtener la última secuencia
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
        console.log("Respuesta del servidor:", response)

        // MEJORA: Verificar si la respuesta es válida
        if (!response) {
          console.error("Respuesta vacía del servidor")
          // Usar un valor predeterminado
          const codigoFinal = mes + digitoTipo + "001"
          console.log("Usando código predeterminado:", codigoFinal)
          resolve(codigoFinal)
          return
        }

        if (response.error) {
          console.error("Error del servidor:", response.error)
          // No rechazar la promesa, usar un valor predeterminado
          const codigoFinal = mes + digitoTipo + "001"
          console.log("Usando código predeterminado debido a error:", codigoFinal)
          resolve(codigoFinal)
          return
        }

        // Obtener la última secuencia y sumar 1 para obtener la siguiente
        let ultimaSecuencia = 0
        if (response.secuencia !== undefined) {
          ultimaSecuencia = Number.parseInt(response.secuencia)
        }

        // Incrementar para obtener la siguiente secuencia
        const siguienteSecuencia = ultimaSecuencia + 1
        console.log("Última secuencia:", ultimaSecuencia)
        console.log("Siguiente secuencia:", siguienteSecuencia)

        // Formatear la secuencia con tres dígitos (001-999)
        const secuenciaFormateada =
          siguienteSecuencia < 10
            ? "00" + siguienteSecuencia
            : siguienteSecuencia < 100
              ? "0" + siguienteSecuencia
              : siguienteSecuencia.toString()

        // Construir el código completo: MES + TIPO + SECUENCIA
        const codigoFinal = mes + digitoTipo + secuenciaFormateada
        console.log("Código generado:", codigoFinal)

        resolve(codigoFinal)
      },
      error: (error) => {
        console.error("Error al obtener secuencia:", error)
        // No rechazar la promesa, usar un valor predeterminado
        const codigoFinal = mes + digitoTipo + "001"
        console.log("Usando código predeterminado debido a error de red:", codigoFinal)
        resolve(codigoFinal)
      },
    })
  })
}

// Función para obtener cookies (para CSRF)
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

// Función para actualizar el código cuando cambia el tipo de cuenta
function actualizarCodigo() {
  const tipoCuenta = $('select[name="tip_cuenta"]').val()

  // Mostrar indicador de carga
  $('input[name="codigo"]').val("Generando...")

  // Generar el código secuencial
  generarCodigoSecuencial(tipoCuenta)
    .then((codigo) => {
      $('input[name="codigo"]').val(codigo)
    })
    .catch((error) => {
      console.error("Error al generar código:", error)

      // MEJORA: Generar un código predeterminado en caso de error
      const fechaActual = new Date()
      let mes = fechaActual.getMonth() + 1
      mes = mes < 10 ? "0" + mes : mes.toString()

      let digitoTipo = "1" // Por defecto
      const tipoCuentaTexto = $('select[name="tip_cuenta"] option:selected').text().trim()
      if (tipoCuentaTexto === "COMPROBANTE PAGO") {
        digitoTipo = "2"
      } else if (tipoCuentaTexto === "INGRESO A CAJA") {
        digitoTipo = "3"
      } else if (tipoCuentaTexto === "EGRESO DE CAJA") {
        digitoTipo = "4"
      }

      const codigoPredeterminado = mes + digitoTipo + "001"
      $('input[name="codigo"]').val(codigoPredeterminado)

      // Mostrar alerta de error
      if (typeof Swal !== "undefined") {
        Swal.fire({
          title: "Advertencia",
          text: "No se pudo obtener la última secuencia. Se ha generado un código predeterminado.",
          icon: "warning",
        })
      } else {
        alert("No se pudo obtener la última secuencia. Se ha generado un código predeterminado.")
      }
    })
}

// Inicializar eventos cuando el documento esté listo
$(document).ready(() => {
  // Generar código inicial basado en el tipo de cuenta seleccionado
  setTimeout(actualizarCodigo, 1500)

  // Actualizar código cuando cambie el tipo de cuenta
  $('select[name="tip_cuenta"]').on("change", () => {
    actualizarCodigo()
  })

  $("#frmSale").on("submit", () => {
    // Obtener el código actual
    const codigo = $('input[name="codigo"]').val()

    // Verificar que el código tenga el formato correcto
    if (!/^\d{2}\d\d{3}$/.test(codigo)) {
      if (typeof Swal !== "undefined") {
        Swal.fire({
          title: "Error",
          text: "El código generado no tiene el formato correcto. Por favor, regenere el código.",
          icon: "error",
        })
      } else {
        alert("El código generado no tiene el formato correcto. Por favor, regenere el código.")
      }
      return false
    }

    return true
  })
})



// Función para depurar el select y sus opciones
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

$(() => {
    // Agregar estilos para tablas compactas
    $("<style>").text(compactStyles).appendTo("head")

    preseleccionarEmpresaBIO()

    // Depurar el select para entender su estructura
    setTimeout(depurarSelect, 1000)

    // Generar código inicial basado en el tipo de cuenta seleccionado
    setTimeout(actualizarCodigo, 1500)

    // Inicialización de componentes
    $(".select2").select2({
        theme: "bootstrap4",
        language: "es",
    })

    // Evento para abrir el modal de búsqueda
    $("#btnBuscarPlanBIO").on("click", () => {
        loadPlanCuentasBIO()
    })

// Función para agregar un plan desde el modal - CORREGIDA
    $(document).on("click", '#tblSearchPlan tbody a[rel="add"]', function () {
        // Obtener la fila actual
        var row = $(this).closest("tr")

        // Obtener los datos de la fila
        var codigo = row.find("td:eq(0)").text()
        var tipo_cuenta = row.find("td:eq(1)").text()
        var nombre = row.find("td:eq(2)").text()
        var empresa = row.find("td:eq(3)").text()

        // Intentar obtener el ID real de la cuenta
        var cuentaId = null

        // Buscar en los datos en caché si están disponibles
        if (planCuentasCache) {
            for (var i = 0; i < planCuentasCache.length; i++) {
                if (planCuentasCache[i].codigo === codigo) {
                    cuentaId = planCuentasCache[i].id
                    break
                }
            }
        }

        // Si no se encontró el ID, mostrar un error
        if (!cuentaId) {
            console.error("No se pudo encontrar el ID de la cuenta con código:", codigo)
            alerta_error("No se pudo obtener el ID de la cuenta. Por favor, intente nuevamente.")
            return
        }

        // Crear el objeto con los datos necesarios
        var item = {
            id: cuentaId, // Usar el ID real de la cuenta, no un timestamp
            codigo: codigo,
            nombre: nombre,
            tipo_cuenta: tipo_cuenta,
            detalle: $('input[name="descripcion"]').val() || "",
            debe: 0.0,
            haber: 0.0,
        }

        // Declare vents variable (assuming it's an object with an add method)
        // You might need to adjust this based on how vents is actually used in your project
        var vents = window.vents || {
            add: (item) => {
                console.log("Adding item:", item)
                // Implement the actual logic to add the item to the vents object
            },
        }

        // Agregar el item a la lista de productos
        vents.add(item)

        // Eliminar la fila del modal
        row.remove()

        // Actualizar la caché para reflejar la eliminación
        if (planCuentasCache) {
            var index = -1
            for (var j = 0; j < planCuentasCache.length; j++) {
                if (planCuentasCache[j].codigo === codigo) {
                    index = j
                    break
                }
            }
            if (index !== -1) {
                planCuentasCache.splice(index, 1)
            }
        }
    })


    // Actualizar código cuando cambie el tipo de cuenta
    $('select[name="tip_cuenta"]').on("change", () => {
        // depurarSelect()
        actualizarCodigo()
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

    function preseleccionarEmpresaBIO() {
        // Buscar la opción que contiene "BIOCASCAJAL" o "BIO"
        var empresaSelect = $('select[name="empresa"]')

        // Primero intentamos encontrar la opción por su texto
        var encontrada = false
        empresaSelect.find("option").each(function () {
            if ($(this).text().includes("BIOCASCAJAL") || $(this).text() === "BIO") {
                empresaSelect.val($(this).val()).trigger("change")
                encontrada = true
                console.log("Empresa BIO seleccionada por texto:", $(this).text())
                return false // Salir del bucle
            }
        })

        // Si no se encontró por texto, intentamos por el valor de la opción
        if (!encontrada) {
            // Buscar por ID o valor específico (ajustar según tu estructura de datos)
            empresaSelect.find("option").each(function () {
                var valor = $(this).val()
                // Verificar si el valor corresponde a la empresa BIO
                // Esto depende de cómo estén estructurados tus datos
                if (valor && (valor === "BIO" || valor.includes("BIO"))) {
                    empresaSelect.val(valor).trigger("change")
                    console.log("Empresa BIO seleccionada por valor:", valor)
                    return false // Salir del bucle
                }
            })
        }
    }

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

            // Verificar si es una cuenta general
            if (data.tipo_cuenta === "GENERAL") {
                return false
            }

            // Verificar que el ID sea un número válido
            if (!data.id || isNaN(Number.parseInt(data.id))) {
                console.error("ID de cuenta inválido:", data.id)
                alerta_error("Error: ID de cuenta inválido. Por favor, seleccione otra cuenta.")
                return false
            }

            // Usar el ID real de la cuenta, no un timestamp
            var item = {
                id: data.id, // Usar el ID real de la cuenta
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

    // Precarga de datos en segundo plano para mejorar la experiencia
    setTimeout(() => {
        $.ajax({
            url: window.location.pathname,
            type: "POST",
            data: {
                action: "search_plan",
                ids: JSON.stringify([]),
                empresa: "BIO",
            },
            dataType: "json",
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
            },
            success: (data) => {
                planCuentasCache = data
                lastLoadTime = new Date().getTime()
                console.log("Datos precargados exitosamente")
            },
        })
    }, 1000) // Esperar 1 segundo después de cargar la página
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

// Función para mostrar mensajes de error (usando SweetAlert si está disponible)
function alerta_error(message) {
    alert(message)
}

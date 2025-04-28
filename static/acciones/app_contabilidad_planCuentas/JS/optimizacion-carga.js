// Este archivo contiene optimizaciones para la carga inicial del modal
// Incluir este script al final de tu página HTML

// Declaración de variables globales
var planCuentasCache = null

// Función para precargar datos en segundo plano
function precargarDatos() {
  // Verificar si ya tenemos datos en caché
  if (planCuentasCache !== null) {
    console.log("Usando datos en caché existentes")
    return
  }

  console.log("Iniciando precarga de datos...")

  // Realizar la petición AJAX en segundo plano
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
      console.log("Precarga completada: " + data.length + " registros")
      planCuentasCache = data
    },
    error: (error) => {
      console.error("Error en precarga:", error)
    },
  })
}

// Función para cargar el modal con datos precargados
function loadPlanCuentasBIOOptimizado() {
  // Mostrar el modal inmediatamente
  $("#myModalSearchPlan").modal("show")

  // Si ya tenemos datos en caché, usarlos directamente
  if (planCuentasCache !== null) {
    console.log("Usando datos precargados")
    renderizarDatos(planCuentasCache)
    return
  }

  // Mostrar indicador de carga
  $("#table-tree").html(
    '<tr><td colspan="5" class="text-center py-3"><div class="spinner-border text-primary" role="status"></div><p class="mt-2">Cargando plan de cuentas...</p></td></tr>',
  )

  // Si no hay datos en caché, cargar normalmente
  loadPlanCuentasBIO()
}

// Función para renderizar datos en la tabla
function renderizarDatos(data) {
  // Limpiar la tabla
  $("#table-tree").empty()

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

  // Actualizar contador de registros
  var totalRows = data.length
  $("#recordsInfo").text("Registros del 1 al " + totalRows + " de un total de " + totalRows + " registros")

  // Inicializar búsqueda rápida
  $("#searchInput, #searchBox").val("").trigger("keyup")
}

// Reemplazar el evento click original con la versión optimizada
$(document).ready(() => {
  // Reemplazar el evento click para usar la versión optimizada
  $("#btnBuscarPlanBIO")
    .off("click")
    .on("click", () => {
      loadPlanCuentasBIOOptimizado()
    })

  // Iniciar precarga de datos después de 2 segundos
  setTimeout(precargarDatos, 2000)
})

// Función para obtener el valor de una cookie
function getCookie(name) {
  let cookieValue = null
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";")
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim()
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}

// Función loadPlanCuentasBIO (simulada, ya que no se proporciona su implementación)
function loadPlanCuentasBIO() {
  console.log("Función loadPlanCuentasBIO llamada (implementación original)")
  // Aquí iría la implementación original de loadPlanCuentasBIO
  // Por ejemplo, una llamada AJAX similar a precargarDatos pero sin usar caché
}

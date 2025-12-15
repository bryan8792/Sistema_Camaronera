var $ = window.jQuery
var Swal = window.Swal

var anticipo = {
  items: {
    formas_pago: [],
  },

  init: () => {
    console.log("[v0] Inicializando módulo de anticipos")

    $(".btnSave").on("click", (event) => {
      event.preventDefault()
      anticipo.guardar()
    })
  },

  guardar: () => {
    console.log("[v0] Guardando anticipo...")

    // Validar que haya al menos una forma de pago
    if (anticipo.items.formas_pago.length === 0) {
      Swal.fire({
        icon: "error",
        title: "Error",
        text: "Debe agregar al menos una forma de pago",
      })
      return false
    }

    // Validar que el monto coincida
    const monto = Number.parseFloat($("#monto").val()) || 0
    const total_formas = anticipo.calcularTotal()

    if (Math.abs(monto - total_formas) > 0.01) {
      Swal.fire({
        icon: "error",
        title: "Error",
        text: `El monto ($${monto.toFixed(2)}) no coincide con el total de formas de pago ($${total_formas.toFixed(2)})`,
      })
      return false
    }

    const centro_costo = $("#centro_costo_id").val()
    const identificacion = $("#identificacion").val()
    const razon_social = $("#razon_social").val()
    const fecha = $("#fecha").val()
    const concepto = $("#concepto").val()

    if (!centro_costo || !identificacion || !razon_social || !fecha || !concepto) {
      Swal.fire({
        icon: "error",
        title: "Error",
        text: "Complete todos los campos obligatorios (marcados con *)",
      })
      return false
    }

    console.log("[v0] Enviando datos:", {
      formas_pago: anticipo.items.formas_pago,
      monto: monto,
      total_formas: total_formas,
    })

    const csrftoken = $('input[name="csrfmiddlewaretoken"]').val()
    console.log("[v0] CSRF Token:", csrftoken)

    $.ajax({
      url: window.location.pathname,
      data: {
        action: "create",
        caja: $("#caja").val(),
        tipo_cliente: $("#tipo_cliente").val(),
        centro_costo_id: $("#centro_costo_id").val(),
        tipo_identificacion: $("#tipo_identificacion").val(),
        identificacion: $("#identificacion").val(),
        razon_social: $("#razon_social").val(),
        nombre_comercial: $("#nombre_comercial").val(),
        telefono: $("#telefono").val(),
        celular: $("#celular").val(),
        email: $("#email").val(),
        ciudad: $("#ciudad").val(),
        direccion: $("#direccion").val(),
        fecha: $("#fecha").val(),
        monto: $("#monto").val(),
        concepto: $("#concepto").val(),
        categoria_contable_id: $("#categoria_contable_id").val(),
        formas_pago: JSON.stringify(anticipo.items.formas_pago),
        csrfmiddlewaretoken: csrftoken,
      },
      type: "POST",
      dataType: "json",
      success: (response) => {
        console.log("[v0] Respuesta del servidor:", response)

        if (response.success) {
          Swal.fire({
            position: "top-center",
            icon: "success",
            title: response.message || "Anticipo guardado correctamente",
            showConfirmButton: false,
            timer: 1500,
          })
          setTimeout(() => {
            window.location.href = "/anticipo/listar_anticipo"
          }, 1600)
        } else if (response.error) {
          Swal.fire({
            icon: "error",
            title: "Error",
            text: response.error,
          })
        }
      },
      error: (jqXHR, textStatus, errorThrown) => {
        console.error("[v0] Error:", textStatus, errorThrown)
        console.error("[v0] Response:", jqXHR.responseText)
        Swal.fire({
          icon: "error",
          title: "Error",
          text: "Error al guardar el anticipo: " + errorThrown,
        })
      },
    })
  },

  cargarPlanCuentas: () => {
    const empresa_id = $("#centro_costo_id").val()

    console.log("[v0] Cargando plan de cuentas para empresa:", empresa_id)

    if (!empresa_id) {
      $("#categoria_contable_id").html('<option value="">Seleccione cuenta</option>')
      return
    }

    const csrftoken = $('input[name="csrfmiddlewaretoken"]').val()
    console.log("[v0] CSRF Token para get_plan_cuentas:", csrftoken)

    $.ajax({
      url: window.location.pathname,
      type: "POST",
      data: {
        action: "get_plan_cuentas",
        empresa_id: empresa_id,
        csrfmiddlewaretoken: csrftoken,
      },
      dataType: "json",
      headers: {
        "X-CSRFToken": csrftoken,
      },
      success: (response) => {
        console.log("[v0] Plan de cuentas cargado:", response)
        const select = $("#categoria_contable_id")
        select.html('<option value="">Seleccione cuenta</option>')

        if (response.error) {
          Swal.fire("Error", response.error, "error")
          return
        }

        response.forEach((cuenta) => {
          select.append(`<option value="${cuenta.id}">${cuenta.descripcion}</option>`)
        })
      },
      error: (xhr, status, error) => {
        console.error("[v0] Error al cargar plan de cuentas:", error)
        console.error("[v0] Status:", status)
        console.error("[v0] Response:", xhr.responseText)
        Swal.fire("Error", "No se pudo cargar el plan de cuentas: " + error, "error")
      },
    })
  },

  calcularTotal: () => {
    let total = 0
    $.each(anticipo.items.formas_pago, (key, value) => {
      total += Number.parseFloat(value.valor) || 0
    })
    return total
  },
}

function cargarPlanCuentas() {
  anticipo.cargarPlanCuentas()
}

function abrirModalFormaPago() {
  $("#fp_valor").val("")
  $("#fp_tipo").val("")
  $("#fp_forma").val("")
  $("#fp_referencia").val("")
  $("#fp_banco").val("")
  $("#fp_observacion").val("")
  $("#modalFormaPago").modal("show")
}

function abrirNuevoTipoPago() {
  const tiposWindow = window.open("{% url 'app_anticipos:tipo_pago_list' %}", "tipos_pago", "width=900,height=600")
  // Recargar select de tipos después de cerrar la ventana
  const checkWindow = setInterval(() => {
    if (tiposWindow.closed) {
      clearInterval(checkWindow)
      recargarSelectTipos()
    }
  }, 500)
}

function abrirNuevaFormaPago() {
  const formasWindow = window.open("{% url 'app_anticipos:forma_pago_list' %}", "formas_pago", "width=900,height=600")
  // Recargar select de formas después de cerrar la ventana
  const checkWindow = setInterval(() => {
    if (formasWindow.closed) {
      clearInterval(checkWindow)
      recargarSelectFormas()
    }
  }, 500)
}

function recargarSelectTipos() {
  console.log("[v0] Recargando select de tipos...")
  const csrftoken = $('input[name="csrfmiddlewaretoken"]').val()
  $.ajax({
    url: "{% url 'app_anticipos:tipo_pago_list' %}",
    type: "POST",
    data: {
      action: "list",
      csrfmiddlewaretoken: csrftoken,
    },
    headers: {
      "X-CSRFToken": csrftoken,
    },
    dataType: "json",
    success: (response) => {
      const select = $("#fp_tipo")
      const currentValue = select.val()
      select.html('<option value="">Seleccione...</option>')
      response.forEach((tipo) => {
        select.append(`<option value="${tipo.id}">${tipo.nombre}</option>`)
      })
      select.val(currentValue)
    },
  })
}

function recargarSelectFormas() {
  console.log("[v0] Recargando select de formas...")
  const csrftoken = $('input[name="csrfmiddlewaretoken"]').val()
  $.ajax({
    url: "{% url 'app_anticipos:forma_pago_list' %}",
    type: "POST",
    data: {
      action: "list",
      csrfmiddlewaretoken: csrftoken,
    },
    headers: {
      "X-CSRFToken": csrftoken,
    },
    dataType: "json",
    success: (response) => {
      const select = $("#fp_forma")
      const currentValue = select.val()
      select.html('<option value="">Seleccione...</option>')
      response.forEach((forma) => {
        select.append(`<option value="${forma.id}">${forma.nombre}</option>`)
      })
      select.val(currentValue)
    },
  })
}

function agregarFormaPago() {
  const valor = Number.parseFloat($("#fp_valor").val())
  const tipo_id = $("#fp_tipo").val()
  const forma_id = $("#fp_forma").val()
  const referencia = $("#fp_referencia").val()
  const banco = $("#fp_banco").val()
  const observacion = $("#fp_observacion").val()

  if (!valor || valor <= 0) {
    Swal.fire("Error", "Ingrese un valor válido", "error")
    return
  }
  if (!tipo_id) {
    Swal.fire("Error", "Seleccione un tipo", "error")
    return
  }
  if (!forma_id) {
    Swal.fire("Error", "Seleccione una forma", "error")
    return
  }

  // Obtener textos de los select
  const tipo_text = $("#fp_tipo option:selected").text()
  const forma_text = $("#fp_forma option:selected").text()

  anticipo.items.formas_pago.push({
    tipo_id: tipo_id,
    tipo_text: tipo_text,
    forma_id: forma_id,
    forma_text: forma_text,
    valor: valor,
    referencia: referencia,
    banco: banco,
    observacion: observacion,
  })

  console.log("[v0] Forma de pago agregada:", anticipo.items.formas_pago)

  // Actualizar tabla y monto
  actualizarTablaFormasPago()
  actualizarMonto()

  $("#modalFormaPago").modal("hide")
}

function actualizarTablaFormasPago() {
  const tbody = $("#tblFormasPago tbody")
  tbody.html("")

  $.each(anticipo.items.formas_pago, (index, row) => {
    const tr = `
      <tr>
        <td><a rel="remove" class="btn btn-danger btn-xs" style="color: white;"><i class="fas fa-trash"></i></a></td>
        <td>${row.tipo_text}</td>
        <td>${row.forma_text}</td>
        <td align="right">$${Number.parseFloat(row.valor).toFixed(2)}</td>
        <td>${row.referencia || ""}</td>
        <td>${row.banco || ""}</td>
        <td>${row.observacion || ""}</td>
      </tr>
    `
    tbody.append(tr)
  })

  // Event listener para borrar
  $("#tblFormasPago tbody").on("click", 'a[rel="remove"]', function () {
    const tr = $(this).closest("tr").index()
    anticipo.items.formas_pago.splice(tr, 1)
    actualizarTablaFormasPago()
    actualizarMonto()
  })
}

function actualizarMonto() {
  const total = anticipo.calcularTotal()
  $("#monto").val(total.toFixed(2))
  $("#total_formas_pago").text(total.toFixed(2))
}

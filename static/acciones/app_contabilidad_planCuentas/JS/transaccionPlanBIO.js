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
        }

        tbl_transaccionPlan = $("#tbl_transaccionPlan").DataTable({
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
            dom: "rtip",
            bPaginate: false,
            responsive: true,
            autoWidth: false,
            bFilter: false,
            scrollY: "305px",
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
                        '<input type="text" name="detalle" class="form-control text-center border-0" autocomplete="off" value="' +
                        (row.detalle != null ? row.detalle : "") +
                        '">',
                },
                {
                    targets: [-2],
                    class: "text-center",
                    orderable: false,
                    render: (data, type, row) =>
                        '<input type="text" name="debe" class="form-control text-center border-0" autocomplete="off" value="' +
                        Number.parseFloat(row.debe > 0 ? row.debe : 0).toFixed(2) +
                        '">',
                },
                {
                    targets: [-1],
                    class: "text-center",
                    orderable: false,
                    render: (data, type, row) =>
                        '<input type="text" name="haber" class="form-control text-center border-0" autocomplete="off" value="' +
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
        '<div class="wrapper container">' +
        '<div class="row">' +
        '<div class="col-lg-1">' +
        "<i class='fa fa-sort-amount-down-alt'></i>" +
        "</div>" +
        '<div class="col-lg-11">' +
        '<p style="margin-bottom: 0;">' +
        "<b>Codigo:</b>" +
        "&nbsp;&nbsp;&nbsp;" +
        repo.codigo +
        "<br>" +
        "<b>Nombre:</b>" +
        "&nbsp;&nbsp;" +
        repo.nombre +
        "<br>" +
        "<b>Nivel:</b>" +
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" +
        repo.nivel +
        "<br>" +
        "<b>Detalle de Cuenta Padre:</b>" +
        "&nbsp;&nbsp;" +
        repo.cuenta_padre +
        "<br>" +
        "</p>" +
        "</div>" +
        "</div>" +
        "</div>",
    )

    return option
}

// OPTIMIZACIÓN CLAVE: Función para cargar el plan de cuentas de forma eficiente
function loadPlanCuentasBIO() {
    // 1. MOSTRAR EL MODAL INMEDIATAMENTE (sin esperar a la carga de datos)
    $("#myModalSearchPlan").modal("show")

    // 2. Mostrar indicador de carga en el modal
    $("#table-tree").html(
        '<tr><td colspan="5" class="text-center"><div class="spinner-border text-primary" role="status"></div><p class="mt-2">Cargando datos...</p></td></tr>',
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
                '<tr><td colspan="5" class="text-center text-danger">Error al cargar los datos. <button class="btn btn-sm btn-primary" onclick="loadPlanCuentasBIO()">Reintentar</button></td></tr>',
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

    // Si ya existe una instancia de DataTable, destruirla
    if ($.fn.DataTable.isDataTable("#tblSearchPlan")) {
        $("#tblSearchPlan").DataTable().destroy()
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
                sFirst: "Primero",
                sLast: "Último",
                sNext: "Siguiente",
                sPrevious: "Anterior",
            },
            zeroRecords: "Ningun dato disponible en esta tabla",
            sInfo: "Registros del _START_ al _END_ de un total de _TOTAL_ registros",
            infoEmpty: "Tabla vacia por favor inserte datos",
            lengthMenu: "Listando _MENU_ registros",
            sSearch: "Buscar:",
            infoFiltered: "(filtrado de _MAX_ registros totales)",
        },
        dom: "frtip",
        bPaginate: false,
        ordering: false,
        responsive: true,
        autoWidth: false,
        scrollY: "305px",
        destroy: true,
        deferRender: true,
        search: {
            return: true,
        },
        // Opciones para mejorar rendimiento
        processing: true,
        pageLength: 100,
        initComplete: () => {
            // Enfocar el campo de búsqueda para facilitar la búsqueda rápida
            $("#tblSearchPlan_filter input").focus()
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

$(() => {
    // Inicialización de componentes
    $(".select2").select2({
        theme: "bootstrap4",
        language: "es",
    })

    // Evento para abrir el modal de búsqueda
    $("#btnBuscarPlanBIO").on("click", () => {
        loadPlanCuentasBIO()
    })

    // Evento para agregar un plan desde el modal
    $(document).on("click", '#tblSearchPlan tbody a[rel="add"]', function () {
        // Obtener la fila actual
        var row = $(this).closest("tr")

        // Obtener los datos de la fila
        var codigo = row.find("td:eq(0)").text()
        var tipo_cuenta = row.find("td:eq(1)").text()
        var nombre = row.find("td:eq(2)").text()
        var empresa = row.find("td:eq(3)").text()

        // Crear el objeto con los datos necesarios
        var item = {
            id: Date.now(), // Usar timestamp como ID único
            codigo: codigo,
            nombre: nombre,
            tipo_cuenta: tipo_cuenta,
            detalle: $('input[name="descripcion"]').val() || "",
            debe: 0.0,
            haber: 0.0,
        }

        // Agregar el item a la lista de productos
        vents.add(item)

        // Eliminar la fila del modal
        row.remove()

        // Actualizar la caché para reflejar la eliminación
        if (planCuentasCache) {
            var index = -1
            for (var i = 0; i < planCuentasCache.length; i++) {
                if (planCuentasCache[i].codigo === codigo) {
                    index = i
                    break
                }
            }
            if (index !== -1) {
                planCuentasCache.splice(index, 1)
            }
        }
    })

    // Mantener el resto de eventos originales
    $("select[name='tip_cuenta']").on("change", function () {
        var cuenta = $(this).val()
        var fecha = fecha_actual
        var extraer_mes = fecha.getMonth()
        var mes_exacto = extraer_mes + 1

        if (mes_exacto < 10) {
            $('input[name="codigo"]').val("0" + mes_exacto + cuenta)
        } else {
            $('input[name="codigo"]').val(mes_exacto + cuenta)
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
                    location.href = "/app_planCuentas/listar_transaccionPlan_bio/"
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
            data.detalle = $('input[name="descripcion"]').val()
            data.debe = 0.0
            data.haber = 0.0
            vents.add(data)
            $(this).val("").trigger("change.select2")
        })

    // Inicializar la tabla
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
    if (typeof Swal !== "undefined") {
        Swal.fire({
            title: "Error",
            text: message,
            icon: "error",
        })
    } else {
        alert(message)
    }
}

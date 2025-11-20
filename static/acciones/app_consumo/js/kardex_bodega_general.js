/*
let datosKardex = [];
let productosListado = [];

document.addEventListener('DOMContentLoaded', function() {
    console.log('[v0] Inicializando Kardex Bodega - Modo Horizontal');
    inicializarDateRange();

    // Asignar eventos a botones
    document.getElementById('btn_buscar').addEventListener('click', buscarKardex);
    document.getElementById('btn_excel').addEventListener('click', exportarExcel);
    document.getElementById('btn_pdf').addEventListener('click', exportarPDF);
    document.getElementById('btn_imprimir').addEventListener('click', function() {
        window.print();
    });

    console.log('[v0] Kardex inicializado correctamente');
});

function inicializarDateRange() {
    console.log('[v0] Inicializando DateRangePicker');

    moment.locale('es');
    const hoy = moment();
    const hace30dias = moment().subtract(30, 'days');

    $('#daterange').daterangepicker({
        startDate: hace30dias,
        endDate: hoy,
        locale: {
            format: 'YYYY-MM-DD',
            applyLabel: 'Aplicar',
            cancelLabel: 'Cancelar',
            customRangeLabel: 'Personalizado',
            daysOfWeek: ['Do', 'Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sa'],
            monthNames: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        },
        ranges: {
            'Hoy': [moment(), moment()],
            'Últimos 7 días': [moment().subtract(6, 'days'), moment()],
            'Últimos 30 días': [moment().subtract(29, 'days'), moment()],
            'Este mes': [moment().startOf('month'), moment().endOf('month')],
            'Mes anterior': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
        }
    });

    console.log('[v0] DateRangePicker inicializado');
}

function buscarKardex() {
    const daterange = $('#daterange').data('daterangepicker');
    if (!daterange) {
        alert('Por favor, selecciona un rango de fechas');
        return;
    }

    const start_date = daterange.startDate.format('YYYY-MM-DD');
    const end_date = daterange.endDate.format('YYYY-MM-DD');

    console.log('[v0] Buscando kardex de', start_date, 'a', end_date);

    $.ajax({
        type: 'POST',
        url: window.location.pathname,
        data: {
            action: 'get_kardex_horizontal',
            start_date: start_date,
            end_date: end_date,
            csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
        },
        dataType: 'json',
        success: function(response) {
            console.log('[v0] Datos recibidos:', response);
            datosKardex = response.datos;
            productosListado = response.productos;
            construirTablaHorizontal();
        },
        error: function(xhr, status, error) {
            console.error('[v0] Error al buscar:', error);
            alert('Error al cargar datos: ' + error);
        }
    });
}

function construirTablaHorizontal() {
    console.log('[v0] Construyendo tabla horizontal con', datosKardex.length, 'filas');

    if (datosKardex.length === 0) {
        $('#tbody_kardex').html('<tr><td colspan="100" class="text-center text-muted">No hay datos disponibles</td></tr>');
        return;
    }

    let headerHTML = `<th class="col-fecha">FECHA</th><th class="col-empresa">EMPRESA</th>`;

    productosListado.forEach(prod => {
        headerHTML += `<th colspan="3" class="seccion-campo text-center">${prod.substring(0, 20)}</th>`;
    });

    $('#header_productos').html(headerHTML);

    let subHeaderHTML = `<tr class="thead-dark"><th></th><th></th>`;
    productosListado.forEach(prod => {
        subHeaderHTML += `<th class="dato-ingreso text-center">ING</th><th class="dato-egreso text-center">EGR</th><th class="dato-stock text-center">STK</th>`;
    });
    subHeaderHTML += `</tr>`;

    // Insertar subencabezado después del encabezado principal
    let headerRow = $('#header_productos');
    if (headerRow.next().hasClass('thead-dark')) {
        headerRow.next().remove(); // Remover fila antigua
    }
    headerRow.after(subHeaderHTML);

    let bodyHTML = '';
    let fechaActual = '';

    datosKardex.forEach(fila => {
        // Separador de fecha
        if (fila.fecha !== fechaActual) {
            if (fechaActual !== '') {
                bodyHTML += '<tr style="height: 8px;"><td colspan="100"></td></tr>';
            }
            fechaActual = fila.fecha;
        }

        bodyHTML += `<tr class="row-empresa">`;
        bodyHTML += `<td class="col-fecha">${fila.fecha}</td>`;
        bodyHTML += `<td class="col-empresa"><strong>${fila.empresa}</strong></td>`;

        // Datos de cada producto
        productosListado.forEach(prod => {
            const prodData = fila.productos[prod] || { ingreso: 0, egreso: 0, stock: 0, unidad: '' };

            bodyHTML += `<td class="dato-ingreso text-center">${prodData.ingreso > 0 ? prodData.ingreso.toFixed(2) : '-'}</td>`;
            bodyHTML += `<td class="dato-egreso text-center">${prodData.egreso > 0 ? prodData.egreso.toFixed(2) : '-'}</td>`;
            bodyHTML += `<td class="dato-stock text-center">${prodData.stock > 0 ? prodData.stock.toFixed(2) : '-'}</td>`;
        });

        bodyHTML += `</tr>`;
    });

    $('#tbody_kardex').html(bodyHTML);
    console.log('[v0] Tabla construida correctamente');
}

function exportarExcel() {
    if (datosKardex.length === 0) {
        alert('No hay datos para exportar. Realiza una búsqueda primero.');
        return;
    }

    console.log('[v0] Exportando a Excel');

    let workbookData = [];

    // Encabezado
    let headerRow = ['FECHA', 'EMPRESA'];
    productosListado.forEach(prod => {
        headerRow.push(prod + ' (ING)', prod + ' (EGR)', prod + ' (STOCK)');
    });
    workbookData.push(headerRow);

    // Datos
    datosKardex.forEach(fila => {
        let row = [fila.fecha, fila.empresa];
        productosListado.forEach(prod => {
            const prodData = fila.productos[prod] || { ingreso: 0, egreso: 0, stock: 0 };
            row.push(
                prodData.ingreso > 0 ? prodData.ingreso : '',
                prodData.egreso > 0 ? prodData.egreso : '',
                prodData.stock > 0 ? prodData.stock : ''
            );
        });
        workbookData.push(row);
    });

    const ws = XLSX.utils.aoa_to_sheet(workbookData);

    // Ajustar ancho de columnas
    let columnWidths = [
        { wch: 15 }, // FECHA
        { wch: 15 }  // EMPRESA
    ];
    productosListado.forEach(() => {
        columnWidths.push({ wch: 12 }, { wch: 12 }, { wch: 12 });
    });
    ws['!cols'] = columnWidths;

    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Kardex');

    const nombreArchivo = 'Kardex_Bodega_' + moment().format('YYYY-MM-DD_HHmm') + '.xlsx';
    XLSX.writeFile(wb, nombreArchivo);

    console.log('[v0] Excel exportado:', nombreArchivo);
}

function exportarPDF() {
    if (datosKardex.length === 0) {
        alert('No hay datos para exportar. Realiza una búsqueda primero.');
        return;
    }

    console.log('[v0] Exportando a PDF');

    const elemento = document.getElementById('kardex_container');
    const opt = {
        margin: [5, 5, 5, 5],
        filename: 'Kardex_Bodega_' + moment().format('YYYY-MM-DD_HHmm') + '.pdf',
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true },
        jsPDF: { orientation: 'landscape', unit: 'mm', format: 'a4' }
    };

    // Usar html2pdf si está disponible
    if (typeof html2pdf !== 'undefined') {
        html2pdf().set(opt).from(elemento).save();
    } else {
        console.warn('[v0] html2pdf no está disponible, usando impresión en su lugar');
        window.print();
    }
}
*/




let datosJerarquia = {};     // datos recibidos (empresa -> piscina -> fecha -> producto)
let productosListado = [];   // lista de productos (columnas)
let categorias = {};         // producto -> categoria

$(document).ready(function() {
    moment.locale('es');

    $('#daterange').daterangepicker({
        startDate: moment().subtract(30, 'days'),
        endDate: moment(),
        locale: { format: 'YYYY-MM-DD' }
    });

    $('#btn_buscar').click(function() { buscarKardex(); });
    $('#btn_excel').click(function() { exportarExcel(); });
    $('#btn_pdf').click(function() { exportarPDF(); });
    $('#btn_imprimir').click(function() { window.print(); });
});

function buscarKardex() {
    const dr = $('#daterange').data('daterangepicker');
    if(!dr){ alert('Selecciona un rango'); return; }
    const start_date = dr.startDate.format('YYYY-MM-DD');
    const end_date = dr.endDate.format('YYYY-MM-DD');
    const empresa = $('#select_empresa').val() || '';

    $.ajax({
        type: 'POST',
        url: window.location.pathname,
        data: {
            action: 'get_kardex_horizontal',
            start_date: start_date,
            end_date: end_date,
            empresa: empresa,
            csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
        },
        dataType: 'json',
        success: function(resp) {
            if(resp.status !== 'ok'){ alert('Error al cargar datos'); return; }
            datosJerarquia = resp.datos || {};
            productosListado = resp.productos || [];
            categorias = resp.categorias || {};
            renderTablaPorEmpresaPiscina();
        },
        error: function(xhr, st, err){
            console.error(err); alert('Error: ' + err);
        }
    });
}

function clasePorCategoria(cat){
    // map categoria a clase CSS
    if(!cat) return 'seccion-otros';
    cat = cat.toString().toLowerCase();
    if(cat.indexOf('balance') !== -1 || cat.indexOf('balanc') !== -1) return 'seccion-balanceado';
    if(cat.indexOf('campo') !== -1 || cat.indexOf('eco') !== -1 || cat.indexOf('bio') !== -1) return 'seccion-campo';
    if(cat.indexOf('camaron') !== -1 || cat.indexOf('shrimp') !== -1) return 'seccion-camarones';
    return 'seccion-otros';
}

function renderTablaPorEmpresaPiscina(){
    const $tbody = $('#tbody_kardex');
    $tbody.empty();

    if(Object.keys(datosJerarquia).length === 0){
        $tbody.html('<tr><td colspan="200" class="text-center text-muted">No hay datos</td></tr>');
        return;
    }

    // Construir encabezado dinámico: productos (colspan 3 por producto)
    let headerHTML = `<th class="col-fecha">FECHA</th><th class="col-empresa">EMPRESA / PISCINA</th>`;
    productosListado.forEach(prod => {
        // usamos la categoria del producto para colorear el encabezado de esa columna
        const cat = categorias[prod] || '';
        const cls = clasePorCategoria(cat);
        headerHTML += `<th colspan="3" class="${cls} text-center" title="${prod}">${prod.length>18?prod.substring(0,18)+'...':prod}</th>`;
    });
    $('#header_productos').html(headerHTML);

    // Sub-encabezado (ING EGR STK por producto)
    let subHeader = `<tr class="thead-dark"><th></th><th></th>`;
    productosListado.forEach(_ => {
        subHeader += `<th class="dato-ingreso">ING</th><th class="dato-egreso">EGR</th><th class="dato-stock">STK</th>`;
    });
    subHeader += `</tr>`;
    // eliminar subheader previo si existe
    if($('#header_productos').next().hasClass('thead-dark')) $('#header_productos').next().remove();
    $('#header_productos').after(subHeader);

    // Recorremos empresa -> piscina -> fechas
    Object.keys(datosJerarquia).forEach(empresa => {
        // fila título empresa
        $tbody.append(`<tr><td colspan="200" style="background:#DCEFF8;font-weight:bold;font-size:14px;">EMPRESA: ${empresa}</td></tr>`);

        const piscinas = datosJerarquia[empresa];
        Object.keys(piscinas).forEach(piscina => {
            $tbody.append(`<tr><td colspan="200" style="background:#FFF3CD;font-weight:bold;">PISCINA: ${piscina}</td></tr>`);

            // Ordenar fechas asc
            const fechas = Object.keys(piscinas[piscina]).sort((a,b)=> {
                // formato dd-mm-yyyy => convertir a yyyy-mm-dd para ordenar
                const toIso = s => {
                    const parts = s.split('-'); if(parts.length!==3) return s;
                    return `${parts[2]}-${parts[1]}-${parts[0]}`;
                };
                return toIso(a) > toIso(b) ? 1 : -1;
            });

            fechas.forEach(fecha => {
                // fila con fecha (separador pequeño)
                $tbody.append(`<tr class="row-fecha"><td>${fecha}</td><td></td>${''}</tr>`);

                // fila datos por producto
                let filaHtml = `<tr class="row-empresa"><td class="col-fecha">${fecha}</td><td class="col-empresa"><strong>${empresa} / ${piscina}</strong></td>`;
                productosListado.forEach(prod => {
                    const mov = piscinas[piscina][fecha][prod] || { ingreso:0, egreso:0, stock: (0) };
                    filaHtml += `<td class="dato-ingreso">${mov.ingreso?Number(mov.ingreso).toFixed(2):''}</td>`;
                    filaHtml += `<td class="dato-egreso">${mov.egreso?Number(mov.egreso).toFixed(2):''}</td>`;
                    filaHtml += `<td class="dato-stock">${mov.stock?Number(mov.stock).toFixed(2):''}</td>`;
                });
                filaHtml += `</tr>`;
                $tbody.append(filaHtml);
            });

            // separación visual entre piscinas
            $tbody.append('<tr><td colspan="200" style="height:8px;background:#fff;"></td></tr>');
        });
    });
}

// Exportar Excel y PDF — pueden reutilizar tu implementacion previa; aquí solo llamamos a tus funciones existentes
function exportarExcel(){
    // si quieres, podemos construir un Excel por empresa/piscina o plano. Por ahora llamo a la función previa que generaba por filas planas:
    // Reconstruimos un arreglo plano con las filas mostradas para exportar.
    if(Object.keys(datosJerarquia).length === 0){ alert('No hay datos para exportar'); return; }

    let workbookData = [];
    // cabecera
    let header = ['EMPRESA','PISCINA','FECHA'];
    productosListado.forEach(p => {
        header.push(p + ' (ING)', p + ' (EGR)', p + ' (STK)');
    });
    workbookData.push(header);

    Object.keys(datosJerarquia).forEach(empresa => {
        const piscinas = datosJerarquia[empresa];
        Object.keys(piscinas).forEach(piscina => {
            Object.keys(piscinas[piscina]).forEach(fecha => {
                let row = [empresa, piscina, fecha];
                productosListado.forEach(prod => {
                    const mov = piscinas[piscina][fecha][prod] || { ingreso:0, egreso:0, stock:0 };
                    row.push(mov.ingreso || '', mov.egreso || '', mov.stock || '');
                });
                workbookData.push(row);
            });
        });
    });

    const ws = XLSX.utils.aoa_to_sheet(workbookData);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Kardex');
    const nombre = 'Kardex_Bodega_' + moment().format('YYYYMMDD_HHmm') + '.xlsx';
    XLSX.writeFile(wb, nombre);
}

function exportarPDF(){
    const elemento = document.getElementById('kardex_container');
    const opt = {
        margin: 5,
        filename: 'Kardex_Bodega_' + moment().format('YYYYMMDD_HHmm') + '.pdf',
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true },
        jsPDF: { orientation: 'landscape', unit: 'mm', format: 'a4' }
    };
    if(typeof html2pdf !== 'undefined'){
        html2pdf().set(opt).from(elemento).save();
    } else window.print();
}

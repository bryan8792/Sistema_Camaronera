var productos = [];
var datosTabla = [];

function cargarAnios() {
    $.ajax({
        url: window.location.pathname,
        type: 'POST',
        data: {
            'action': 'get_anios'
        },
        dataType: 'json'
    }).done(function(data) {
        var select = $('#select_anio');
        select.find('option:not(:first)').remove();

        if (Array.isArray(data)) {
            data.forEach(function(anio) {
                select.append('<option value="' + anio + '">' + anio + '</option>');
            });
        }
    }).fail(function(jqXHR, textStatus, errorThrown) {
        console.error('Error al cargar anios:', textStatus);
    });
}

function formatNumber(valor) {
    // Formatear numero con 2 decimales si tiene decimales, sino mostrar entero
    if (valor === 0 || valor === null || valor === undefined) {
        return '';
    }
    var num = parseFloat(valor);
    if (Number.isInteger(num)) {
        return num.toLocaleString('es-EC');
    } else {
        return num.toLocaleString('es-EC', {minimumFractionDigits: 2, maximumFractionDigits: 2});
    }
}

function cargarDatos() {
    var empresa = $('#select_empresa').val();
    var anio = $('#select_anio').val();

    // Mostrar loading
    $('#loading').show();
    $('#body_data').html('<tr><td colspan="100" class="text-center py-4"><span class="text-muted">Cargando datos...</span></td></tr>');

    $.ajax({
        url: window.location.pathname,
        type: 'POST',
        data: {
            'action': 'searchdata',
            'empresa': empresa,
            'anio': anio
        },
        dataType: 'json'
    }).done(function(response) {
        $('#loading').hide();

        if (response.error) {
            alert('Error: ' + response.error);
            return;
        }

        productos = response.productos || [];
        datosTabla = response.data || [];

        if (productos.length === 0) {
            $('#header_row').html('<th>MES</th>');
            $('#body_data').html('<tr><td colspan="100" class="text-center text-muted py-4">No se encontraron datos para los filtros seleccionados</td></tr>');
            return;
        }

        renderizarTabla();

    }).fail(function(jqXHR, textStatus, errorThrown) {
        $('#loading').hide();
        console.error('Error al cargar datos:', textStatus);
        $('#body_data').html('<tr><td colspan="100" class="text-center text-danger py-4">Error al cargar los datos</td></tr>');
    });
}

function renderizarTabla() {
    // Renderizar encabezados
    var headerHtml = '<th>MES</th>';
    productos.forEach(function(producto, index) {
        // Truncar nombre si es muy largo para el header vertical
        var nombreCorto = producto.length > 20 ? producto.substring(0, 17) + '...' : producto;
        headerHtml += '<th title="' + producto + '">' + nombreCorto + '</th>';
    });
    $('#header_row').html(headerHtml);

    // Renderizar datos
    var bodyHtml = '';
    datosTabla.forEach(function(fila, index) {
        var isTotal = fila.mes === 'Total general';
        var rowClass = isTotal ? 'class="total-row"' : '';

        bodyHtml += '<tr ' + rowClass + '>';
        bodyHtml += '<td>' + fila.mes + '</td>';

        productos.forEach(function(producto) {
            var valor = fila[producto] || 0;
            var displayVal = formatNumber(valor);

            // Clase para celdas con valor (no en fila total)
            var cellClass = '';
            if (valor > 0 && !isTotal) {
                cellClass = 'class="cell-with-value"';
            }

            bodyHtml += '<td ' + cellClass + '>' + displayVal + '</td>';
        });

        bodyHtml += '</tr>';
    });

    $('#body_data').html(bodyHtml);
}

function exportarExcel() {
    if (productos.length === 0 || datosTabla.length === 0) {
        alert('No hay datos para exportar');
        return;
    }

    var empresa = $('#select_empresa').val() || 'TODAS';
    var anio = $('#select_anio').val() || 'TODOS';

    // Crear datos para CSV con separador de punto y coma para Excel en espanol
    var csvContent = '\uFEFF'; // BOM para UTF-8

    // Encabezados
    csvContent += 'MES';
    productos.forEach(function(producto) {
        csvContent += ';' + producto.replace(/;/g, ',');
    });
    csvContent += '\n';

    // Datos
    datosTabla.forEach(function(fila) {
        csvContent += fila.mes;
        productos.forEach(function(producto) {
            var valor = fila[producto] || 0;
            // Usar coma como separador decimal para Excel en espanol
            var valorStr = valor > 0 ? valor.toString().replace('.', ',') : '';
            csvContent += ';' + valorStr;
        });
        csvContent += '\n';
    });

    // Descargar archivo
    var blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    var link = document.createElement('a');
    var url = URL.createObjectURL(blob);
    var fecha = new Date().toISOString().slice(0, 10).replace(/-/g, '');

    link.setAttribute('href', url);
    link.setAttribute('download', 'movimientos_por_producto_' + empresa + '_' + anio + '_' + fecha + '.csv');
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

$(function() {
    // Cargar anios disponibles
    cargarAnios();

    // Evento filtrar
    $('#btn_filtrar').on('click', function() {
        cargarDatos();
    });

    // Evento exportar
    $('#btn_exportar').on('click', function() {
        exportarExcel();
    });
});
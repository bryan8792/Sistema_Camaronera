/**
 * Created by Bryan Barrezueta.
 */
function correcto(mensaje) {
    setTimeout(function () {
        toastr.options = {
            closeButton: true,
            progressBar: true,
            showMethod: 'slideDown',
            "positionClass": "toast-bottom-right",
            timeOut: 4000
        };
        toastr.success(mensaje, 'Evaluador | ISO 25000:2014');
    }, 1300);
}

function informacion(mensaje) {
    setTimeout(function () {
        toastr.options = {
            closeButton: true,
            progressBar: true,
            showMethod: 'slideDown',
            "positionClass": "toast-bottom-right",
            timeOut: 4000
        };
        toastr.info(mensaje, 'Evaluador | ISO 25000:2014');
    }, 1300);
}

function fallo(mensaje) {
    setTimeout(function () {
        toastr.options = {
            closeButton: true,
            progressBar: true,
            showMethod: 'slideDown',
            "positionClass": "toast-bottom-right",
            timeOut: 4000
        };
        toastr.error(mensaje, 'Evaluador | ISO 25000:2014');
    }, 1300);
}

function peligro(mensaje) {
    setTimeout(function () {
        toastr.options = {
            closeButton: true,
            progressBar: true,
            showMethod: 'slideDown',
            "positionClass": "toast-bottom-right",
            timeOut: 4000
        };
        toastr.warning(mensaje, 'Evaluador | ISO 25000:2014');
    }, 1300);
}

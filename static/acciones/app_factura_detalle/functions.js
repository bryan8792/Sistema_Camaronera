function alert_action(title, content, callback, cancel) {
    $.confirm({
        theme: 'material',
        title: title,
        icon: 'fa fa-info',
        content: content,
        columnClass: 'small',
        typeAnimated: true,
        cancelButtonClass: 'btn-primary',
        draggable: true,
        dragWindowBorder: false,
        buttons: {
            info: {
                text: "Si",
                btnClass: 'btn-primary',
                action: function () {
                    callback();
                }
            },
            danger: {
                text: "No",
                btnClass: 'btn-red',
                action: function () {
                    cancel();
                }
            },
        }
    })
}


function alerta_error(obj) {
    Swal.fire({
        icon: 'error',
        title: 'Atención',
        text: obj
    })
}

function mensaje_succes(obj, icon) {
    Swal.fire({
        position: 'center',
        icon: icon,
        title: obj,
        showConfirmButton: false,
        timer: 1500
    })
}
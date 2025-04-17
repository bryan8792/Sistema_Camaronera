$(function () {

    $.contextMenu({
        selector: 'li',
        callback: function (key, options) {
            var m = "clicked: " + key + " on " + $(this).text();
            window.console && console.log(m);
        },
        items: {
            "create": {
                name: "Nuevo Elemento",
                icon: "add",
                callback: function (key, options) {
                    // Obtenemos el nodo del JSTree
                    var nodeId = $(this).attr('id');
                    var tree = $('#arbolBio').jstree(true);
                    var selectedNode = tree.get_node(nodeId);

                    // Extraer el código (está dentro del HTML del text)
                    var temp = $('<div>').html(selectedNode.text);
                    var codigo = temp.find('strong').text().trim();

                    let node = $.jstree.reference(this).get_node(this);
                    let parent_id = node.id;
                    let codigo_padre = node.original.codigo;

                    Swal.fire({
                        position: 'top-center',
                        icon: 'success',
                        title: 'Preparando Formulario',
                        showConfirmButton: false,
                        timer: 1000
                    });

                    // Redirigimos a la vista de creación con parámetros
                    location.href = `/planCuentas/crearPlanBIO/?parent_id=${parent_id}&codigo_padre=${codigo_padre}`;
                    return true;
                }
            },
            /*"edit": {
                name: "Editar Elemento",
                icon: "edit",
                callback: function (key, options) {
                    var nombresincortar = $(this).text().split(" ")[0].trim();
                    console.log("nombresincortar")
                    console.log(nombresincortar)
                    window.console && console.log(nombresincortar);
                    Swal.fire({
                        position: 'top-center',
                        icon: 'success',
                        title: 'Preparando Formulario',
                        showConfirmButton: false,
                        timer: 5500
                    });
                    location.href = '/planCuentas/actualizarPlanBIO/' + nombresincortar;
                    return true;
                }
            },*/
            /*"cut": {name: "Cut", icon: "cut"},
            "copy": {name: "Copy", icon: "copy"},
            "paste": {name: "Paste", icon: "paste"},*/
            "edit": {
                name: "Editar Elemento",
                icon: "edit",
                callback: function (key, options) {
                    var nodeId = $(this).attr('id'); // ID del nodo JSTree
                    console.log("ID del nodo:", nodeId);

                    Swal.fire({
                        position: 'top-center',
                        icon: 'success',
                        title: 'Preparando Formulario',
                        showConfirmButton: false,
                        timer: 2500
                    });

                    location.href = '/planCuentas/actualizarPlanBIO/' + nodeId;
                    return true;
                }
            },
            "delete": {
                name: "Eliminar Elemento",
                icon: "delete",
                callback: function (itemKey, opt, e) {
                    var nodeId = $(this).attr('id'); // ID del nodo JSTree
                    console.log("ID del nodo:", nodeId);
                    window.console && console.log(nodeId);
                    location.href = '/planCuentas/eliminarPlanBIO/' + nodeId;
                }
            },
            "sep1": "---------",
            "quit": {
                name: "Salir", icon: function ($element, key, item) {
                    return 'context-menu-icon context-menu-icon-quit';
                }
            }
        }
    });

    /*let dtos = [];
    let obterner = () => {
        $.ajax({
            url: window.location.pathname,
            type: 'POST',
            data: {
                'action': 'searchdataBIO',
                'empresa': 'BIO'
            },
            dataType: 'json',
            beforeSend: function () {
                Swal.fire({
                    title: 'Cargando Plan de Cuentas <br> Por favor espere...',
                    icon: 'success',
                    html: '<img src="https://i.gifer.com/ZZ5H.gif" alt="Cargando..." width="60">',
                    allowOutsideClick: false,
                    showConfirmButton: false,
                    didOpen: () => {
                        Swal.showLoading();
                    }
                });
            },
        }).done(function (data) {

            data.map(function (x) {
                if (x.parentId == null) {
                    dtos.push({
                        id: x.id.toString(),
                        parent: "#",
                        label: x.nombre,
                        amount: x.nivel,
                        codigo: x.codigo,
                        nivel: x.nivel
                    });
                } else {
                    dtos.push({
                        id: x.id.toString(),
                        parent: x.parentId.toString(),
                        label: x.nombre,
                        amount: x.nivel,
                        codigo: x.codigo,
                        nivel: x.nivel
                    });
                }
            })
            // dtos.forEach((e, i) => e.text = `<span class="context-menu-one"><label style="visibility: hidden">${e.id}</label> &nbsp;${e.codigo} &nbsp; ${e.label}</span><span class='amount'>${e.amount}&nbsp;&nbsp;&nbsp;&nbsp;</span> `);
            dtos.forEach((e, i) => e.text = `<span class="context-menu-one"><label style="visibility: hidden; display: inline-block; width: 50px;">${e.id}</label> &nbsp;&nbsp; <strong>${e.codigo}</strong> &nbsp;&nbsp;${e.label}</span> <span class="amount"><strong>Nivel ${e.amount}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; </strong></span>`);
            // dtos.forEach((e, i) => e.text = `<span class="context-menu-one"><label style="visibility: hidden">${e.id}</label> &nbsp;&nbsp; <strong>${e.codigo}</strong> &nbsp;&nbsp;<span class="badge badge-secondary">${e.label}</span></span> <span class="amount"><strong>Nivel ${e.amount}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; </strong></span>`);
            $("#arbolBio").jstree({
                core: {
                    data: dtos
                },
                plugins: ['wholerow']
            }).on('loaded', function () {
                $('#arbolBio').jstree('open_all');
            });
        }).always(function () {
            // Cerrar SweetAlert cuando los datos se han cargado
            Swal.close();
        });
    }

    obterner();*/


    /*$(function () {
        $('#arbolBio').jstree({
            core: {
                data: function (node, cb) {
                    $.ajax({
                        url: window.location.pathname,
                        type: 'POST',
                        data: {
                            action: 'get_children',
                            empresa: 'BIO',
                            parent_id: node.id === "#" ? "#" : node.id
                        },
                        dataType: 'json',
                        success: function (data) {
                            cb(data);
                        }
                    });
                }
            },
            plugins: ['wholerow']
        });
    });*/

    $(function () {
        Swal.fire({
            title: 'Cargando estructura...',
            html: '<img src="https://i.gifer.com/ZZ5H.gif" width="60">',
            allowOutsideClick: false,
            showConfirmButton: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });

        $('#arbolBio').jstree({
            core: {
                data: function (node, cb) {
                    $.ajax({
                        url: window.location.pathname,
                        type: 'POST',
                        data: {
                            action: 'get_plan',
                            empresa: 'BIO',
                            parent_id: node.id === "#" ? "#" : node.id
                        },
                        dataType: 'json',
                        success: function (data) {
                            cb(data);
                        }
                    });
                }
            },
            plugins: ['wholerow']
        }).on('ready.jstree', function () {
            Swal.close();
        });
    });


});

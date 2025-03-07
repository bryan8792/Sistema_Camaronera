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
                callback: function (data, type, row) {
                    Swal.fire({
                        position: 'top-center',
                        icon: 'success',
                        title: 'Preparando Formulario',
                        showConfirmButton: false,
                        timer: 5500
                    });
                    location.href = '/planCuentas/crearPlanBIO/';
                    return true;
                }
            },
            "edit": {
                name: "Editar Elemento",
                icon: "edit",
                callback: function (key, options) {
                    var nombresincortar = $(this).text().split(" ")[0].trim();
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
            },
            /*"cut": {name: "Cut", icon: "cut"},
            "copy": {name: "Copy", icon: "copy"},
            "paste": {name: "Paste", icon: "paste"},*/
            "delete": {
                name: "Eliminar Elemento",
                icon: "delete",
                callback: function (itemKey, opt, e) {
                    var nombresincortar = $(this).text().split(" ")[0].trim();
                    window.console && console.log(nombresincortar);
                    location.href = '/planCuentas/eliminarPlanBIO/' + nombresincortar;
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

    // $('#the-node').on('click', function (e) {
    //     console.log('Se ha seleccionado', this);
    // });

    // $.contextMenu({
    //     selector: '.context-menu-one',
    //     items: $.contextMenu.fromMenu($('#html5menu'))
    // });

    // $('#jstree_cats').jstree();


    let dtos = [];
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
                    dtos.push({id: x.id.toString(), parent: "#", label: x.nombre, amount: x.nivel, codigo: x.codigo, nivel: x.nivel});
                } else {
                    dtos.push({id: x.id.toString(), parent: x.parentId.toString(), label: x.nombre, amount: x.nivel, codigo: x.codigo, nivel: x.nivel});
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

    obterner();



    /*$('#jstree').jstree({
        core: {
            data: function () {

                $.ajax({
                    url: window.location.pathname,
                    type: 'POST',
                    data: {
                        'action': 'searchdata'
                    },
                    dataType: 'json',

                }).done(function (data) {
                    console.log('data')
                    //console.log(data)
                    data.map(function (x) {
                        console.log(x.id)
                        console.log(x.codigo)
                        console.log(x.nombre)
                        console.log(x.nivel)
                        console.log(x.tipo_cuenta)
                        console.log(x.estado)
                        console.log(x.empresa)
                        console.log(x.periodo)
                        console.log(x.cuentasuma)
                        // lo que pasa que esto quiero presentar en el html estaba haciendo esto
                    })
                    data.forEach(function (element, el) {
                        //console.log('element')
                        //console.log(element)
                        //console.log('el')
                        //console.log(el)
                        //return `${element.codigo}<span class='amount'>${element.nombre}</span>`
                        // LO DE AQUI NO SE COMO HACER PARA QUE SE ME PRESENTE EL <UL> <LI>
                    })

                    /!*var tableData = '<ul>';
                    $.each(data, function (key, value) {
                        console.log('key')
                        console.log(key)
                        console.log('value')
                        console.log(value)

                        tableData += '<li style="text-align: center">' + value.nombre + '<span class="amount">' + value.c + '</li>'

                    });
                    tableData += '</ul>';
                    document.getElementById("jstree").innerHTML = tableData;*!/

                    /!*data.map(function (key, value) {
                        console.log('key')
                        console.log(key)
                        console.log('value')
                        console.log(value)

                    })*!/
                }).fail(function (jqXHR, textStatus, errorThrown) {
                    alert(textStatus + ': ' + errorThrown);
                }).always(function (data) {
                    //console.log('Operacion realizada correctamente'+data)
                })

            }
        },
        // plugins: ['wholerow']
    }).on('loaded.jstree',function (e) {
        console.log('e')
        console.log(e)
        $('#jstree').jstree('open_all');
  });
*/

    /*$('#using_json').jstree({
        'core': {
            'data': [
                {"id": "ajson1", "parent": "#", "text": "Simple root node"},
                {"id": "ajson2", "parent": "#", "text": "Root node 2"},
                {"id": "ajson3", "parent": "ajson2", "text": "Child 1"},
                {"id": "ajson4", "parent": "ajson2", "text": "Child 2"},
                {"id": "ACTIVO", "parent": "#", "text": "ACTIVO"},
                {"id": "PASIVO", "parent": "#", "text": "PASIVO"},
                {"id": "PATRIMONIO NETO", "parent": "#", "text": "PATRIMONIO NETO"},
                {"id": "INGRESOS", "parent": "#", "text": "INGRESOS"},
                {"id": "EGRESOS", "parent": "#", "text": "EGRESOS"},
                {"id": "GASTOS E INGRESOS POR IMP.DIFERIDO", "parent": "#", "text": "GASTOS E INGRESOS POR IMP.DIFERIDO"},
                {"id": "ACTIVO CORRIENTE", "parent": "ACTIVO", "text": "ACTIVO CORRIENTE"},
                {"id": "ACTIVO NO CORRIENTE", "parent": "ACTIVO", "text": "ACTIVO NO CORRIENTE"},
                {"id": "PASIVO CORRIENTE", "parent": "PASIVO", "text": "PASIVO CORRIENTE"},
                {"id": "PASIVO NO CORRIENTE", "parent": "PASIVO", "text": "PASIVO NO CORRIENTE"},
                {"id": "CAPITAL", "parent": "PATRIMONIO NETO", "text": "CAPITAL"},
                {"id": "APORTES DE SOCIOS O ACCIONISTAS PARA FUT", "parent": "PATRIMONIO NETO", "text": "APORTES DE SOCIOS O ACCIONISTAS PARA FUT"},
                {"id": "PRIMA POR EMISIÓN PRIMARIA DE ACCIONES", "parent": "PATRIMONIO NETO", "text": "PRIMA POR EMISIÓN PRIMARIA DE ACCIONES"},
                {"id": "RESERVAS", "parent": "PATRIMONIO NETO", "text": "RESERVAS"},
            ]
        }
    });*/

});

from django.forms import *
from django import forms
from datetime import datetime
from app_contabilidad_planCuentas.models import *

OPCIONES_NIVEL = (
    ('', '---------'),
    ('1', 'Nivel 1'),
    ('2', 'Nivel 2'),
    ('3', 'Nivel 3'),
    ('4', 'Nivel 4'),
    ('5', 'Nivel 5'),
    ('6', 'Nivel 6'),
    ('7', 'Nivel 7'),
)

OPCIONES_ESTADO = (
    ('', '---------'),
    ('Activo', 'Activo'),
    ('Inactivo', 'Inactivo'),
)

OPCIONES_CUENTA = (
    ('', '---------'),
    ('GENERAL', 'GENERAL'),
    ('DETALLE', 'DETALLE'),
)

OPCIONES_TIPO_COMPROBANTE = (
    ('', '---------'),
    ('1', '01 FACTURA'),
    ('2', '02 NOTA O BOLETO VENTA'),
    ('4', '04 NOTA CREDITO'),
    ('5', '05 NOTA DEBITO'),
    ('12', '12 DOC. EMIT. INST. FIN'),
    ('19', '19 DOC. PAG. DE CUOTA/APORTE'),
    ('20', '20 SERV. ADM. DEL ESTADO'),
)

OPCIONES_ENCABEZADO_PLAN = (
    ('', '----------'),
    ('1', 'DIARIO CONTABLE'),
    ('2', 'COMPROBANTE PAGO'),
    ('3', 'INGRESO A CAJA'),
    ('4', 'EGRESO DE CAJA'),
    ('5', 'COMPROBANTE SISTEMA'),
)

OPCIONES_TRANSACCION_PLAN = (
    ('', '----------'),
    ('1', 'COMPRAS-RET'),
    ('2', 'VENTAS-RET'),
    ('3', 'NINGUNO (COMP-VTA)'),
    ('4', 'ANULADO (COMP)'),
    ('5', 'ANULADO (CH)'),
    ('6', 'COMPRAS NO RET'),
    ('7', 'VENTAS NO RET'),
)

OPCIONES_FORM_CIENTOCUATRO_BASE_CERO = (
    ('0', '-------'),
    ('403', '403'),
    ('507', '507'),
    ('508', '508'),
    ('535', '535'),
)

OPCIONES_FORM_CIENTOCUATRO_BASE_IVA_NORMAL = (
    ('0', '-------'),
    ('402', '402'),
    ('501', '501'),
    ('502', '502'),
    ('508', '508'),
    ('535', '535'),
)

OPCIONES_FORM_CIENTOCUATRO_BASE_IVA_BIENES = (
    ('0', '-------'),
    ('500', '500'),
    ('540', '540'),
)

OPCIONES_IVA_NORMAL_PORCEN = (
    ('0', '-------'),
    ('15', '15.00'),
)

OPCIONES_IVA_BIENES_PORCEN = (
    ('0', '-------'),
    ('5', '5.00'),
)

OPCIONES_ICE_PORCEN = (
    ('0', '-------'),
    ('1', '1.00'),
)

OPCIONES_RET_IVA_CERO = (
    ('0', '-------'),
    ('1', '725'),
)

OPCIONES_RET_IVA_DIEZ = (
    ('0', '-------'),
    ('721', '721'),
)

OPCIONES_RET_IVA_VEINT = (
    ('0', '-------'),
    ('723', '723'),
)

OPCIONES_RET_IVA_TREINT = (
    ('0', '-------'),
    ('725', '725'),
)

OPCIONES_RET_IVA_CINC = (
    ('0', '-------'),
    ('727', '727'),
)

OPCIONES_RET_IVA_SETEN = (
    ('0', '-------'),
    ('1', '729'),
)

OPCIONES_RET_IVA_CIEN = (
    ('0', '-------'),
    ('731', '731'),
)

OPCIONES_RET_FUEN_ANEXO_UNO = (
    ('0', '-------'),
    ('312', '312 Transf bienes muebles,'),
    ('343', '343 Otras retenciones aplicadas'),
)

OPCIONES_RET_FUEN_ANEXO_DOS = (
    ('0', '-------'),
    ('312', '312 Transf bienes muebles,'),
)

OPCIONES_RET_FUEN_ANEXO_TRES = (
    ('0', '-------'),
    ('312', '312 Transf bienes muebles,'),
)

OPCIONES_F_PAGO = (
    ('', '-------'),
    ('SUIF', '1. SIN UTILIZACION SISTEMA FINANCIERO'),
)

OPCIONES_T_F_PAGO = (
    ('', '-------'),
    ('NINGUNO', '6. NINGUNO'),
)


class PlanCuentaForm(ModelForm):
    # Definir empresa manualmente para evitar dependencia circular
    empresa = forms.ModelChoiceField(
        queryset=None,
        required=False,
        widget=Select(attrs={
            'class': 'form-control select2',
            'placeholder': 'Selecciona una Empresa',
            'autocomplete': 'off'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from app_empresa.app_reg_empresa.models import Empresa
        self.fields['empresa'].queryset = Empresa.objects.all()

    class Meta:
        model = PlanCuenta
        exclude = ['empresa']  # Excluir empresa - se define arriba manualmente
        widgets = {
            'codigo': NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese un Codigo',
                    'autocomplete': 'off'
                }
            ),
            'nombre': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Nombre de la Cuenta',
                    'autocomplete': 'off'
                }
            ),
            'periodo': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese un Periodo',
                    'autocomplete': 'off'
                }
            ),
            'tipo_cuenta': Select(choices=OPCIONES_CUENTA,
                                  attrs={
                                      'class': 'form-control select2'
                                  }
                                  ),
            'nivel': Select(choices=OPCIONES_NIVEL,
                            attrs={
                                'class': 'form-control select2'
                            }
                            ),
            'parentId': Select(
                attrs={
                    'class': 'form-control select2',
                }
            ),
        }


class EncabezadoCuentasPlanCuentaForm(ModelForm):
    empresa = forms.ModelChoiceField(
        queryset=None,
        required=False,
        widget=Select(attrs={
            'class': 'form-control select2',
            'autocomplete': 'off',
            'style': 'width: 100%;'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from app_empresa.app_reg_empresa.models import Empresa
        self.fields['empresa'].queryset = Empresa.objects.all()

    class Meta:
        model = EncabezadoCuentasPlanCuenta
        exclude = ['empresa']
        widgets = {
            'codigo': NumberInput(
                attrs={
                    'class': 'form-control text-center',
                    'placeholder': 'Ingrese un Codigo',
                    'autocomplete': 'off'
                }
            ),
            'tip_cuenta': Select(
                choices=OPCIONES_ENCABEZADO_PLAN,
                attrs={
                    'class': 'form-control select2',
                    'style': 'width: 100%;'
                }
            ),
            'tip_transa': Select(choices=OPCIONES_TRANSACCION_PLAN,
                                 attrs={
                                     'class': 'form-control select2',
                                     'style': 'width: 100%;'
                                 }
                                 ),
            'fecha': TextInput(
                attrs={
                    'class': 'form-control',
                    'autocomplete': 'off'
                }
            ),
            'descripcion': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese una Descripcion',
                    'autocomplete': 'off'
                }
            ),
            'comprobante': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese un Comprobante',
                    'autocomplete': 'off'
                }
            ),
            'ruc': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese un numero de RUC',
                    'autocomplete': 'off'
                }
            ),
            'proveedor': Select(
                attrs={
                    'class': 'form-control select2',
                    'autocomplete': 'off',
                    'style': 'width: 100%;'
                }
            ),
            'reg_ats': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese un numero de Registro de ATS',
                    'autocomplete': 'off'
                }
            ),
            'reg_control': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese un numero de Regitro de Control',
                    'autocomplete': 'off'
                }
            ),
            'direccion': Textarea(
                attrs={
                    'class': 'form-control',
                    'autocomplete': 'off',
                    'placeholder': 'Ingrese una Direccion',
                    'rows': "3",
                    'cols': "50"
                }
            ),
        }


class DetalleCuentasPlanCuentaForm(ModelForm):
    empresa = forms.ModelChoiceField(
        queryset=None,
        required=False,
        widget=Select(attrs={
            'class': 'form-control select2',
            'placeholder': 'Selecciona una Empresa',
            'autocomplete': 'off'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from app_empresa.app_reg_empresa.models import Empresa
        self.fields['empresa'].queryset = Empresa.objects.all()

    class Meta:
        model = DetalleCuentasPlanCuenta
        exclude = ['empresa']
        widgets = {
            'codigo': NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese un Codigo',
                    'autocomplete': 'off'
                }
            ),
            'nombre': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Nombre de la Cuenta',
                    'autocomplete': 'off'
                }
            ),
            'periodo': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese un Periodo',
                    'autocomplete': 'off'
                }
            ),
            'tipo_comp': Select(choices=OPCIONES_CUENTA,
                                attrs={
                                    'class': 'form-control select2'
                                }
                                ),
            'nivel': Select(choices=OPCIONES_NIVEL,
                            attrs={
                                'class': 'form-control select2'
                            }
                            ),
            'cuentasuma': Select(
                attrs={
                    'class': 'form-control select2',
                }
            ),
        }


class ReportForm(Form):
    rango_dias = CharField(widget=TextInput(attrs={
        'class': 'form-control',
        'autocomplete': 'off',
        'id': 'rango_dias'
    }))


class ReciboForm(ModelForm):
    empresa = forms.ModelChoiceField(
        queryset=None,
        required=False,
        widget=Select(attrs={
            'class': 'form-control select2',
            'style': 'width: 100%;',
            'name': 'empresa_id'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['voucher_type'].widget.attrs['autofocus'] = True
        from app_empresa.app_reg_empresa.models import Empresa
        self.fields['empresa'].queryset = Empresa.objects.all()

    class Meta:
        model = Recibo
        exclude = ['empresa']
        widgets = {
            'voucher_type': Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'establishment_code': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese un numero'}),
            'issuing_point_code': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese un numero'}),
            'sequence': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese un numero de secuencia'}),
        }

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                super().save()
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class AnextoTransaccionalForm(ModelForm):
    company = forms.ModelChoiceField(
        queryset=None,
        required=False,
        widget=Select(attrs={
            'class': 'form-control select2', 'style': 'width: 100%;'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from app_empresa.app_reg_empresa.models import Empresa
        self.fields['company'].queryset = Empresa.objects.all()
        self.fields['receipt'].queryset = Recibo.objects.filter(
            voucher_type__in=[VOUCHER_TYPE[0][0], VOUCHER_TYPE[-1][0]], empresa_id=self.instance.company_id
        )

    class Meta:
        model = AnexoTransaccional
        exclude = ['company']
        widgets = {
            'estab': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese una Descripcion',
                    'autocomplete': 'off'
                }
            ),
            'tip_cuenta': Select(choices=OPCIONES_ENCABEZADO_PLAN,
                                 attrs={
                                     'class': 'form-control select2'
                                 }
                                 ),
            'receipt': Select(
                attrs={
                    'class': 'form-control select2', 'style': 'width: 100%;'
                }
            ),
            'comp_numero': TextInput(
                attrs={
                    'class': 'form-control', 'readonly': True
                }
            ),
            'tipo_comp': Select(choices=OPCIONES_TIPO_COMPROBANTE,
                                attrs={
                                    'class': 'form-control select2'
                                }
                                ),
            'fecha': TextInput(
                attrs={
                    'class': 'form-control',
                    'autocomplete': 'off'
                }
            ),
            'comp_fecha_reg': TextInput(
                attrs={
                    'class': 'form-control',
                    'autocomplete': 'off'
                }
            ),
            'comp_fecha_em': TextInput(
                attrs={
                    'class': 'form-control',
                    'autocomplete': 'off'
                }
            ),
            'ret_fecha': TextInput(
                attrs={
                    'class': 'form-control',
                    'autocomplete': 'off'
                }
            ),
            'descripcion': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese una Descripcion',
                    'autocomplete': 'off'
                }
            ),
            'comprobante': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese un Comprobante',
                    'autocomplete': 'off'
                }
            ),
            'direccion': Textarea(
                attrs={
                    'class': 'form-control',
                    'autocomplete': 'off',
                    'placeholder': 'Ingrese una Observacion',
                    'rows': "3",
                    'cols': "50"
                }
            ),
            'base_cero_bruto_fcientocuatro': Select(choices=OPCIONES_FORM_CIENTOCUATRO_BASE_CERO,
                                                    attrs={
                                                        'class': 'form-control select2'
                                                    }
                                                    ),
            'base_iva_normal_bruto_fcientocuatro': Select(choices=OPCIONES_FORM_CIENTOCUATRO_BASE_IVA_NORMAL,
                                                          attrs={
                                                              'class': 'form-control select2'
                                                          }
                                                          ),
            'base_iva_normal_porcen': Select(choices=OPCIONES_IVA_NORMAL_PORCEN,
                                             attrs={
                                                 'class': 'form-control select2'
                                             }
                                             ),
            'base_iva_bienes_bruto_fcientocuatro': Select(choices=OPCIONES_FORM_CIENTOCUATRO_BASE_IVA_BIENES,
                                                          attrs={
                                                              'class': 'form-control select2'
                                                          }
                                                          ),
            'base_iva_bienes_porcen': Select(choices=OPCIONES_IVA_BIENES_PORCEN,
                                             attrs={
                                                 'class': 'form-control select2'
                                             }
                                             ),
            'porcent_ice': Select(choices=OPCIONES_ICE_PORCEN,
                                  attrs={
                                      'class': 'form-control select2'
                                  }
                                  ),
            'ret_iva_cero': Select(choices=OPCIONES_RET_IVA_CERO,
                                   attrs={
                                       'class': 'form-control select2'
                                   }
                                   ),
            'ret_iva_diez': Select(choices=OPCIONES_RET_IVA_DIEZ,
                                   attrs={
                                       'class': 'form-control select2'
                                   }
                                   ),
            'ret_iva_veint': Select(choices=OPCIONES_RET_IVA_VEINT,
                                    attrs={
                                        'class': 'form-control select2'
                                    }
                                    ),
            'ret_iva_treint': Select(choices=OPCIONES_RET_IVA_TREINT,
                                     attrs={
                                         'class': 'form-control select2'
                                     }
                                     ),
            'ret_iva_cinc': Select(choices=OPCIONES_RET_IVA_CINC,
                                   attrs={
                                       'class': 'form-control select2'
                                   }
                                   ),
            'ret_iva_setn': Select(choices=OPCIONES_RET_IVA_SETEN,
                                   attrs={
                                       'class': 'form-control select2'
                                   }
                                   ),
            'ret_iva_cien': Select(choices=OPCIONES_RET_IVA_CIEN,
                                   attrs={
                                       'class': 'form-control select2'
                                   }
                                   ),
            'ret_fue_iva_anexo_uno': Select(choices=OPCIONES_RET_FUEN_ANEXO_UNO,
                                            attrs={
                                                'class': 'form-control select2'
                                            }
                                            ),
            'ret_fue_iva_anexo_dos': Select(choices=OPCIONES_RET_FUEN_ANEXO_DOS,
                                            attrs={
                                                'class': 'form-control select2'
                                            }
                                            ),
            'ret_fue_iva_anexo_tres': Select(choices=OPCIONES_RET_FUEN_ANEXO_TRES,
                                             attrs={
                                                 'class': 'form-control select2'
                                             }
                                             ),
            'tip_form': Select(choices=OPCIONES_F_PAGO,
                               attrs={
                                   'class': 'form-control select2'
                               }
                               ),
            'det_form': Select(choices=OPCIONES_T_F_PAGO,
                               attrs={
                                   'class': 'form-control select2'
                               }
                               ),
        }


class ATSGenerarXMLForm(Form):
    id_receptor = CharField(
        max_length=13,
        widget=TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese ID Receptor'
        }),
        label="ID Receptor"
    )
    nombre = CharField(
        max_length=200,
        widget=TextInput(attrs={
            'class': 'form-control',
            'readonly': True
        }),
        label="Nombre"
    )
    periodicidad = ChoiceField(
        choices=[('mensual', 'Mensual'), ('semestral', 'Semestral')],
        widget=RadioSelect(attrs={'class': 'form-check-input'}),
        initial='mensual',
        label="Periodicidad"
    )
    periodo = ChoiceField(
        choices=[
            ('Enero', 'Enero'), ('Febrero', 'Febrero'), ('Marzo', 'Marzo'),
            ('Abril', 'Abril'), ('Mayo', 'Mayo'), ('Junio', 'Junio'),
            ('Julio', 'Julio'), ('Agosto', 'Agosto'), ('Septiembre', 'Septiembre'),
            ('Octubre', 'Octubre'), ('Noviembre', 'Noviembre'), ('Diciembre', 'Diciembre')
        ],
        widget=Select(attrs={'class': 'form-control'}),
        initial='Agosto',
        label="Periodo"
    )
    anio = IntegerField(
        widget=NumberInput(attrs={
            'class': 'form-control',
            'min': 2000,
            'max': 2050
        }),
        initial=datetime.now().year,
        label="Ano"
    )
    destino = CharField(
        widget=TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ruta de destino del archivo'
        }),
        required=False,
        label="Destino"
    )
    eliminar_caracteres = BooleanField(
        widget=CheckboxInput(attrs={'class': 'form-check-input'}),
        required=False,
        initial=False,
        label="Eliminar caracteres de separacion de linea y tabulacion"
    )


class ATSImportarComprasForm(Form):
    periodicidad = ChoiceField(
        choices=[('mensual', 'Mensual'), ('semestral', 'Semestral')],
        widget=RadioSelect(attrs={'class': 'form-check-input'}),
        initial='mensual',
        label="Periodicidad"
    )
    periodo = ChoiceField(
        choices=[
            ('Enero', 'Enero'), ('Febrero', 'Febrero'), ('Marzo', 'Marzo'),
            ('Abril', 'Abril'), ('Mayo', 'Mayo'), ('Junio', 'Junio'),
            ('Julio', 'Julio'), ('Agosto', 'Agosto'), ('Septiembre', 'Septiembre'),
            ('Octubre', 'Octubre'), ('Noviembre', 'Noviembre'), ('Diciembre', 'Diciembre')
        ],
        widget=Select(attrs={'class': 'form-control'}),
        initial='Agosto',
        label="Periodo"
    )
    anio = IntegerField(
        widget=NumberInput(attrs={
            'class': 'form-control',
            'min': 2000,
            'max': 2050
        }),
        initial=datetime.now().year,
        label="Ano"
    )
    ruta = CharField(
        widget=TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ruta del archivo XLS'
        }),
        label="Ruta"
    )
    modo_insercion = ChoiceField(
        choices=[
            ('agregar', 'Agregar datos a periodo'),
            ('reemplazar', 'Reemplazar periodo de contribuyente')
        ],
        widget=RadioSelect(attrs={'class': 'form-check-input'}),
        initial='agregar',
        label="Modo de insercion de datos"
    )


class ATSImportarVentasForm(Form):
    periodicidad = ChoiceField(
        choices=[('mensual', 'Mensual'), ('semestral', 'Semestral')],
        widget=RadioSelect(attrs={'class': 'form-check-input'}),
        initial='mensual',
        label="Periodicidad"
    )
    periodo = ChoiceField(
        choices=[
            ('Enero', 'Enero'), ('Febrero', 'Febrero'), ('Marzo', 'Marzo'),
            ('Abril', 'Abril'), ('Mayo', 'Mayo'), ('Junio', 'Junio'),
            ('Julio', 'Julio'), ('Agosto', 'Agosto'), ('Septiembre', 'Septiembre'),
            ('Octubre', 'Octubre'), ('Noviembre', 'Noviembre'), ('Diciembre', 'Diciembre')
        ],
        widget=Select(attrs={'class': 'form-control'}),
        initial='Agosto',
        label="Periodo"
    )
    anio = IntegerField(
        widget=NumberInput(attrs={
            'class': 'form-control',
            'min': 2000,
            'max': 2050
        }),
        initial=datetime.now().year,
        label="Ano"
    )
    ruta = CharField(
        widget=TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ruta del archivo XLS'
        }),
        label="Ruta"
    )


class ATSImportarXMLForm(Form):
    archivo_xml = FileField(
        widget=FileInput(attrs={
            'class': 'form-control-file',
            'accept': '.xml'
        }),
        label="Ubicacion de archivo XML"
    )
    modo_insercion = ChoiceField(
        choices=[
            ('agregar', 'Agregar datos a periodo'),
            ('reemplazar', 'Reemplazar periodo de contribuyente')
        ],
        widget=RadioSelect(attrs={'class': 'form-check-input'}),
        initial='agregar',
        label="Modo de insercion de datos"
    )


class ATSRevisionDatosForm(forms.Form):
    id_receptor = CharField(
        max_length=13,
        widget=Select(attrs={'class': 'form-control'}),
        label="ID Receptor"
    )
    periodicidad = ChoiceField(
        choices=[('mensual', 'Mensual'), ('semestral', 'Semestral')],
        widget=RadioSelect(attrs={'class': 'form-check-input'}),
        initial='mensual',
        label="Periodicidad"
    )
    periodo = ChoiceField(
        choices=[
            ('Enero', 'Enero'), ('Febrero', 'Febrero'), ('Marzo', 'Marzo'),
            ('Abril', 'Abril'), ('Mayo', 'Mayo'), ('Junio', 'Junio'),
            ('Julio', 'Julio'), ('Agosto', 'Agosto'), ('Septiembre', 'Septiembre'),
            ('Octubre', 'Octubre'), ('Noviembre', 'Noviembre'), ('Diciembre', 'Diciembre')
        ],
        widget=Select(attrs={'class': 'form-control'}),
        initial='Agosto',
        label="Periodo"
    )
    anio = IntegerField(
        widget=NumberInput(attrs={
            'class': 'form-control',
            'min': 2000,
            'max': 2050
        }),
        initial=datetime.now().year,
        label="Ano"
    )
    tipo_transaccion = ChoiceField(
        choices=[
            ('compras', 'Compras'),
            ('ventas', 'Ventas'),
            ('anulados', 'Anulados')
        ],
        widget=RadioSelect(attrs={'class': 'form-check-input'}),
        initial='compras',
        label="Tipo de transaccion"
    )


class ATSCarpetaXMLForm(Form):
    ubicacion_origen = CharField(
        widget=TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ubicacion origen de archivos XML'
        }),
        label="Ubicacion Origen de archivos XML"
    )
    mostrar_pendientes = BooleanField(
        widget=CheckboxInput(attrs={'class': 'form-check-input'}),
        required=False,
        label="Mostrar solo pendientes"
    )
    archivo_bd = BooleanField(
        widget=CheckboxInput(attrs={'class': 'form-check-input'}),
        required=False,
        label="Archivo que no consta en BD"
    )
    archivo_consta_bd = BooleanField(
        widget=CheckboxInput(attrs={'class': 'form-check-input'}),
        required=False,
        label="Archivo ya consta en BD"
    )
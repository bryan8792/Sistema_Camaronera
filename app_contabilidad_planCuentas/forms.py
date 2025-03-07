from django.forms import *
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
    class Meta:
        model = PlanCuenta
        fields = '__all__'
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
            'empresa': Select(
                attrs={
                    'class': 'form-control select2',
                    'placeholder': 'Selecciona una Empresa',
                    'autocomplete': 'off'
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
                    # 'multiple': 'multiple'
                }
            ),

        }



class EncabezadoCuentasPlanCuentaForm(ModelForm):
    class Meta:
        model = EncabezadoCuentasPlanCuenta
        fields = '__all__'
        widgets = {
            'codigo': NumberInput(
                attrs={
                    'class': 'form-control text-center',
                    'placeholder': 'Ingrese un Codigo',
                    'autocomplete': 'off'
                }
            ),
            'tip_cuenta': Select(choices=OPCIONES_ENCABEZADO_PLAN,
                attrs={
                    'class': 'form-control select2'
                }
            ),
            'tip_transa': Select(choices=OPCIONES_TRANSACCION_PLAN,
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
            'descripcion': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese una Descripción',
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
            'empresa': Select(
                attrs={
                    'class': 'form-control select2',
                    'autocomplete': 'off'
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
                    'placeholder': 'Ingrese una Dirección',
                    'rows': "3",
                    'cols': "50"
                }
            ),

        }



class DetalleCuentasPlanCuentaForm(ModelForm):
    class Meta:
        model = DetalleCuentasPlanCuenta
        fields = '__all__'
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
            'empresa': Select(
                attrs={
                    'class': 'form-control select2',
                    'placeholder': 'Selecciona una Empresa',
                    'autocomplete': 'off'
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
                    # 'multiple': 'multiple'
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['voucher_type'].widget.attrs['autofocus'] = True

    class Meta:
        model = Recibo
        fields = '__all__'
        widgets = {
            'voucher_type': Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'empresa': Select(attrs={
                'class': 'form-control select2',
                'style': 'width: 100%;',
                'name': 'empresa_id'
            }),
            'establishment_code': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese un número'}),
            'issuing_point_code': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese un número'}),
            'sequence': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese un número de secuencia'}),
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['receipt'].queryset = Recibo.objects.filter(
            voucher_type__in=[VOUCHER_TYPE[0][0], VOUCHER_TYPE[-1][0]], empresa_id=self.instance.company_id
        )
        #self.fields['receipt'].choices = tuple((code, label) for code, label in VOUCHER_TYPE if code != VOUCHER_TYPE[-1][0])

    class Meta:
        model = AnexoTransaccional
        fields = '__all__'
        widgets = {
            'estab': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese una Descripción',
                    'autocomplete': 'off'
                }
            ),
            'tip_cuenta': Select(choices=OPCIONES_ENCABEZADO_PLAN,
                attrs={
                    'class': 'form-control select2'
                }
            ),
            'company': Select(
                attrs={
                    'class': 'form-control select2', 'style': 'width: 100%;'
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
                    'placeholder': 'Ingrese una Descripción',
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
                    'placeholder': 'Ingrese una Observación',
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
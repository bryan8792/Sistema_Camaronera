from datetime import datetime
import base64
import math
import tempfile
import time
import unicodedata
from datetime import datetime
from io import BytesIO
from xml.etree import ElementTree
import barcode
from barcode import writer
from django.contrib.contenttypes.models import ContentType
from django.core.files import File
from django.core.files.base import ContentFile
from django.db import models
from django.db.models import FloatField
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.forms import model_to_dict
from django.db import models
from Sistema_Camaronera import settings
from app_contabilidad_planCuentas.models import Recibo
from app_empresa.app_reg_empresa.models import Empresa
from app_inventario.app_categoria.models import Producto
from app_venta.models import Sale, SaleDetail
from utilities import printer
from utilities.sri import SRI
from utilities.choices import *


# Create your models here.
class CreditNote(models.Model):
    company = models.ForeignKey(Empresa, on_delete=models.PROTECT, verbose_name='Compañia')
    sale = models.ForeignKey(Sale, on_delete=models.PROTECT, verbose_name='Venta')
    date_joined = models.DateField(default=datetime.now, verbose_name='Fecha de registro')
    motive = models.CharField(max_length=300, null=True, blank=True, verbose_name='Motivo')
    receipt = models.ForeignKey(Recibo, on_delete=models.PROTECT, verbose_name='Tipo de comprobante')
    voucher_number = models.CharField(max_length=9, verbose_name='Número de comprobante')
    voucher_number_full = models.CharField(max_length=20, verbose_name='Número de comprobante completo')
    subtotal_12 = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Subtotal')
    subtotal_0 = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Subtotal 0%')
    total_dscto = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Valor del descuento')
    iva = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Iva')
    total_iva = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Valor de iva')
    total = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Total a pagar')
    environment_type = models.PositiveIntegerField(choices=ENVIRONMENT_TYPE, default=ENVIRONMENT_TYPE[0][0])
    access_code = models.CharField(max_length=49, null=True, blank=True, verbose_name='Clave de acceso')
    authorization_date = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de autorización')
    xml_authorized = models.FileField(null=True, blank=True, verbose_name='XML Autorizado')
    pdf_authorized = models.FileField(upload_to='pdf_authorized/%Y/%m/%d', null=True, blank=True, verbose_name='PDF Autorizado')
    create_electronic_invoice = models.BooleanField(default=True, verbose_name='Crear factura electrónica')
    status = models.CharField(max_length=50, choices=INVOICE_STATUS, default=INVOICE_STATUS[0][0], verbose_name='Estado')

    def __str__(self):
        return self.motive

    def get_iva_percent(self):
        return int(self.iva * 100)

    def get_full_subtotal(self):
        return float(self.subtotal_0) + float(self.subtotal_12)

    def get_subtotal_without_taxes(self):
        return float(self.creditnotedetail_set.filter().aggregate(result=Coalesce(Sum('subtotal'), 0.00, output_field=FloatField()))['result'])

    def get_authorization_date(self):
        return self.authorization_date.strftime('%Y-%m-%d %H:%M:%S')

    def get_date_joined(self):
        return (datetime.strptime(self.date_joined, '%Y-%m-%d') if isinstance(self.date_joined, str) else self.date_joined).strftime('%Y-%m-%d')

    def get_xml_authorized(self):
        if self.xml_authorized:
            return f'{settings.MEDIA_URL}{self.xml_authorized}'
        return None

    def get_pdf_authorized(self):
        if self.pdf_authorized:
            return f'{settings.MEDIA_URL}{self.pdf_authorized}'
        return None

    def get_voucher_number_full(self):
        return f'{self.receipt.establishment_code}-{self.receipt.issuing_point_code}-{self.voucher_number}'

    def generate_voucher_number(self):
        number = int(self.receipt.get_sequence()) + 1
        return f'{number:09d}'

    def generate_voucher_number_full(self):
        self.company = Empresa.objects.first()
        self.receipt = Recibo.objects.get(voucher_type=VOUCHER_TYPE[1][0], establishment_code=self.company.establishment_code, issuing_point_code=self.company.issuing_point_code)
        self.voucher_number = self.generate_voucher_number()
        return self.get_voucher_number_full()

    def generate_pdf_authorized(self):
        rv = BytesIO()
        barcode.Code128(self.access_code, writer=barcode.writer.ImageWriter()).write(rv, options={'text_distance': 3.0, 'font_size': 6})
        file = base64.b64encode(rv.getvalue()).decode("ascii")
        context = {'credit_note': self, 'access_code_barcode': f"data:image/png;base64,{file}"}
        pdf_file = printer.create_pdf(context=context, template_name='credit_note/format/invoice.html')
        with tempfile.NamedTemporaryFile(delete=True) as file_temp:
            file_temp.write(pdf_file)
            file_temp.flush()
            self.pdf_authorized.save(name=f'{self.receipt.get_name_xml()}_{self.access_code}.pdf', content=File(file_temp))

    def generate_xml(self):
        access_key = SRI().create_access_key(self)
        root = ElementTree.Element('notaCredito', id="comprobante", version="1.1.0")
        # infoTributaria
        xml_tax_info = ElementTree.SubElement(root, 'infoTributaria')
        ElementTree.SubElement(xml_tax_info, 'ambiente').text = str(self.company.environment_type)
        ElementTree.SubElement(xml_tax_info, 'tipoEmision').text = str(self.company.emission_type)
        ElementTree.SubElement(xml_tax_info, 'razonSocial').text = self.company.business_name
        ElementTree.SubElement(xml_tax_info, 'nombreComercial').text = self.company.tradename
        ElementTree.SubElement(xml_tax_info, 'ruc').text = self.company.ruc
        ElementTree.SubElement(xml_tax_info, 'claveAcceso').text = access_key
        ElementTree.SubElement(xml_tax_info, 'codDoc').text = self.receipt.voucher_type
        ElementTree.SubElement(xml_tax_info, 'estab').text = self.receipt.establishment_code
        ElementTree.SubElement(xml_tax_info, 'ptoEmi').text = self.receipt.issuing_point_code
        ElementTree.SubElement(xml_tax_info, 'secuencial').text = self.voucher_number
        ElementTree.SubElement(xml_tax_info, 'dirMatriz').text = self.company.main_address
        if self.company.retention_agent == RETENTION_AGENT[0][0]:
            ElementTree.SubElement(xml_tax_info, 'agenteRetencion').text = '1'
        # infoNotaCredito
        xml_info_invoice = ElementTree.SubElement(root, 'infoNotaCredito')
        ElementTree.SubElement(xml_info_invoice, 'fechaEmision').text = datetime.now().strftime('%d/%m/%Y')
        ElementTree.SubElement(xml_info_invoice, 'dirEstablecimiento').text = self.company.establishment_address
        ElementTree.SubElement(xml_info_invoice, 'tipoIdentificacionComprador').text = self.sale.client.identification_type
        ElementTree.SubElement(xml_info_invoice, 'razonSocialComprador').text = self.sale.client.user.names
        ElementTree.SubElement(xml_info_invoice, 'identificacionComprador').text = self.sale.client.dni
        if not self.company.special_taxpayer == '000':
            ElementTree.SubElement(xml_info_invoice, 'contribuyenteEspecial').text = self.company.special_taxpayer
        ElementTree.SubElement(xml_info_invoice, 'obligadoContabilidad').text = self.company.obligated_accounting
        ElementTree.SubElement(xml_info_invoice, 'rise').text = 'Contribuyente Régimen Simplificado RISE'
        ElementTree.SubElement(xml_info_invoice, 'codDocModificado').text = self.sale.receipt.voucher_type
        ElementTree.SubElement(xml_info_invoice, 'numDocModificado').text = self.sale.voucher_number_full
        ElementTree.SubElement(xml_info_invoice, 'fechaEmisionDocSustento').text = self.sale.date_joined.strftime('%d/%m/%Y')
        ElementTree.SubElement(xml_info_invoice, 'totalSinImpuestos').text = f'{self.get_full_subtotal():.2f}'
        ElementTree.SubElement(xml_info_invoice, 'valorModificacion').text = f'{self.total:.2f}'
        ElementTree.SubElement(xml_info_invoice, 'moneda').text = 'DOLAR'
        # totalConImpuestos
        xml_total_with_taxes = ElementTree.SubElement(xml_info_invoice, 'totalConImpuestos')
        # totalImpuesto
        if self.subtotal_0 != 0.0000:
            xml_total_tax = ElementTree.SubElement(xml_total_with_taxes, 'totalImpuesto')
            ElementTree.SubElement(xml_total_tax, 'codigo').text = str(TAX_CODES[0][0])
            ElementTree.SubElement(xml_total_tax, 'codigoPorcentaje').text = '0'
            ElementTree.SubElement(xml_total_tax, 'baseImponible').text = f'{self.subtotal_0:.2f}'
            ElementTree.SubElement(xml_total_tax, 'valor').text = f'{0:.2f}'
        if self.subtotal_12 != 0.0000:
            xml_total_tax2 = ElementTree.SubElement(xml_total_with_taxes, 'totalImpuesto')
            ElementTree.SubElement(xml_total_tax2, 'codigo').text = str(TAX_CODES[0][0])
            ElementTree.SubElement(xml_total_tax2, 'codigoPorcentaje').text = str(self.company.vat_percentage)
            ElementTree.SubElement(xml_total_tax2, 'baseImponible').text = f'{self.subtotal_12:.2f}'
            ElementTree.SubElement(xml_total_tax2, 'valor').text = f'{self.total_iva:.2f}'
        ElementTree.SubElement(xml_info_invoice, 'motivo').text = self.motive
        # detalles
        xml_details = ElementTree.SubElement(root, 'detalles')
        for detail in self.creditnotedetail_set.all():
            xml_detail = ElementTree.SubElement(xml_details, 'detalle')
            ElementTree.SubElement(xml_detail, 'codigoInterno').text = detail.product.code
            ElementTree.SubElement(xml_detail, 'descripcion').text = detail.product.name
            ElementTree.SubElement(xml_detail, 'cantidad').text = f'{detail.cant:.2f}'
            ElementTree.SubElement(xml_detail, 'precioUnitario').text = f'{detail.price:.2f}'
            ElementTree.SubElement(xml_detail, 'descuento').text = f'{detail.total_dscto:.2f}'
            ElementTree.SubElement(xml_detail, 'precioTotalSinImpuesto').text = f'{detail.total:.2f}'
            xml_taxes = ElementTree.SubElement(xml_detail, 'impuestos')
            xml_tax = ElementTree.SubElement(xml_taxes, 'impuesto')
            ElementTree.SubElement(xml_tax, 'codigo').text = str(TAX_CODES[0][0])
            if detail.product.with_tax:
                ElementTree.SubElement(xml_tax, 'codigoPorcentaje').text = str(self.company.vat_percentage)
                ElementTree.SubElement(xml_tax, 'tarifa').text = f'{detail.iva * 100:.2f}'
                ElementTree.SubElement(xml_tax, 'baseImponible').text = f'{detail.total:.2f}'
                ElementTree.SubElement(xml_tax, 'valor').text = f'{detail.total_iva:.2f}'
            else:
                ElementTree.SubElement(xml_tax, 'codigoPorcentaje').text = "0"
                ElementTree.SubElement(xml_tax, 'tarifa').text = "0"
                ElementTree.SubElement(xml_tax, 'baseImponible').text = f'{detail.total:.2f}'
                ElementTree.SubElement(xml_tax, 'valor').text = "0"
        # infoAdicional
        xml_additional_info = ElementTree.SubElement(root, 'infoAdicional')
        ElementTree.SubElement(xml_additional_info, 'campoAdicional', nombre='dirCliente').text = self.sale.client.address
        ElementTree.SubElement(xml_additional_info, 'campoAdicional', nombre='telfCliente').text = self.sale.client.mobile
        ElementTree.SubElement(xml_additional_info, 'campoAdicional', nombre='Observacion').text = f'NOTA_CREDITO # {self.voucher_number}'
        return ElementTree.tostring(root, xml_declaration=True, encoding='UTF-8').decode('UTF-8').replace("'", '"'), access_key

    def toJSON(self):
        item = model_to_dict(self)
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        item['sale'] = self.sale.toJSON()
        item['company'] = self.company.toJSON()
        item['receipt'] = self.receipt.toJSON()
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        item['subtotal_12'] = float(self.subtotal_12)
        item['subtotal_0'] = float(self.subtotal_0)
        item['subtotal'] = self.get_full_subtotal()
        item['total_dscto'] = float(self.total_dscto)
        item['iva'] = float(self.iva)
        item['total_iva'] = float(self.total_iva)
        item['total'] = float(self.total)
        item['environment_type'] = {'id': self.environment_type, 'name': self.get_environment_type_display()}
        item['invoice'] = self.get_voucher_number_full()
        item['authorization_date'] = '' if self.authorization_date is None else self.authorization_date.strftime('%Y-%m-%d')
        item['xml_authorized'] = self.get_xml_authorized()
        item['pdf_authorized'] = self.get_pdf_authorized()
        item['status'] = {'id': self.status, 'name': self.get_status_display()}
        return item

    def generate_electronic_invoice(self):
        sri = SRI()
        result = sri.create_xml(self)
        if result['resp']:
            result = sri.firm_xml(instance=self, xml=result['xml'])
            if result['resp']:
                result = sri.validate_xml(instance=self, xml=result['xml'])
                if result['resp']:
                    return sri.authorize_xml(instance=self)
        return result

    def calculate_detail(self):
        for detail in self.creditnotedetail_set.filter():
            detail.price = float(detail.price)
            detail.iva = float(self.iva)
            detail.price_with_vat = detail.price + (detail.price * detail.iva)
            detail.subtotal = detail.price * detail.cant
            detail.total_dscto = detail.subtotal * float(detail.dscto)
            detail.total_iva = (detail.subtotal - detail.total_dscto) * detail.iva
            detail.total = detail.subtotal - detail.total_dscto
            detail.save()

    def calculate_invoice(self):
        self.subtotal_0 = float(self.creditnotedetail_set.filter(product__with_tax=False).aggregate(result=Coalesce(Sum('total'), 0.00, output_field=FloatField()))['result'])
        self.subtotal_12 = float(self.creditnotedetail_set.filter(product__with_tax=True).aggregate(result=Coalesce(Sum('total'), 0.00, output_field=FloatField()))['result'])
        self.total_iva = float(self.creditnotedetail_set.filter(product__with_tax=True).aggregate(result=Coalesce(Sum('total_iva'), 0.00, output_field=FloatField()))['result'])
        self.total_dscto = float(self.creditnotedetail_set.filter().aggregate(result=Coalesce(Sum('total_dscto'), 0.00, output_field=FloatField()))['result'])
        self.total = float(self.get_full_subtotal()) + float(self.total_iva)
        self.save()

    def edit(self):
        super(CreditNote, self).save()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.motive is None:
            self.motive = 'Sin detalles'
        if self.pk is None:
            self.receipt.sequence = int(self.voucher_number)
            self.receipt.save()
        super(CreditNote, self).save()

    def delete(self, using=None, keep_parents=False):
        try:
            for i in self.creditnotedetail_set.filter(product__inventoried=True):
                i.product.stock += i.cant
                i.product.save()
                i.delete()
        except:
            pass
        super(CreditNote, self).delete()

    class Meta:
        db_table = 'tb_notCredito'
        verbose_name = 'Nota de Credito'
        verbose_name_plural = 'Notas de Credito'
        ordering = ['id']


class CreditNoteDetail(models.Model):
    credit_note = models.ForeignKey(CreditNote, on_delete=models.CASCADE)
    sale_detail = models.ForeignKey(SaleDetail, on_delete=models.PROTECT)
    product = models.ForeignKey(Producto, blank=True, null=True, on_delete=models.PROTECT)
    date_joined = models.DateField(default=datetime.now)
    cant = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    price_with_vat = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    subtotal = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    iva = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    total_iva = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    dscto = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    total_dscto = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)

    def __str__(self):
        return self.product.nombre

    def toJSON(self):
        item = model_to_dict(self)
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        item['sale_detail'] = self.sale_detail.toJSON()
        item['product'] = self.product.toJSON()
        item['price'] = float(self.price)
        item['price_with_vat'] = float(self.price_with_vat)
        item['subtotal'] = float(self.subtotal)
        item['iva'] = float(self.subtotal)
        item['total_iva'] = float(self.subtotal)
        item['dscto'] = float(self.dscto)
        item['total_dscto'] = float(self.total_dscto)
        item['total'] = float(self.total)
        return item

    class Meta:
        db_table = 'tb_notCreditodetalle'
        verbose_name = 'Detalle Devolución Ventas'
        verbose_name_plural = 'Detalle Devoluciones Ventas'
        ordering = ['id']
from django.db import models
from xml.etree import ElementTree
from app_compra.models import Purchase
from app_empresa.app_reg_empresa.models import *
import barcode
from barcode import writer
from app_cliente.models import *
from app_contabilidad_planCuentas.models import *
from app_inventario.app_categoria.models import Producto
from app_user.models import *


# Create your models here.
class Sale(models.Model):
    company = models.ForeignKey(Empresa, on_delete=models.PROTECT, verbose_name='Compañia')
    client = models.ForeignKey(Client, on_delete=models.PROTECT, verbose_name='Cliente')
    receipt = models.ForeignKey(Recibo, on_delete=models.PROTECT, limit_choices_to={'voucher_type__in': [VOUCHER_TYPE[0][0], VOUCHER_TYPE[-1][0]]}, verbose_name='Tipo de comprobante')
    voucher_number = models.CharField(max_length=9, verbose_name='Número de comprobante')
    voucher_number_full = models.CharField(max_length=20, verbose_name='Número de comprobante completo')
    employee = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Empleado')
    payment_type = models.CharField(choices=PAYMENT_TYPE, max_length=50, default=PAYMENT_TYPE[0][0], verbose_name='Tipo de pago')
    payment_method = models.CharField(choices=PAYMENT_METHOD, max_length=50, default=PAYMENT_METHOD[5][0], verbose_name='Método de pago')
    time_limit = models.IntegerField(default=31, verbose_name='Plazo')
    creation_date = models.DateTimeField(default=datetime.now, verbose_name='Fecha y hora de registro')
    date_joined = models.DateField(default=datetime.now, verbose_name='Fecha de registro')
    end_credit = models.DateField(default=datetime.now, verbose_name='Fecha limite de credito')
    additional_info = models.JSONField(default=dict, verbose_name='Información adicional')
    subtotal_12 = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Subtotal')
    subtotal_0 = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Subtotal 0%')
    total_dscto = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Valor del descuento')
    iva = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Iva')
    total_iva = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Valor de iva')
    total = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Total a pagar')
    cash = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Efectivo recibido')
    change = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Cambio')
    environment_type = models.PositiveIntegerField(choices=ENVIRONMENT_TYPE, default=ENVIRONMENT_TYPE[0][0])
    access_code = models.CharField(max_length=49, null=True, blank=True, verbose_name='Clave de acceso')
    authorization_date = models.DateField(null=True, blank=True, verbose_name='Fecha de emisión')
    xml_authorized = models.FileField(null=True, blank=True, verbose_name='XML Autorizado')
    pdf_authorized = models.FileField(upload_to='pdf_authorized/%Y/%m/%d', null=True, blank=True, verbose_name='PDF Autorizado')
    create_electronic_invoice = models.BooleanField(default=True, verbose_name='Crear factura electrónica')
    status = models.CharField(max_length=50, choices=INVOICE_STATUS, default=INVOICE_STATUS[0][0], verbose_name='Estado')

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return f'{self.voucher_number_full} / {self.client.get_full_name()})'

    def get_iva_percent(self):
        return int(self.iva * 100)

    def get_full_subtotal(self):
        return float(self.subtotal_0) + float(self.subtotal_12)

    def get_subtotal_without_taxes(self):
        return float(self.saledetail_set.filter().aggregate(result=Coalesce(Sum('subtotal'), 0.00, output_field=FloatField()))['result'])

    def get_authorization_date(self):
        return self.authorization_date.strftime('%Y-%m-%d %H:%M:%S')

    def get_date_joined(self):
        return (datetime.strptime(self.date_joined, '%Y-%m-%d') if isinstance(self.date_joined, str) else self.date_joined).strftime('%Y-%m-%d')

    def get_end_credit(self):
        return (datetime.strptime(self.end_credit, '%Y-%m-%d') if isinstance(self.end_credit, str) else self.end_credit).strftime('%Y-%m-%d')

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

    def generate_voucher_number(self, increase=True):
        if isinstance(self.receipt.sequence, str):
            self.receipt.sequence = int(self.receipt.sequence)
        number = self.receipt.sequence + 1 if increase else self.receipt.sequence
        return f'{number:09d}'

    def generate_voucher_number_full(self):
        if self.receipt_id is None:
            self.company = Empresa.objects.first()
            self.receipt = Recibo.objects.get(voucher_type=VOUCHER_TYPE[0][0], establishment_code=self.company.establishment_code, issuing_point_code=self.company.issuing_point_code)
        self.voucher_number = self.generate_voucher_number()
        return self.get_voucher_number_full()

    def generate_pdf_authorized(self):
        rv = BytesIO()
        barcode.Code128(self.access_code, writer=barcode.writer.ImageWriter()).write(rv, options={'text_distance': 3.0, 'font_size': 6})
        file = base64.b64encode(rv.getvalue()).decode("ascii")
        context = {'sale': self, 'access_code_barcode': f"data:image/png;base64,{file}"}
        pdf_file = printer.create_pdf(context=context, template_name='sale/format/invoice.html')
        with tempfile.NamedTemporaryFile(delete=True) as file_temp:
            file_temp.write(pdf_file)
            file_temp.flush()
            self.pdf_authorized.save(name=f'{self.receipt.get_name_xml()}_{self.access_code}.pdf', content=File(file_temp))

    def generate_xml(self):
        access_key = SRI().create_access_key(self)
        root = ElementTree.Element('factura', id="comprobante", version="1.0.0")
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
        # infoFactura
        xml_info_invoice = ElementTree.SubElement(root, 'infoFactura')
        ElementTree.SubElement(xml_info_invoice, 'fechaEmision').text = datetime.now().strftime('%d/%m/%Y')
        ElementTree.SubElement(xml_info_invoice, 'dirEstablecimiento').text = self.company.establishment_address
        ElementTree.SubElement(xml_info_invoice, 'obligadoContabilidad').text = self.company.obligated_accounting
        ElementTree.SubElement(xml_info_invoice, 'tipoIdentificacionComprador').text = self.client.identification_type
        ElementTree.SubElement(xml_info_invoice, 'razonSocialComprador').text = self.client.user.names
        ElementTree.SubElement(xml_info_invoice, 'identificacionComprador').text = self.client.dni
        ElementTree.SubElement(xml_info_invoice, 'direccionComprador').text = self.client.address
        ElementTree.SubElement(xml_info_invoice, 'totalSinImpuestos').text = f'{self.get_full_subtotal():.2f}'
        ElementTree.SubElement(xml_info_invoice, 'totalDescuento').text = f'{self.total_dscto:.2f}'
        # totalConImpuestos
        xml_total_with_taxes = ElementTree.SubElement(xml_info_invoice, 'totalConImpuestos')
        # totalImpuesto
        if self.subtotal_0 != 0.0000:
            xml_total_tax_0 = ElementTree.SubElement(xml_total_with_taxes, 'totalImpuesto')
            ElementTree.SubElement(xml_total_tax_0, 'codigo').text = str(TAX_CODES[0][0])
            ElementTree.SubElement(xml_total_tax_0, 'codigoPorcentaje').text = '0'
            ElementTree.SubElement(xml_total_tax_0, 'baseImponible').text = f'{self.subtotal_0:.2f}'
            ElementTree.SubElement(xml_total_tax_0, 'valor').text = '0.00'
        if self.subtotal_12 != 0.0000:
            xml_total_tax12 = ElementTree.SubElement(xml_total_with_taxes, 'totalImpuesto')
            ElementTree.SubElement(xml_total_tax12, 'codigo').text = str(TAX_CODES[0][0])
            ElementTree.SubElement(xml_total_tax12, 'codigoPorcentaje').text = str(self.company.vat_percentage)
            ElementTree.SubElement(xml_total_tax12, 'baseImponible').text = f'{self.subtotal_12:.2f}'
            ElementTree.SubElement(xml_total_tax12, 'valor').text = f'{self.total_iva:.2f}'
        ElementTree.SubElement(xml_info_invoice, 'propina').text = '0.00'
        ElementTree.SubElement(xml_info_invoice, 'importeTotal').text = f'{self.total:.2f}'
        ElementTree.SubElement(xml_info_invoice, 'moneda').text = 'DOLAR'
        # pagos
        xml_payments = ElementTree.SubElement(xml_info_invoice, 'pagos')
        xml_payment = ElementTree.SubElement(xml_payments, 'pago')
        ElementTree.SubElement(xml_payment, 'formaPago').text = self.payment_method
        ElementTree.SubElement(xml_payment, 'total').text = f'{self.total:.2f}'
        ElementTree.SubElement(xml_payment, 'plazo').text = str(self.time_limit)
        ElementTree.SubElement(xml_payment, 'unidadTiempo').text = 'dias'
        # detalles
        xml_details = ElementTree.SubElement(root, 'detalles')
        for detail in self.saledetail_set.all():
            xml_detail = ElementTree.SubElement(xml_details, 'detalle')
            ElementTree.SubElement(xml_detail, 'codigoPrincipal').text = detail.product.code
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
        if len(self.additional_info):
            xml_additional_info = ElementTree.SubElement(root, 'infoAdicional')
            for additional_info in self.additional_info:
                ElementTree.SubElement(xml_additional_info, 'campoAdicional', nombre=additional_info['name']).text = additional_info['value']
        return ElementTree.tostring(root, xml_declaration=True, encoding='utf-8').decode('utf-8').replace("'", '"'), access_key

    def is_invoice(self):
        return self.receipt.voucher_type == VOUCHER_TYPE[0][0]

    def toJSON(self):
        item = model_to_dict(self)
        item['company'] = self.company.toJSON()
        item['client'] = self.client.toJSON()
        item['receipt'] = self.receipt.toJSON()
        item['employee'] = self.employee.toJSON()
        item['payment_type'] = {'id': self.payment_type, 'name': self.get_payment_type_display()}
        item['payment_method'] = {'id': self.payment_method, 'name': self.get_payment_method_display()}
        item['creation_date'] = self.creation_date.strftime('%Y-%m-%d %H:%M:%S')
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        item['end_credit'] = self.end_credit.strftime('%Y-%m-%d')
        item['subtotal_0'] = float(self.subtotal_0)
        item['subtotal_12'] = float(self.subtotal_12)
        item['subtotal'] = self.get_full_subtotal()
        item['total_dscto'] = float(self.total_dscto)
        item['iva'] = float(self.iva)
        item['total_iva'] = float(self.total_iva)
        item['total'] = float(self.total)
        item['cash'] = float(self.cash)
        item['change'] = float(self.change)
        item['environment_type'] = {'id': self.environment_type, 'name': self.get_environment_type_display()}
        item['authorization_date'] = '' if self.authorization_date is None else self.authorization_date.strftime('%Y-%m-%d')
        item['xml_authorized'] = self.get_xml_authorized()
        item['pdf_authorized'] = self.get_pdf_authorized()
        item['status'] = {'id': self.status, 'name': self.get_status_display()}
        return item

    def calculate_detail(self):
        for detail in self.saledetail_set.filter():
            detail.price = float(detail.price)
            detail.iva = float(self.iva)
            detail.price_with_vat = detail.price + (detail.price * detail.iva)
            detail.subtotal = detail.price * detail.cant
            detail.total_dscto = detail.subtotal * float(detail.dscto)
            detail.total_iva = (detail.subtotal - detail.total_dscto) * detail.iva
            detail.total = detail.subtotal - detail.total_dscto
            detail.save()

    def calculate_invoice(self):
        self.subtotal_0 = float(self.saledetail_set.filter(product__with_tax=False).aggregate(result=Coalesce(Sum('total'), 0.00, output_field=FloatField()))['result'])
        self.subtotal_12 = float(self.saledetail_set.filter(product__with_tax=True).aggregate(result=Coalesce(Sum('total'), 0.00, output_field=FloatField()))['result'])
        self.total_iva = float(self.saledetail_set.filter(product__with_tax=True).aggregate(result=Coalesce(Sum('total_iva'), 0.00, output_field=FloatField()))['result'])
        self.total_dscto = float(self.saledetail_set.filter().aggregate(result=Coalesce(Sum('total_dscto'), 0.00, output_field=FloatField()))['result'])
        self.total = float(self.get_full_subtotal()) + float(self.total_iva)
        self.save()

    def edit(self):
        super(Sale, self).save()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.pk is None:
            self.receipt.sequence = int(self.voucher_number)
            self.receipt.save()
        super(Sale, self).save()

    def delete(self, using=None, keep_parents=False):
        try:
            for i in self.saledetail_set.filter(product__inventoried=True):
                i.product.stock += i.cant
                i.product.save()
                i.delete()
        except:
            pass
        super(Sale, self).delete()

    def generate_electronic_invoice(self):
        sri = SRI()
        result = sri.create_xml(self)
        if result['resp']:
            result = sri.firm_xml(instance=self, xml=result['xml'])
            if result['resp']:
                result = sri.validate_xml(instance=self, xml=result['xml'])
                if result['resp']:
                    result = sri.authorize_xml(instance=self)
                    index = 1
                    while not result['resp'] and index < 3:
                        time.sleep(1)
                        result = sri.authorize_xml(instance=self)
                        index += 1
                    if result['resp']:
                        result['print_url'] = self.get_pdf_authorized()
                    return result
        return result

    class Meta:
        db_table = 'tb_venta'
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['id']


class SaleDetail(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    product = models.ForeignKey(Producto, on_delete=models.PROTECT)
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

    def get_iva_percent(self):
        return int(self.iva * 100)

    def toJSON(self, args=None):
        item = model_to_dict(self, exclude=['sale'])
        item['product'] = self.product.toJSON()
        item['price'] = float(self.price)
        item['price_with_vat'] = float(self.price_with_vat)
        item['subtotal'] = float(self.subtotal)
        item['iva'] = float(self.subtotal)
        item['total_iva'] = float(self.subtotal)
        item['dscto'] = float(self.dscto) * 100
        item['total_dscto'] = float(self.total_dscto)
        item['total'] = float(self.total)
        if args is not None:
            item.update(args)
        return item

    class Meta:
        db_table = 'tb_detVenta'
        verbose_name = 'Detalle de Venta'
        verbose_name_plural = 'Detalle de Ventas'
        ordering = ['id']


class CtasCollect(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.PROTECT)
    date_joined = models.DateField(default=datetime.now)
    end_date = models.DateField(default=datetime.now)
    debt = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    saldo = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    state = models.BooleanField(default=True)

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return f"{self.sale.client.user.names} ({self.sale.client.dni}) / {self.date_joined.strftime('%Y-%m-%d')} / ${f'{self.debt:.2f}'}"

    def validate_debt(self):
        try:
            saldo = self.paymentsctacollect_set.aggregate(result=Coalesce(Sum('valor'), 0.00, output_field=FloatField()))['result']
            self.saldo = float(self.debt) - float(saldo)
            self.state = self.saldo > 0.00
            self.save()
        except:
            pass

    def toJSON(self):
        item = model_to_dict(self)
        item['sale'] = self.sale.toJSON()
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        item['end_date'] = self.end_date.strftime('%Y-%m-%d')
        item['debt'] = float(self.debt)
        item['saldo'] = float(self.saldo)
        return item

    class Meta:
        db_table = 'tb_ctasCollect'
        verbose_name = 'Cuenta por cobrar'
        verbose_name_plural = 'Cuentas por cobrar'
        ordering = ['id']



class PaymentsCtaCollect(models.Model):
    ctas_collect = models.ForeignKey(CtasCollect, on_delete=models.CASCADE, verbose_name='Cuenta por cobrar')
    date_joined = models.DateField(default=datetime.now, verbose_name='Fecha de registro')
    description = models.CharField(max_length=500, null=True, blank=True, verbose_name='Detalles')
    valor = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Valor')

    def __str__(self):
        return self.ctas_collect.id

    def toJSON(self):
        item = model_to_dict(self, exclude=['ctas_collect'])
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        item['valor'] = float(self.valor)
        return item

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.description is None:
            self.description = 's/n'
        elif len(self.description) == 0:
            self.description = 's/n'
        super(PaymentsCtaCollect, self).save()

    class Meta:
        db_table = 'tb_pagoCtascollect'
        verbose_name = 'Pago Cuenta por cobrar'
        verbose_name_plural = 'Pagos Cuentas por cobrar'
        ordering = ['id']


class DebtsPay(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.PROTECT)
    date_joined = models.DateField(default=datetime.now)
    end_date = models.DateField(default=datetime.now)
    debt = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    saldo = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    state = models.BooleanField(default=True)

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return f"{self.purchase.provider.nombre_com} ({self.purchase.number}) / {self.date_joined.strftime('%Y-%m-%d')} / ${f'{self.debt:.2f}'}"

    def validate_debt(self):
        try:
            saldo = self.paymentsdebtspay_set.aggregate(result=Coalesce(Sum('valor'), 0.00, output_field=FloatField()))['result']
            self.saldo = float(self.debt) - float(saldo)
            self.state = self.saldo > 0.00
            self.save()
        except:
            pass

    def toJSON(self):
        item = model_to_dict(self)
        item['purchase'] = self.purchase.toJSON()
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        item['end_date'] = self.end_date.strftime('%Y-%m-%d')
        item['debt'] = float(self.debt)
        item['saldo'] = float(self.saldo)
        return item

    class Meta:
        db_table = 'tb_ctasPorpagar'
        verbose_name = 'Cuenta por pagar'
        verbose_name_plural = 'Cuentas por pagar'
        ordering = ['id']


class PaymentsDebtsPay(models.Model):
    debts_pay = models.ForeignKey(DebtsPay, on_delete=models.CASCADE, verbose_name='Cuenta por pagar')
    date_joined = models.DateField(default=datetime.now, verbose_name='Fecha de registro')
    description = models.CharField(max_length=500, null=True, blank=True, verbose_name='Detalles')
    valor = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Valor')

    def __str__(self):
        return self.debts_pay.id

    def toJSON(self):
        item = model_to_dict(self, exclude=['debts_pay'])
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        item['valor'] = float(self.valor)
        return item

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.description is None:
            self.description = 's/n'
        elif len(self.description) == 0:
            self.description = 's/n'
        super(PaymentsDebtsPay, self).save()

    class Meta:
        db_table = 'tb_detCtasporpagar'
        verbose_name = 'Det. Cuenta por pagar'
        verbose_name_plural = 'Det. Cuentas por pagar'
        ordering = ['id']


class TypeExpense(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Nombre')

    def __str__(self):
        return self.name

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        db_table = 'tb_tipoGasto'
        verbose_name = 'Tipo de Gasto'
        verbose_name_plural = 'Tipos de Gastos'
        ordering = ['id']


class Expenses(models.Model):
    type_expense = models.ForeignKey(TypeExpense, on_delete=models.PROTECT, verbose_name='Tipo de Gasto')
    description = models.CharField(max_length=500, null=True, blank=True, verbose_name='Descripción')
    date_joined = models.DateField(default=datetime.now, verbose_name='Fecha de Registro')
    valor = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Valor')

    def __str__(self):
        return self.description

    def toJSON(self):
        item = model_to_dict(self)
        item['type_expense'] = self.type_expense.toJSON()
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        item['valor'] = float(self.valor)
        return item

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.description is None:
            self.description = 's/n'
        elif len(self.description) == 0:
            self.description = 's/n'
        super(Expenses, self).save()

    class Meta:
        db_table = 'tb_gasto'
        verbose_name = 'Gasto'
        verbose_name_plural = 'Gastos'
        ordering = ['id']
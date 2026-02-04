# app_retencion/models.py
import base64
from io import BytesIO
from decimal import Decimal, ROUND_HALF_UP
import xml.etree.ElementTree as ET
from datetime import date

from django.db import models, transaction
from django.forms import model_to_dict
from django.template.loader import render_to_string
from django.core.files import File

from weasyprint import HTML
from barcode.writer import ImageWriter
import barcode
from tempfile import NamedTemporaryFile

from Sistema_Camaronera import settings
from app_empresa.app_reg_empresa.models import Empresa
from app_proveedor.models import Proveedor
from app_contabilidad_planCuentas.models import Recibo

# Servicio SRI
from utilities.sri import SRI


# ======================================================
# MODELO RETENCIÓN
# ======================================================
class Retention(models.Model):
    company = models.ForeignKey(Empresa, on_delete=models.PROTECT)
    provider = models.ForeignKey(Proveedor, on_delete=models.PROTECT, null=True, blank=True)
    receipt = models.ForeignKey(Recibo, on_delete=models.PROTECT, null=True, blank=True)

    voucher_number = models.CharField(max_length=9, default='', blank=True)
    voucher_number_full = models.CharField(max_length=20, default='', blank=True)

    date_joined = models.DateField(auto_now_add=True)
    authorization_date = models.DateField(null=True, blank=True)
    access_code = models.CharField(max_length=49, null=True, blank=True)

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_iva = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_renta = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_retained = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    pdf_authorized = models.FileField(upload_to='retenciones/', null=True, blank=True)

    email_sent = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.voucher_number_full} / {self.provider.razon_soc if self.provider else "-"}'

    # --------------------------------------------------
    # SECUENCIA ATS (RECIBO)
    # --------------------------------------------------
    def generate_voucher_number(self):
        if self.voucher_number:
            return

        with transaction.atomic():
            recibo = Recibo.objects.select_for_update().get(
                empresa=self.company,
                voucher_type='07'
            )

            recibo.sequence += 1
            recibo.save(update_fields=['sequence'])

            secuencia = str(recibo.sequence).zfill(9)

            self.voucher_number = secuencia
            self.voucher_number_full = (
                f"{recibo.establishment_code}-"
                f"{recibo.issuing_point_code}-"
                f"{secuencia}"
            )
            self.receipt = recibo

    # --------------------------------------------------
    # TOTALES
    # --------------------------------------------------
    def update_totals(self):
        details = self.details.all()
        self.subtotal = sum(d.base for d in details)
        self.total_iva = sum(d.value for d in details if d.tax_type == 'IVA')
        self.total_renta = sum(d.value for d in details if d.tax_type == 'RENTA')
        self.total_retained = self.total_iva + self.total_renta
        self.save(update_fields=[
            'subtotal',
            'total_iva',
            'total_renta',
            'total_retained'
        ])

    # --------------------------------------------------
    # CLAVE DE ACCESO SRI
    # --------------------------------------------------
    def generate_access_code(self):
        if self.access_code:
            return

        sri = SRI()
        access_key = sri.create_access_key(self)

        if not access_key:
            raise ValueError("No se pudo generar la clave de acceso SRI")

        self.access_code = access_key
        self.authorization_date = date.today()
        self.save(update_fields=['access_code', 'authorization_date'])

    # --------------------------------------------------
    # BARCODE
    # --------------------------------------------------
    def get_access_code_barcode(self):
        if not self.access_code:
            return None

        rv = BytesIO()
        barcode.Code128(self.access_code, writer=ImageWriter()).write(
            rv, options={'text_distance': 3.0, 'font_size': 6}
        )
        return f"data:image/png;base64,{base64.b64encode(rv.getvalue()).decode()}"

    # --------------------------------------------------
    # PDF
    # --------------------------------------------------
    def generate_pdf(self):
        context = {
            'retention': self,
            'access_code_barcode': self.get_access_code_barcode(),
            'logo_base64': self.company.get_logo_base64(),
        }

        html_string = render_to_string(
            'app_retencion/admin/retention.html',
            context
        )

        pdf_file = BytesIO()

        HTML(
            string=html_string,
            base_url=settings.BASE_DIR  # 🔥 ESTA LÍNEA ES LA CLAVE
        ).write_pdf(pdf_file)

        pdf_file.seek(0)
        return pdf_file

    def save_pdf_authorized(self):
        self.generate_access_code()
        pdf = self.generate_pdf()

        with NamedTemporaryFile(delete=True) as tmp:
            tmp.write(pdf.getvalue())
            tmp.flush()
            self.pdf_authorized.save(
                f"retencion_{self.voucher_number_full}.pdf",
                File(tmp),
                save=True
            )

    # --------------------------------------------------
    # XML SRI
    # --------------------------------------------------
    # En tu modelo Retention, modifica el método generate_xml
    def generate_xml(self, filepath):
        self.generate_access_code()

        comprobante = ET.Element("comprobanteRetencion", id="comprobante", version="2.0.0")

        info = ET.SubElement(comprobante, "infoTributaria")
        ET.SubElement(info, "razonSocial").text = self.company.business_name
        ET.SubElement(info, "ruc").text = self.company.ruc
        ET.SubElement(info, "claveAcceso").text = self.access_code
        ET.SubElement(info, "codDoc").text = "07"
        ET.SubElement(info, "estab").text = self.receipt.establishment_code
        ET.SubElement(info, "ptoEmi").text = self.receipt.issuing_point_code
        ET.SubElement(info, "secuencial").text = self.voucher_number
        ET.SubElement(info, "dirMatriz").text = self.company.direccion or "-"

        info_ret = ET.SubElement(comprobante, "infoCompRetencion")
        ET.SubElement(info_ret, "fechaEmision").text = self.date_joined.strftime('%d/%m/%Y')
        ET.SubElement(info_ret, "razonSocialSujetoRetenido").text = self.provider.razon_soc
        ET.SubElement(info_ret, "identificacionSujetoRetenido").text = self.provider.ruc
        ET.SubElement(info_ret, "dirEstablecimiento").text = (
                self.provider.direccion1 or "-"
        )
        ET.SubElement(info_ret, "periodoFiscal").text = self.date_joined.strftime('%m/%Y')

        impuestos = ET.SubElement(comprobante, "impuestos")
        for d in self.details.all():
            imp = ET.SubElement(impuestos, "impuesto")
            ET.SubElement(imp, "codigo").text = "2" if d.tax_type == "IVA" else "1"
            ET.SubElement(imp, "baseImponible").text = f"{d.base:.2f}"
            ET.SubElement(imp, "porcentajeRetener").text = f"{d.percentage:.2f}"
            ET.SubElement(imp, "valorRetenido").text = f"{d.value:.2f}"

            # AGREGAR NUEVOS CAMPOS AL XML
            if d.numero_15_digitos:  # Solo incluir si tiene valor
                ET.SubElement(imp, "numeroDocumento").text = d.numero_15_digitos
            ET.SubElement(imp, "compPagoCuota").text = d.comp_pago_cuota
            # Si quieres el valor legible en lugar del código:
            # ET.SubElement(imp, "compPagoCuota").text = d.get_comp_pago_cuota_display()

        ET.ElementTree(comprobante).write(filepath, encoding="UTF-8", xml_declaration=True)

    def toJSON(self):
        item = model_to_dict(self)
        item['details'] = [d.toJSON() for d in self.details.all()]
        item['subtotal'] = float(self.subtotal)
        item['total_iva'] = float(self.total_iva)
        item['total_renta'] = float(self.total_renta)
        item['total_retained'] = float(self.total_retained)
        return item

    # --------------------------------------------------
    # SAVE CONTROLADO
    # --------------------------------------------------
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and not self.voucher_number:
            self.generate_voucher_number()
            super().save(update_fields=[
                'voucher_number',
                'voucher_number_full',
                'receipt'
            ])


# ======================================================
# DETALLE DE RETENCIÓN
# ======================================================
class RetentionDetail(models.Model):
    COMP_PAGO_CUOTA_CHOICES = [
        ('OPCION_1', 'OPCIÓN 1'),
        ('OPCION_2', 'OPCIÓN 2'),
        ('OPCION_3', 'OPCIÓN 3'),
        ('OPCION_4', 'OPCIÓN 4'),
        ('OPCION_5', 'OPCIÓN 5'),
        ('OPCION_6', 'OPCIÓN 6'),
        ('OPCION_7', 'OPCIÓN 7'),
        ('OPCION_8', 'OPCIÓN 8'),
        ('OPCION_9', 'OPCIÓN 9'),
        ('OPCION_10', 'OPCIÓN 10'),
        ('OPCION_11', 'OPCIÓN 11'),
        ('COMP_PAGO_CUOTA', 'COMP. PAGO CUOTA'),  # Opción 12
        ('OPCION_13', 'OPCIÓN 13'),
        ('OPCION_14', 'OPCIÓN 14'),
        ('OPCION_15', 'OPCIÓN 15'),
    ]

    retention = models.ForeignKey(Retention, related_name='details', on_delete=models.CASCADE)
    tax_type = models.CharField(max_length=10, choices=(('IVA', 'IVA'), ('RENTA', 'RENTA')))
    tax_code = models.CharField(max_length=10)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    base = models.DecimalField(max_digits=12, decimal_places=2)
    value = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    # Nuevos campos solicitados
    numero_15_digitos = models.CharField(
        max_length=15,
        verbose_name="Número (15 dígitos máximo)",
        help_text="Ingrese un número de hasta 15 dígitos",
        blank=True,
        null=True
    )

    comp_pago_cuota = models.CharField(
        max_length=20,
        choices=COMP_PAGO_CUOTA_CHOICES,
        verbose_name="COMP. PAGO CUOTA",
        help_text="Seleccione una opción, la opción 12 es 'COMP. PAGO CUOTA'",
        default='OPCION_1'
    )

    def save(self, *args, **kwargs):
        self.value = (self.base * self.percentage / Decimal('100')).quantize(
            Decimal('0.01'),
            rounding=ROUND_HALF_UP
        )
        super().save(*args, **kwargs)

        if self.retention:
            self.retention.update_totals()

    def toJSON(self):
        return {
            'tax_type': self.tax_type,
            'tax_code': self.tax_code,
            'percentage': float(self.percentage),
            'base': float(self.base),
            'value': float(self.value),
            'numero_15_digitos': self.numero_15_digitos,
            'comp_pago_cuota': self.comp_pago_cuota,
            'comp_pago_cuota_display': self.get_comp_pago_cuota_display(),
        }

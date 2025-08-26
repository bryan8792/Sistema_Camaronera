import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime
from .models import ATSCompra, ATSVenta, ATSAnulado, ATSPeriodo
import os


class ATSXMLGenerator:
    """Generador de archivos XML para ATS"""

    def __init__(self, config, periodo):
        self.config = config
        self.periodo = periodo

    def generar_xml(self, destino=None):
        """Genera el archivo XML ATS"""
        try:
            # Crear elemento raíz
            root = ET.Element("iva")

            # Información del contribuyente
            info_tributaria = ET.SubElement(root, "TipoIDInformante")
            info_tributaria.text = "R"

            id_informante = ET.SubElement(root, "IdInformante")
            id_informante.text = self.config.id_receptor

            razon_social = ET.SubElement(root, "razonSocial")
            razon_social.text = self.config.nombre_receptor

            # Período
            anio_elem = ET.SubElement(root, "Anio")
            anio_elem.text = str(self.periodo.anio)

            mes_elem = ET.SubElement(root, "Mes")
            mes_elem.text = self._get_mes_numero(self.periodo.periodo)

            # Compras
            compras = ATSCompra.objects.filter(periodo=self.periodo)
            if compras.exists():
                compras_elem = ET.SubElement(root, "compras")
                for compra in compras:
                    self._add_compra_xml(compras_elem, compra)

            # Ventas
            ventas = ATSVenta.objects.filter(periodo=self.periodo)
            if ventas.exists():
                ventas_elem = ET.SubElement(root, "ventas")
                for venta in ventas:
                    self._add_venta_xml(ventas_elem, venta)

            # Anulados
            anulados = ATSAnulado.objects.filter(periodo=self.periodo)
            if anulados.exists():
                anulados_elem = ET.SubElement(root, "anulados")
                for anulado in anulados:
                    self._add_anulado_xml(anulados_elem, anulado)

            # Generar archivo
            tree = ET.ElementTree(root)
            if destino:
                filename = f"ATS_{self.config.id_receptor}_{self.periodo.periodo}_{self.periodo.anio}.xml"
                filepath = os.path.join(destino, filename)
                tree.write(filepath, encoding='utf-8', xml_declaration=True)
                return filepath

            return ET.tostring(root, encoding='utf-8')

        except Exception as e:
            raise Exception(f"Error generando XML: {str(e)}")

    def _get_mes_numero(self, mes_nombre):
        """Convierte nombre del mes a número"""
        meses = {
            'Enero': '01', 'Febrero': '02', 'Marzo': '03', 'Abril': '04',
            'Mayo': '05', 'Junio': '06', 'Julio': '07', 'Agosto': '08',
            'Septiembre': '09', 'Octubre': '10', 'Noviembre': '11', 'Diciembre': '12'
        }
        return meses.get(mes_nombre, '01')

    def _add_compra_xml(self, parent, compra):
        """Añade elemento de compra al XML"""
        compra_elem = ET.SubElement(parent, "detalleCompras")

        ET.SubElement(compra_elem, "codSustento").text = compra.sust_tp
        ET.SubElement(compra_elem, "tpIdProv").text = compra.tp_id
        ET.SubElement(compra_elem, "idProv").text = compra.no_identif
        ET.SubElement(compra_elem, "tipoComprobante").text = "01"
        ET.SubElement(compra_elem, "fechaRegistro").text = compra.fecha_emision.strftime('%d/%m/%Y')
        ET.SubElement(compra_elem, "establecimiento").text = compra.no_doc[:3]
        ET.SubElement(compra_elem, "puntoEmision").text = compra.no_doc[4:7]
        ET.SubElement(compra_elem, "secuencial").text = compra.no_doc[8:]
        ET.SubElement(compra_elem, "fechaEmision").text = compra.fecha_emision.strftime('%d/%m/%Y')
        ET.SubElement(compra_elem, "autorizacion").text = ""
        ET.SubElement(compra_elem, "baseNoGraIva").text = str(compra.excento)
        ET.SubElement(compra_elem, "baseImponible").text = str(compra.base_iva)
        ET.SubElement(compra_elem, "baseImpGrav").text = str(compra.base_0)
        ET.SubElement(compra_elem, "montoIva").text = str(compra.monto_iva)
        ET.SubElement(compra_elem, "valorRetIva").text = str(compra.rt_iva)
        ET.SubElement(compra_elem, "valorRetRenta").text = str(compra.rt_fte)

    def _add_venta_xml(self, parent, venta):
        """Añade elemento de venta al XML"""
        venta_elem = ET.SubElement(parent, "detalleVentas")

        ET.SubElement(venta_elem, "tpIdCliente").text = venta.tp_id
        ET.SubElement(venta_elem, "idCliente").text = venta.no_identif
        ET.SubElement(venta_elem, "tipoComprobante").text = venta.tp_comp
        ET.SubElement(venta_elem, "numeroComprobantes").text = "1"
        ET.SubElement(venta_elem, "baseNoGraIva").text = str(venta.no_objeto_iva)
        ET.SubElement(venta_elem, "baseImponible").text = str(venta.base_imp_iva)
        ET.SubElement(venta_elem, "baseImpGrav").text = str(venta.base_imp_0)
        ET.SubElement(venta_elem, "montoIva").text = str(venta.monto_iva)
        ET.SubElement(venta_elem, "valorRetIva").text = str(venta.ret_iva)
        ET.SubElement(venta_elem, "valorRetRenta").text = str(venta.ret_fte)

    def _add_anulado_xml(self, parent, anulado):
        """Añade elemento de anulado al XML"""
        anulado_elem = ET.SubElement(parent, "detalleAnulados")

        ET.SubElement(anulado_elem, "tipoComprobante").text = anulado.tp_doc
        ET.SubElement(anulado_elem, "establecimiento").text = anulado.no_documento[:3]
        ET.SubElement(anulado_elem, "puntoEmision").text = anulado.no_documento[4:7]
        ET.SubElement(anulado_elem, "secuencialInicio").text = anulado.no_documento[8:]
        ET.SubElement(anulado_elem, "secuencialFin").text = anulado.no_documento[8:]
        ET.SubElement(anulado_elem, "autorizacion").text = anulado.clave_acceso


class ATSXMLImporter:
    """Importador de archivos XML ATS"""

    def __init__(self):
        pass

    def importar_xml(self, archivo_xml, modo='agregar'):
        """Importa datos desde archivo XML ATS"""
        try:
            tree = ET.parse(archivo_xml)
            root = tree.getroot()

            # Extraer información básica
            id_informante = root.find('IdInformante').text if root.find('IdInformante') is not None else ''
            razon_social = root.find('razonSocial').text if root.find('razonSocial') is not None else ''
            anio = root.find('Anio').text if root.find('Anio') is not None else ''
            mes = root.find('Mes').text if root.find('Mes') is not None else ''

            # Crear resumen
            resumen = {
                'periodo': f"{self._get_mes_nombre(mes)} {anio}",
                'informante': razon_social,
                'compras': {'total': 0},
                'ventas': {'total': 0},
                'anulados': {'total': 0}
            }

            # Procesar compras
            compras_elem = root.find('compras')
            if compras_elem is not None:
                resumen['compras']['total'] = len(compras_elem.findall('detalleCompras'))

            # Procesar ventas
            ventas_elem = root.find('ventas')
            if ventas_elem is not None:
                resumen['ventas']['total'] = len(ventas_elem.findall('detalleVentas'))

            # Procesar anulados
            anulados_elem = root.find('anulados')
            if anulados_elem is not None:
                resumen['anulados']['total'] = len(anulados_elem.findall('detalleAnulados'))

            return resumen

        except Exception as e:
            raise Exception(f"Error importando XML: {str(e)}")

    def _get_mes_nombre(self, mes_numero):
        """Convierte número del mes a nombre"""
        meses = {
            '01': 'Enero', '02': 'Febrero', '03': 'Marzo', '04': 'Abril',
            '05': 'Mayo', '06': 'Junio', '07': 'Julio', '08': 'Agosto',
            '09': 'Septiembre', '10': 'Octubre', '11': 'Noviembre', '12': 'Diciembre'
        }
        return meses.get(mes_numero, 'Enero')


class ATSExcelImporter:
    """Importador de archivos Excel para compras y ventas"""

    def __init__(self):
        pass

    def importar_compras_excel(self, archivo_excel, periodo):
        """Importa compras desde archivo Excel"""
        try:
            df = pd.read_excel(archivo_excel)

            # Mapear columnas del Excel a campos del modelo
            compras_creadas = 0

            for index, row in df.iterrows():
                compra = ATSCompra(
                    periodo=periodo,
                    tp_id=row.get('TP_ID', ''),
                    no_identif=row.get('No_Identif', ''),
                    proveedor=row.get('Proveedor', ''),
                    sust_tp=row.get('Sust_TP', ''),
                    no_doc=row.get('No_Doc', ''),
                    fecha_emision=pd.to_datetime(row.get('F_Emision')).date(),
                    valor_objeto_iva=row.get('V_Ito_Obj_IVA', 0),
                    excento=row.get('Excento', 0),
                    base_0=row.get('Base_0', 0),
                    base_iva=row.get('Base_IVA', 0),
                    monto_iva=row.get('Monto_IVA', 0),
                    total=row.get('Total', 0),
                    no_retenc=row.get('No_Retenc', ''),
                    rt_iva=row.get('RT_IVA', 0),
                    rt_fte=row.get('RT_FTE', 0)
                )
                compra.save()
                compras_creadas += 1

            return compras_creadas

        except Exception as e:
            raise Exception(f"Error importando Excel de compras: {str(e)}")

    def importar_ventas_excel(self, archivo_excel, periodo):
        """Importa ventas desde archivo Excel"""
        try:
            df = pd.read_excel(archivo_excel)

            # Mapear columnas del Excel a campos del modelo
            ventas_creadas = 0

            for index, row in df.iterrows():
                venta = ATSVenta(
                    periodo=periodo,
                    tp_id=row.get('TP_ID', ''),
                    no_identif=row.get('No_Identif', ''),
                    cliente=row.get('Cliente', ''),
                    tp_comp=row.get('Tp_Comp', ''),
                    no_docs=row.get('No_Docs', ''),
                    base_imp_0=row.get('Base_Imp_0', 0),
                    base_imp_iva=row.get('Base_Imp_IVA', 0),
                    monto_iva=row.get('Monto_IVA', 0),
                    no_objeto_iva=row.get('No_Objeto_IVA', 0),
                    ret_iva=row.get('Ret_IVA', 0),
                    ret_fte=row.get('Ret_Fte', 0)
                )
                venta.save()
                ventas_creadas += 1

            return ventas_creadas

        except Exception as e:
            raise Exception(f"Error importando Excel de ventas: {str(e)}")

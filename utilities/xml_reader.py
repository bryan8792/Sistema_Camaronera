
import xml.etree.ElementTree as ET
import json

class XMLReader:

    def read(self, path=''):
        try:
            # Parsear el archivo XML
            tree = ET.parse(path)
            root = tree.getroot()

            # Extraer información de infoTributaria
            info_tributaria = self.extract_info(root, 'infoTributaria', [
                'razonSocial', 'ruc', 'claveAcceso', 'secuencial', 'dirMatriz'
            ])

            # Extraer información de infoFactura
            info_factura = self.extract_info(root, 'infoFactura', [
                'fechaEmision', 'totalSinImpuestos', 'totalDescuento', 'importeTotal'
            ])

            # Extraer detalles de la factura
            detalles = self.extract_detalles(root, 'detalles', [
                'descripcion', 'cantidad', 'precioUnitario', 'precioTotalSinImpuesto'
            ])

            # Extraer información adicional (infoAdicional)
            info_adicional = self.extract_info_adicional(root, 'infoAdicional')

            # Crear un diccionario con los datos extraídos
            return {
                'info_tributaria': info_tributaria,
                'info_factura': info_factura,
                'detalles': detalles,
                'info_adicional': info_adicional,
            }
        except ET.ParseError:
            print(f"Error: No se pudo parsear el archivo XML en la ruta '{path}'.")
        except FileNotFoundError:
            print(f"Error: Archivo no encontrado en la ruta '{path}'.")
        except Exception as e:
            print(f"Error inesperado: {str(e)}")
        return {}

    @staticmethod
    def extract_info(root, section, fields):
        """
        Extrae información de una sección específica del XML.
        """
        section_data = {}
        section_element = root.find(section)
        if section_element is not None:
            for field in fields:
                value = section_element.findtext(field, default=None)
                section_data[field] = value
        return section_data

    @staticmethod
    def extract_detalles(root, section, fields):
        """
        Extrae los detalles de una sección específica del XML.
        """
        detalles = []
        detalles_section = root.find(section)
        if detalles_section is not None:
            for detalle in detalles_section.findall('detalle'):
                detalle_data = {}
                for field in fields:
                    detalle_data[field] = detalle.findtext(field, default=None)
                detalles.append(detalle_data)
        return detalles

    @staticmethod
    def extract_info_adicional(root, section):
        """
        Extrae la información adicional del XML.
        """
        info_adicional = {}
        info_adicional_section = root.find(section)
        if info_adicional_section is not None:
            for campo_adicional in info_adicional_section.findall('campoAdicional'):
                nombre = campo_adicional.get('nombre')
                valor = campo_adicional.text
                if nombre:
                    info_adicional[nombre] = valor
        return info_adicional


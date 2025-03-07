import random
from xml.etree import ElementTree
import json


class XML:

    def read(self, path=''):
        items = {}
        try:
            root = ElementTree.parse(path).getroot()

            # Extraer información tributaria
            info_tributaria = root.find('infoTributaria')
            razon_social = info_tributaria.find('razonSocial').text
            print(f"Razón Social: {razon_social}")
            nombre_comercial = info_tributaria.find('nombreComercial').text
            print(f"Nombre Comercial: {nombre_comercial}")
            ruc = info_tributaria.find('ruc').text
            print(f"RUC: {ruc}")
            clave_acceso = info_tributaria.find('claveAcceso').text
            print(f"Clave de Acceso: {clave_acceso}")
            cod_estab = info_tributaria.find('estab').text
            print(f"Estab codigo: {cod_estab}")
            pto_Emi = info_tributaria.find('ptoEmi').text
            print(f"Punto Emi: {pto_Emi}")
            secuencial = info_tributaria.find('secuencial').text
            print(f"Secuencial: {secuencial}")
            dir_matriz = info_tributaria.find('dirMatriz').text
            print(f"Dirección Matriz: {dir_matriz}")
            cont_Rimpe = info_tributaria.find('contribuyenteRimpe')
            if cont_Rimpe is not None and cont_Rimpe.text:
                cont_Rimpe = cont_Rimpe.text
            else:
                cont_Rimpe = ''

            # Extraer información de la factura
            info_factura = root.find('infoFactura')
            fecha_emision = info_factura.find('fechaEmision').text
            print(f"Fecha de Emisión: {fecha_emision}")
            rsComprador = info_factura.find('razonSocialComprador').text
            print(f"Razon Social Comprador: {rsComprador}")
            idn_Comprador = info_factura.find('identificacionComprador').text
            print(f"Identificación Comprador: {idn_Comprador}")
            total_sin_impuestos = info_factura.find('totalSinImpuestos').text
            print(f"Total sin Impuestos: {total_sin_impuestos}")
            total_descuento = info_factura.find('totalDescuento').text
            print(f"Total Descuento: {total_descuento}")
            importe_total = info_factura.find('importeTotal').text
            print(f"Importe Total: {importe_total}")

            # Extraer detalles de la factura
            detalles = []
            print("Detalles:")
            for detalle in root.find('detalles').findall('detalle'):
                descripcion = detalle.find('descripcion').text
                cantidad = detalle.find('cantidad').text
                precio_unitario = detalle.find('precioUnitario').text
                precio_total = detalle.find('precioTotalSinImpuesto').text

                print(f"  Descripción: {descripcion}")
                print(f"  Cantidad: {cantidad}")
                print(f"  Precio Unitario: {precio_unitario}")
                print(f"  Precio Total: {precio_total}")

                detalle_dict = {
                    'descripcion': descripcion,
                    'cantidad': cantidad,
                    'precio_unitario': precio_unitario,
                    'precio_total': precio_total,
                }

                detalles.append(detalle_dict)

            # Crear un diccionario con los datos extraídos
            items = {
                'info_tributaria': {
                    'razon_social': razon_social,
                    'nombre_comercial': nombre_comercial,
                    'ruc': ruc,
                    'cod_estab': cod_estab,
                    'pto_Emi': pto_Emi,
                    'clave_acceso': clave_acceso,
                    'secuencial': secuencial,
                    'dir_matriz': dir_matriz,
                    'cont_Rimpe': cont_Rimpe,
                },
                'info_factura': {
                    'fecha_emision': fecha_emision,
                    'total_sin_impuestos': total_sin_impuestos,
                    'total_descuento': total_descuento,
                    'importe_total': importe_total,
                },
                'detalles': detalles
            }
            return items
        except Exception as e:
            print(f"Error al procesar el archivo XML: {e}")
        return items



# class XML:
#     def __init__(self):
#         self.parsers = {
#             "2.1.0": self._parse_common,
#             "1.1.0": self._parse_common,
#         }
#
#     def read(self, path=''):
#         """Lee el archivo XML y lo procesa según su versión."""
#         try:
#             root = ElementTree.parse(path).getroot()
#             version = root.attrib.get('version')
#
#             if version in self.parsers:
#                 return self.parsers[version](root)
#             else:
#                 raise ValueError(f"Versión de XML no soportada: {version}")
#         except ElementTree.ParseError as e:
#             raise ValueError(f"Error al analizar el XML: {str(e)}")
#         except Exception as e:
#             raise ValueError(f"Error desconocido: {str(e)}")
#
#     def _parse_common(self, root):
#         """Procesa XML con estructura común entre versiones."""
#         try:
#             # Extraer toda la información tributaria
#             info_tributaria = root.find('infoTributaria')
#             if info_tributaria is None:
#                 raise ValueError("No se encontró el nodo 'infoTributaria' en el XML.")
#
#             info_tributaria_data = {
#                 child.tag: child.text for child in info_tributaria
#             }
#
#             # Extraer información de la factura (si está presente)
#             info_factura = root.find('infoFactura')
#             info_factura_data = {
#                 child.tag: child.text for child in info_factura
#             } if info_factura is not None else {}
#
#             # Extraer detalles (si están presentes)
#             detalles = [
#                 {
#                     child.tag: child.text for child in detalle
#                 } for detalle in root.find('detalles').findall('detalle')
#             ] if root.find('detalles') is not None else []
#
#             return {
#                 'info_tributaria': info_tributaria_data,
#                 'info_factura': info_factura_data,
#                 'detalles': detalles,
#             }
#         except AttributeError as e:
#             raise ValueError(f"Error al procesar XML: {str(e)}")
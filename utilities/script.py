import json
import requests


class SRI(object):
    def __init__(self):
        self.authorization = None
        self.session = requests.Session()
        self.end_point = 'https://srienlinea.sri.gob.ec'
        self.end_point_rest = f'{self.end_point}/sri-catastro-sujeto-servicio-internet/rest'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0'
        }

    def exists_ruc(self, ruc) -> bool:
        url = f'{self.end_point_rest}/ConsolidadoContribuyente/existePorNumeroRuc?numeroRuc={ruc}'
        response = requests.get(url, headers=self.headers)
        if response.ok:
            return response.text == 'true'
        else:
            response.raise_for_status()
        return False

    def generate_authorization(self):
        url = f'{self.end_point}/sri-captcha-servicio-internet/captcha/start/1'
        response = self.session.get(url, headers=self.headers)
        if response.ok:
            tmp = json.loads(response.content.decode('utf-8'))
            if 'values' in tmp:
                values = tmp['values']
                if isinstance(values, list):
                    for value in values:
                        url = f'{self.end_point}/sri-captcha-servicio-internet/rest/ValidacionCaptcha/validarCaptcha/{value}?emitirToken=true'
                        response = self.session.get(url, headers=self.headers)
                        if response.ok:
                            data2 = json.loads(response.content.decode('utf-8'))
                            return data2.get('mensaje')
                        else:
                            response.raise_for_status()
        else:
            response.raise_for_status()
        return False

    def lookup_ruc(self, ruc):
        """
        Consulta la información de un único RUC en el SRI.
        """
        for ruc in [ruc]:  # 👈 aquí está la adaptación que pediste
            try:
                if not self.exists_ruc(ruc):
                    return {
                        'exception': None,
                        'reason': None,
                        'data': {'message': 'La búsqueda no generó resultados.'}
                    }

                if not self.authorization:
                    self.authorization = self.generate_authorization()

                data, reason = {}, None
                if self.authorization:
                    url = f'{self.end_point_rest}/ConsolidadoContribuyente/obtenerPorNumerosRuc?&ruc={ruc}'
                    headers2 = self.headers.copy()
                    headers2.update({'accept': 'application/json', 'Authorization': self.authorization})
                    response = self.session.get(url, headers=headers2)
                    if response.ok:
                        tmp = response.json()
                        if isinstance(tmp, list):
                            for element in tmp:
                                if isinstance(element, dict):
                                    data.update(element)

                        # Consultar establecimientos
                        url = f'{self.end_point_rest}/Establecimiento/consultarPorNumeroRuc?numeroRuc={ruc}'
                        response = self.session.get(url, headers=headers2)
                        if response.ok and response.status_code == 200:
                            data.update({'establecimientos': response.json()})
                        else:
                            response.raise_for_status()
                    else:
                        response.raise_for_status()
                else:
                    reason = 'Servicio temporalmente no disponible'
                    data.update({'message': reason})

                return {'exception': None, 'reason': reason, 'data': data}

            except Exception as err:
                return {
                    'exception': err.__class__.__name__,
                    'reason': str(err),
                    'data': {'message': 'Error por parte del SRI al consultar la información'}
                }

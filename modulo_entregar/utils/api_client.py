import requests
import logging
import base64

_logger = logging.getLogger(__name__)

class LogisticsAPIClient:
    BASE_URL = "https://homologacion.entregarweb.com/api/v1"
    TOKEN_ENDPOINT = "/auth/token"

    def __init__(self):
        self.client_api = "d3df1f7c082d1ade94f42caabe24a70b9fc0dbfacc418aa07fbfb1c09bbe8d13"
        self.client_secret = "c017662e88c5c68f4add11f5cf932d289166316e5980338284b11608f06dc744"
        self.api_token = None
        self.expiration = None

    # ------------------------------------------
    # 1. Autenticación - POST /auth/token
    # ------------------------------------------
    def authenticate(self):
        url = f"{self.BASE_URL}{self.TOKEN_ENDPOINT}"
        payload = {
            'client_api': self.client_api,
            'client_secret': self.client_secret
        }

        try:
            response = requests.post(url, data=payload)
            response.raise_for_status()
            data = response.json()

            if data.get('status') and data.get('result'):
                token_data = data['result'][0]
                self.api_token = token_data['api_token']
                self.expiration = token_data['api_expire_in']
                _logger.info("Token obtenido correctamente.")
            else:
                _logger.error("Error en autenticación: %s", data.get('msg'))
        except requests.RequestException as e:
            _logger.exception("Fallo en autenticación: %s", str(e))

    # ------------------------------------------
    # 2. Estimar precio - POST /shipping/price
    # ------------------------------------------
    def get_shipping_price(self, postal_code, items):
        if not self.api_token:
            self.authenticate()

        url = f"{self.BASE_URL}/shipping/price"
        headers = {'Authorization': f'Bearer {self.api_token}'}
        payload = {
            'postal_code': postal_code,
            'items': str(items)
        }

        try:
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status()
            data = response.json()

            if data.get("status") and data.get("result"):
                return data["result"][0]["price"]
            else:
                _logger.error("Error al obtener precio: %s", data.get("msg"))
        except requests.RequestException as e:
            _logger.exception("Error en consulta de precio: %s", str(e))

        return None

    # ------------------------------------------
    # 3. Obtener geolocalización - POST /shipping/geolocation
    # ------------------------------------------
    def get_geolocation(self, postal_code, address, location):
        if not self.api_token:
            self.authenticate()

        url = f"{self.BASE_URL}/shipping/geolocation"
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        payload = {
            'postal_code': postal_code,
            'address': address,
            'location': location
        }

        try:
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status()
            data = response.json()

            if data.get("status") and data.get("result"):
                geo = data["result"][0]
                if geo.get("status"):
                    return {
                        "lat": geo["lat"],
                        "lng": geo["lng"],
                        "direccion_completa": geo.get("address")
                    }
        except requests.RequestException as e:
            _logger.exception("Fallo en consulta de geolocalización: %s", str(e))

        return None

    # ------------------------------------------
    # 4. Crear envío - POST /shipping/new
    # ------------------------------------------
    def create_shipment(self, shipment_data):
        if not self.api_token:
            self.authenticate()

        url = f"{self.BASE_URL}/shipping/new"
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        try:
            response = requests.post(url, headers=headers, data=shipment_data)
            response.raise_for_status()
            data = response.json()

            if data.get("status") and data.get("result"):
                return data["result"][0]
            else:
                _logger.error("Error en creación de envío: %s", data.get("msg"))
        except requests.RequestException as e:
            _logger.exception("Fallo al crear envío: %s", str(e))

        return None

    # ------------------------------------------
    # 5. Ver estado de envío - GET /shipping/state/{code}
    # ------------------------------------------
    def get_shipment_status(self, code):
        if not self.api_token:
            self.authenticate()

        url = f"{self.BASE_URL}/shipping/state/{code}"
        headers = {'Authorization': f'Bearer {self.api_token}'}

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            if data.get("status") and data.get("result"):
                return data["result"][0]
            else:
                _logger.warning("No se encontró el envío con código %s", code)
        except requests.RequestException as e:
            _logger.exception("Error al obtener estado del envío: %s", str(e))

        return None

    # ------------------------------------------
    # 6. Obtener etiqueta PDF - GET /shipping/print/label/{code}
    # ------------------------------------------
    def get_shipping_label(self, code):
        if not self.api_token:
            self.authenticate()

        url = f"{self.BASE_URL}/shipping/print/label/{code}"
        headers = {'Authorization': f'Bearer {self.api_token}'}

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.content  # Bytes del PDF
        except requests.RequestException as e:
            _logger.exception("Error al descargar etiqueta PDF: %s", str(e))

        return None

    # ------------------------------------------
    # 7. Obtener provincias - GET /shipping/provincias
    # ------------------------------------------
    def get_provinces(self):
        if not self.api_token:
            self.authenticate()

        url = f"{self.BASE_URL}/shipping/provincias"
        headers = {'Authorization': f'Bearer {self.api_token}'}

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            if data.get("status") and data.get("result"):
                return data["result"][0]
        except requests.RequestException as e:
            _logger.exception("Error al obtener provincias: %s", str(e))

        return []

    # ------------------------------------------
    # 8. Obtener historial - GET /shipping/historial/{code}
    # ------------------------------------------
    def get_tracking_history(self, code):
        if not self.api_token:
            self.authenticate()

        url = f"{self.BASE_URL}/shipping/historial/{code}"
        headers = {'Authorization': f'Bearer {self.api_token}'}

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            if data.get("status") and data.get("result"):
                return data["result"]
        except requests.RequestException as e:
            _logger.exception("Error al consultar historial del envío: %s", str(e))

        return []

    # ------------------------------------------
    # 9. Obtener estados posibles - GET /shipping/get_states
    # ------------------------------------------
    def get_available_statuses(self):
        if not self.api_token:
            self.authenticate()

        url = f"{self.BASE_URL}/shipping/get_states"
        headers = {'Authorization': f'Bearer {self.api_token}'}

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            if data.get("status") and data.get("result"):
                return data["result"]
        except requests.RequestException as e:
            _logger.exception("Error al obtener estados posibles: %s", str(e))

        return []

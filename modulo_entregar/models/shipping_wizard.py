from odoo import models, fields, api
from odoo.exceptions import UserError
from ..utils.api_client import LogisticsAPIClient

class ShippingWizard(models.TransientModel):
    _name = 'shipping.wizard'
    _description = 'Asistente para creación de envío logístico'

    receives = fields.Char("Receptor", required=True)
    address = fields.Char("Dirección", required=True)
    location = fields.Char("Localidad", required=True)
    postal_code = fields.Char("Código Postal", required=True)
    reference = fields.Char("Referencia")
    province_id = fields.Integer("ID Provincia")
    items = fields.Char("Items (formato: peso,alto,largo,ancho)", required=True)
    telephone = fields.Char("Teléfono")
    email = fields.Char("Email")
    external_reference = fields.Char("Referencia externa")
    bultos = fields.Integer("Cantidad de bultos", default=1)

    lat = fields.Float("Latitud")
    lng = fields.Float("Longitud")
    envio_code = fields.Char("Código de envío generado")

    def action_obtener_geolocalizacion(self):
        client = LogisticsAPIClient()
        geo = client.get_geolocation(self.postal_code, self.address, self.location)
        if not geo:
            raise UserError("No se pudo obtener la geolocalización.")
        self.lat = geo["lat"]
        self.lng = geo["lng"]

    def action_crear_envio(self):
        if not self.lat or not self.lng:
            raise UserError("Primero debe obtener la geolocalización.")

        client = LogisticsAPIClient()

        shipment_data = {
            'receives': self.receives,
            'address': self.address,
            'location': self.location,
            'reference': self.reference or '',
            'postal_code': self.postal_code,
            'items': f'["{self.items}"]',
            'lat': str(self.lat),
            'lng': str(self.lng),
            'provincia': str(self.province_id or 1),
            'telephone': self.telephone or '',
            'email': self.email or '',
            'external_reference': self.external_reference or '',
            'bultos': str(self.bultos or 1),
        }

        code = client.create_shipment(shipment_data)
        if not code:
            raise UserError("No se pudo crear el envío.")
        self.envio_code = code

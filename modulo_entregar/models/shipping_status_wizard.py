from odoo import models, fields
from odoo.exceptions import UserError
from ..utils.api_client import LogisticsAPIClient

class ShippingStatusWizard(models.TransientModel):
    _name = 'shipping.status.wizard'
    _description = 'Consultar estado de envío logístico'

    code = fields.Char("Código de Envío", required=True)

    # Campos de solo lectura que se llenan automáticamente
    receives = fields.Char("Receptor", readonly=True)
    address = fields.Char("Dirección", readonly=True)
    location = fields.Char("Localidad", readonly=True)
    postal_code = fields.Char("Código Postal", readonly=True)
    bultos = fields.Integer("Bultos", readonly=True)
    state = fields.Char("Estado", readonly=True)
    date = fields.Datetime("Fecha de creación", readonly=True)

    def action_consultar_estado(self):
        client = LogisticsAPIClient()
        result = client.get_shipment_status(self.code)
        if not result:
            raise UserError("No se encontró el envío o hubo un error.")

        self.receives = result.get("receives")
        self.address = result.get("address")
        self.location = result.get("location")
        self.postal_code = result.get("postal_code")
        self.bultos = result.get("bultos")
        self.state = result.get("state")
        self.date = result.get("date", {}).get("date")

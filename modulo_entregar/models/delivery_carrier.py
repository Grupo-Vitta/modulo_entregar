from odoo import models, fields, api
from odoo.exceptions import UserError
from ..utils.api_client import LogisticsAPIClient

class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(selection_add=[('logistics_api', "Logística Externa")])
    fixed_postal_code = fields.Char("Código Postal base (para pruebas)", default="B1653")

    def logistics_rate_shipment(self, order):
        self.ensure_one()
        if self.delivery_type != 'logistics_api':
            return super().rate_shipment(order)

        client = LogisticsAPIClient()

        postal_code = self.fixed_postal_code or order.partner_shipping_id.zip
        if not postal_code:
            raise UserError("El cliente no tiene código postal definido.")

        items = []
        for line in order.order_line.filtered(lambda l: not l.is_delivery and l.product_id.type in ['product', 'consu']):
            qty = int(line.product_uom_qty)
            weight = line.product_id.weight or 1.0
            height = line.product_id.height or 10.0
            width = line.product_id.width or 10.0
            length = line.product_id.length or 10.0
            items.append(f"{qty},{weight},{height},{length}")

        if not items:
            raise UserError("No hay productos físicos para calcular el envío.")

        items_str = "[" + ",".join(f'"{item}"' for item in items) + "]"

        price = client.get_shipping_price(postal_code, items_str)
        if price is None:
            raise UserError("No se pudo calcular el precio del envío desde la API logística.")

        return {
            'success': True,
            'price': price,
            'error_message': False,
            'warning_message': False
        }

    def logistics_send_shipping(self, pickings):
        self.ensure_one()
        if self.delivery_type != 'logistics_api':
            return super().send_shipping(pickings)

        client = LogisticsAPIClient()
        result = []

        for picking in pickings:
            partner = picking.partner_id

            if not partner.zip or not partner.street or not partner.city:
                raise UserError("El cliente no tiene dirección completa definida.")

            geo = client.get_geolocation(partner.zip, partner.street, partner.city)
            if not geo:
                raise UserError("No se pudo obtener la geolocalización del cliente.")

            items = []
            for move in picking.move_lines.filtered(lambda l: l.product_id.type in ['product', 'consu']):
                qty = int(move.product_uom_qty)
                weight = move.product_id.weight or 1.0
                height = move.product_id.height or 10.0
                width = move.product_id.width or 10.0
                length = move.product_id.length or 10.0
                items.append(f"{qty},{weight},{height},{length}")

            if not items:
                raise UserError("No hay productos físicos para enviar.")

            items_str = "[" + ",".join(f'"{item}"' for item in items) + "]"

            shipment_data = {
                'receives': partner.name,
                'address': partner.street or '',
                'location': partner.city or '',
                'reference': partner.street2 or '',
                'postal_code': partner.zip,
                'items': items_str,
                'lat': str(geo["lat"]),
                'lng': str(geo["lng"]),
                'provincia': '1',
                'telephone': partner.phone or '',
                'email': partner.email or '',
                'external_reference': str(picking.id),
                'bultos': '1',
            }

            code = client.create_shipment(shipment_data)
            if not code:
                raise UserError("No se pudo generar el envío en la API externa.")

            picking.carrier_tracking_ref = code
            result.append({
                'exact_price': 0.0,
                'tracking_number': code
            })

        return result


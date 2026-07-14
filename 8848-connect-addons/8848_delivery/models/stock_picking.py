from odoo import models, fields

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    route_id = fields.Many2one('8848.delivery.route', string='Delivery Route', copy=False)
    proof_of_delivery_image = fields.Image(string='Proof of Delivery (Photo)', copy=False)
    customer_signature = fields.Image(string='Customer Signature', copy=False)
    gps_coordinates = fields.Char(string='GPS Coordinates', copy=False, help="Captured automatically by driver app upon delivery.")

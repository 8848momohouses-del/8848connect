from odoo import models, fields, api, _

class DeliveryRoute(models.Model):
    _name = '8848.delivery.route'
    _table = 'connect_delivery_route'
    _description = 'Delivery Route'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(string='Route Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    date = fields.Date(string='Date', required=True, default=fields.Date.context_today, tracking=True)
    driver_id = fields.Many2one('hr.employee', string='Driver', domain=[('is_driver', '=', True)], tracking=True)
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle', tracking=True)
    picking_ids = fields.One2many('stock.picking', 'route_id', string='Deliveries', domain=[('picking_type_code', '=', 'outgoing')])
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_transit', 'In Transit'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('8848.delivery.route') or _('New')
        return super().create(vals_list)

    def action_start_route(self):
        for route in self:
            route.state = 'in_transit'

    def action_done(self):
        for route in self:
            route.state = 'done'
            for picking in route.picking_ids.filtered(lambda p: p.state not in ['done', 'cancel']):
                picking.button_validate()

    def action_cancel(self):
        for route in self:
            route.state = 'cancelled'

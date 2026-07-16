from odoo import models, fields, api, _

class DeliveryRoute(models.Model):
    _name = '8848.delivery.route'
    _table = 'connect_delivery_route'
    _description = 'Delivery Route'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(string='Route Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    date = fields.Date(string='Date', required=True, default=fields.Date.context_today, tracking=True)
    driver_id = fields.Many2one('res.users', string='Driver')
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle')
    
    # Proof of Delivery fields
    recipient_name = fields.Char(string='Recipient Name', copy=False, tracking=True)
    delivered_at = fields.Datetime(string='Delivered At', copy=False, tracking=True)
    failed_delivery_reason = fields.Char(string='Failed Reason', copy=False, tracking=True)
    delivery_notes = fields.Text(string='Delivery Notes', copy=False)
    delivery_photo = fields.Binary(string='Delivery Photo', copy=False, attachment=True)
    delivery_signature = fields.Binary(string='Delivery Signature', copy=False, attachment=True)
    delivery_latitude = fields.Float(string='Latitude', digits=(10, 7), copy=False)
    delivery_longitude = fields.Float(string='Longitude', digits=(10, 7), copy=False)
    
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
            self.write({'state': 'in_transit'})
        
        # Dispatch notification
        for route in self:
            channel = self.env['8848.communication.channel'].search([('code', '=', 'portal')], limit=1)
            if channel:
                for picking in route.picking_ids:
                    if picking.partner_id:
                        self.env['8848.communication.message'].sudo().create({
                            'res_model': route._name,
                            'res_id': route.id,
                            'partner_id': picking.partner_id.id,
                            'channel_id': channel.id,
                            'subject': f"Delivery {route.name} Dispatched",
                            'body': f"<p>Your delivery is on its way with driver {route.driver_id.name or 'assigned'}.</p>",
                            'status': 'queued',
                        })

    def action_done(self):
        for route in self:
            route.state = 'done'
            for picking in route.picking_ids.filtered(lambda p: p.state not in ['done', 'cancel']):
                picking.button_validate()
                
            # Completion notification
            channel = self.env['8848.communication.channel'].search([('code', '=', 'portal')], limit=1)
            if channel:
                for picking in route.picking_ids:
                    if picking.partner_id:
                        self.env['8848.communication.message'].sudo().create({
                            'res_model': route._name,
                            'res_id': route.id,
                            'partner_id': picking.partner_id.id,
                            'channel_id': channel.id,
                            'subject': f"Delivery {route.name} Completed",
                            'body': f"<p>Your delivery has been marked as complete.</p>",
                            'status': 'queued',
                        })

    def action_cancel(self):
        for route in self:
            route.state = 'cancelled'

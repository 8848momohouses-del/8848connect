from odoo import models, fields, api, exceptions, _

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    packing_status = fields.Selection([
        ('pending', 'Pending Packing'),
        ('packing', 'Packing in Progress'),
        ('packed', 'Packed')
    ], string='Packing Status', default='pending', copy=False, tracking=True)

    packed_by = fields.Many2one('res.users', string='Packed By', copy=False, tracking=True)
    packing_started_at = fields.Datetime(string='Packing Started At', copy=False, readonly=True)
    packed_at = fields.Datetime(string='Packed At', copy=False, readonly=True)
    package_count = fields.Integer(string='Package Count', default=0, copy=False)
    packing_notes = fields.Text(string='Packing Notes', copy=False)

    def action_start_packing(self):
        for picking in self:
            if picking.state not in ['assigned']:
                raise exceptions.UserError(_("Can only start packing on ready pickings."))
            picking.write({
                'packing_status': 'packing',
                'packing_started_at': fields.Datetime.now()
            })

    def action_finish_packing(self):
        for picking in self:
            if picking.packing_status != 'packing':
                raise exceptions.UserError(_("Must start packing first."))
            
            picking.write({
                'packing_status': 'packed',
                'packed_by': self.env.user.id,
                'packed_at': fields.Datetime.now()
            })
            
            # Queue notification
            channel = self.env['8848.communication.channel'].search([('code', '=', 'portal')], limit=1)
            if channel and picking.partner_id:
                self.env['8848.communication.message'].sudo().create({
                    'res_model': picking._name,
                    'res_id': picking.id,
                    'partner_id': picking.partner_id.id,
                    'channel_id': channel.id,
                    'subject': f"Order {picking.origin or picking.name} Packed",
                    'body': f"<p>Your order {picking.origin or picking.name} has been packed.</p>",
                    'status': 'queued',
                })

    def button_validate(self):
        for picking in self:
            if picking.picking_type_code == 'outgoing':
                if picking.packing_status != 'packed':
                    raise exceptions.UserError(_("You must complete the packing process before validating this outgoing shipment."))
        return super(StockPicking, self).button_validate()

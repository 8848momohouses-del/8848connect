from odoo import models, fields, api, exceptions, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    approval_state = fields.Selection([
        ('draft', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='8848 Approval State', default='draft', copy=False, required=True, tracking=True)

    approved_by = fields.Many2one('res.users', string='Approved By', copy=False, readonly=True)
    approved_at = fields.Datetime(string='Approved At', copy=False, readonly=True)

    fulfilment_state = fields.Selection([
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('ready', 'Ready'),
        ('packed', 'Packed'),
        ('dispatched', 'Dispatched'),
        ('delivered', 'Delivered'),
        ('exception', 'Exception')
    ], string='Fulfilment State', default='pending', copy=False, tracking=True)

    def action_approve_order(self):
        self.ensure_one()
        if not self.env.user.has_group('8848_security.group_8848_operations_manager') and not self.env.user.has_group('sales_team.group_sale_manager'):
            raise exceptions.AccessError(_("You do not have permission to approve franchise orders."))
        
        if not self.partner_id:
            raise exceptions.UserError(_("No customer selected on the order."))

        if self.partner_id.is_franchise:
            # We must use safe access or ensure franchise_stage_id exists
            if self.partner_id.franchise_stage_id and self.partner_id.franchise_stage_id.code != 'operational':
                raise exceptions.UserError(_("This franchise is not in the 'Operational' stage. Approval blocked."))

        # Check for insufficient stock and warn, but don't strictly block approval.
        # This explicitly shows insufficient stock state.
        for line in self.order_line:
            if line.product_id.is_storable and line.product_uom_qty > line.product_id.virtual_available:
                # We can choose to block or just let the standard Odoo warning show up in the UI.
                # The prompt asks: "insufficient stock is clearly shown; partial availability is supported"
                # If we raise an error, they can't approve it. So let's just log a message in chatter instead.
                self.message_post(body=_("Approval Note: Insufficient stock for %s. Ordered: %s, Available: %s") % (
                    line.product_id.display_name, line.product_uom_qty, line.product_id.virtual_available
                ))

        self.write({
            'approval_state': 'approved',
            'approved_by': self.env.user.id,
            'approved_at': fields.Datetime.now()
        })
        
        # Queue notification
        channel = self.env['8848.communication.channel'].search([('code', '=', 'portal')], limit=1)
        if channel and self.partner_id:
            self.env['8848.communication.message'].sudo().create({
                'res_model': self._name,
                'res_id': self.id,
                'partner_id': self.partner_id.id,
                'channel_id': channel.id,
                'subject': f"Order {self.name} Approved",
                'body': f"<p>Your order {self.name} has been approved and is being processed.</p>",
                'status': 'queued',
            })

    def action_reject_order(self):
        self.ensure_one()
        if not self.env.user.has_group('8848_security.group_8848_operations_manager') and not self.env.user.has_group('sales_team.group_sale_manager'):
            raise exceptions.AccessError(_("You do not have permission to reject franchise orders."))
        self.write({
            'approval_state': 'rejected'
        })

    def action_confirm(self):
        for order in self:
            if order.approval_state != 'approved':
                raise exceptions.UserError(_("Order %s must be approved before it can be confirmed.") % order.name)
        return super(SaleOrder, self).action_confirm()

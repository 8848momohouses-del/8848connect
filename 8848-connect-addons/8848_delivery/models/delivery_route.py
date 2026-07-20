from odoo import models, fields, api, exceptions, _

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

    # Invoicing Fields
    invoice_status = fields.Selection([
        ('not_ready', 'Not Ready'),
        ('pending', 'Pending'),
        ('created', 'Created'),
        ('failed', 'Failed')
    ], string='Invoice Status', default='not_ready', required=True)
    invoice_attempt_count = fields.Integer(string='Invoice Attempt Count', default=0)
    last_invoice_error = fields.Text(string='Last Invoice Error')
    
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
            # First pass: Check all pickings for recorded quantities
            pending_pickings = route.picking_ids.filtered(lambda p: p.state not in ['done', 'cancel'])
            for picking in pending_pickings:
                if not any(move.quantity > 0 for move in picking.move_ids):
                    raise exceptions.UserError(_(
                        "Picking %s has no processed quantities. "
                        "You must explicitly record delivered quantities or cancel the picking to complete the route."
                    ) % picking.name)

            # Second pass: Validate pickings and handle wizards
            for picking in pending_pickings:
                res = picking.button_validate()
                
                # If a wizard is returned, intercept and process it automatically
                if isinstance(res, dict) and res.get('res_model') == 'stock.backorder.confirmation':
                    wizard = self.env['stock.backorder.confirmation'].with_context(res.get('context', {})).create({})
                    wizard.process()
                elif isinstance(res, dict) and res.get('res_model') == 'stock.immediate.transfer':
                    wizard = self.env['stock.immediate.transfer'].with_context(res.get('context', {})).create({})
                    wizard.process()
                elif isinstance(res, dict):
                    # Unhandled wizard, fail safely
                    raise exceptions.UserError(_("Unhandled validation wizard for %s. Please validate manually.") % picking.name)

            # Final check: Ensure all pickings reached a terminal state
            if any(p.state not in ['done', 'cancel'] for p in route.picking_ids):
                raise exceptions.UserError(_("Cannot complete route: not all pickings reached a terminal state (done/cancel)."))

            route.state = 'done'
            
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
            
            # Trigger initial invoice attempt
            route.invoice_status = 'pending'
            route.action_retry_invoice()

    def action_retry_invoice(self):
        if not (self.env.user.has_group('8848_security.group_8848_acc_manager') or self.env.user.has_group('8848_security.group_8848_ops_manager') or self.env.user.has_group('account.group_account_manager')):
            raise exceptions.AccessError(_("Only Accounts or Operations Managers can retry invoice generation."))
            
        for route in self:
            if route.invoice_status == 'created':
                continue
                
            route.invoice_attempt_count += 1
            success = True
            
            for picking in route.picking_ids:
                if hasattr(picking, 'sale_id') and picking.sale_id:
                    try:
                        # Idempotent: _create_invoices does not duplicate existing invoices for delivered quantities
                        picking.sale_id._create_invoices()
                    except Exception as e:
                        success = False
                        route.last_invoice_error = str(e)
                        route.message_post(body=f"Failed to create invoice for {picking.name}: {str(e)}")
                        
            if success:
                route.invoice_status = 'created'
                route.last_invoice_error = False
            else:
                route.invoice_status = 'failed'

    def unlink(self):
        for route in self:
            if route.state == 'done':
                if not self.env.user.has_group('base.group_system'):
                    raise exceptions.AccessError(_("Completed delivery routes cannot be deleted by ordinary users."))
        return super().unlink()

    def action_cancel(self):
        for route in self:
            route.state = 'cancelled'

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class RoyaltyStatement(models.Model):
    _name = '8848.royalty.statement'
    _table = 'connect_royalty_statement'
    _description = 'Franchise Royalty Statement'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    franchise_id = fields.Many2one('res.partner', string='Franchise', required=True, domain=[('is_franchise', '=', True)], tracking=True)
    date_start = fields.Date(string='Period Start', required=True, tracking=True)
    date_end = fields.Date(string='Period End', required=True, tracking=True)
    total_sales = fields.Monetary(string='Total Sales', required=True, tracking=True)
    royalty_percentage = fields.Float(string='Royalty (%)', related='franchise_id.royalty_percentage', readonly=True)
    royalty_amount = fields.Monetary(string='Royalty Amount', compute='_compute_royalty_amount', store=True, tracking=True)
    currency_id = fields.Many2one('res.currency', related='franchise_id.currency_id', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('invoiced', 'Invoiced'),
        ('paid', 'Paid'),
    ], string='Status', default='draft', tracking=True)
    
    invoice_id = fields.Many2one('account.move', string='Invoice', readonly=True, copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('8848.royalty.statement') or _('New')
        return super().create(vals_list)

    @api.depends('total_sales', 'royalty_percentage')
    def _compute_royalty_amount(self):
        for record in self:
            record.royalty_amount = (record.total_sales * record.royalty_percentage) / 100.0

    def action_generate_invoice(self):
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_("You can only generate an invoice for statements in draft state."))
        
        # Create invoice
        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.franchise_id.id,
            'invoice_date': fields.Date.context_today(self),
            'currency_id': self.currency_id.id or self.company_id.currency_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': _('Royalty Fee for %s to %s') % (self.date_start, self.date_end),
                'quantity': 1,
                'price_unit': self.royalty_amount,
            })],
        }
        invoice = self.env['account.move'].create(invoice_vals)
        self.write({
            'invoice_id': invoice.id,
            'state': 'invoiced',
        })
        
        # Return action to open the newly created invoice
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'view_mode': 'form',
            'target': 'current',
        }

from odoo import api, fields, models

class FranchiseApplication(models.Model):
    _name = '8848.franchise.application'
    _description = 'Franchise Application Details'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Application Reference', required=True, copy=False, readonly=True, default='New')
    lead_id = fields.Many2one('crm.lead', string='CRM Lead', ondelete='cascade', tracking=True)
    partner_id = fields.Many2one('res.partner', string='Linked Partner', help='Populated when converted to an operational franchise.', tracking=True)
    
    version = fields.Integer(string='Version', default=1, readonly=True)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Status', default='draft', tracking=True)

    submission_date = fields.Datetime(string='Submission Date', readonly=True)

    # Application Fields
    business_experience = fields.Text(string='Business Experience')
    hospitality_experience = fields.Boolean(string='Has Hospitality Experience', default=False)
    total_assets = fields.Float(string='Total Assets')
    investment_available = fields.Float(string='Investment Available')
    finance_required = fields.Boolean(string='Finance Required', default=False)
    partnership_details = fields.Text(string='Partnership Details')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('8848.franchise.application') or 'APP-NEW'
        return super().create(vals_list)

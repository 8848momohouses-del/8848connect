from odoo import api, fields, models

class CrmLead(models.Model):
    _name = 'crm.lead'
    _inherit = ['crm.lead', '8848.communication.mixin']

    enquiry_reference = fields.Char(string='Enquiry Reference', readonly=True, copy=False, index=True)
    franchise_territory_interest = fields.Char(string='Preferred Territory')
    
    application_ids = fields.One2many('8848.franchise.application', 'lead_id', string='Applications')
    active_application_id = fields.Many2one(
        '8848.franchise.application', 
        string='Active Application',
        compute='_compute_active_application',
        store=True
    )
    
    franchise_score = fields.Integer(string='Franchise Score', readonly=True)
    franchise_score_category = fields.Selection([
        ('hot', 'Hot'),
        ('warm', 'Warm'),
        ('cold', 'Cold')
    ], string='Score Category', compute='_compute_franchise_score_category', store=True)

    external_entry_id = fields.Char(string='External Entry ID', help='e.g. Gravity Forms Entry ID', copy=False, index=True)
    marketing_consent = fields.Boolean(string='Marketing Consent', default=False)
    privacy_consent = fields.Boolean(string='Privacy Consent', default=False)

    @api.depends('application_ids', 'application_ids.status')
    def _compute_active_application(self):
        for lead in self:
            # Pick the most recently submitted/approved application, or just the last one created.
            apps = lead.application_ids.sorted(key=lambda a: a.create_date, reverse=True)
            lead.active_application_id = apps[0].id if apps else False

    @api.depends('franchise_score')
    def _compute_franchise_score_category(self):
        hot_threshold = int(self.env['ir.config_parameter'].sudo().get_param('8848_crm.hot_score_threshold', 80))
        for lead in self:
            if lead.franchise_score >= hot_threshold:
                lead.franchise_score_category = 'hot'
            elif lead.franchise_score >= (hot_threshold - 30):
                lead.franchise_score_category = 'warm'
            else:
                lead.franchise_score_category = 'cold'

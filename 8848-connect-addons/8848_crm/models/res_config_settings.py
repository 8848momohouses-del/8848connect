from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    franchise_default_team_id = fields.Many2one(
        'crm.team',
        string='Default Franchise Sales Team',
        config_parameter='8848_crm.default_team_id',
        help='Default sales team for incoming franchise enquiries.'
    )
    
    franchise_default_user_id = fields.Many2one(
        'res.users',
        string='Default Franchise Salesperson',
        config_parameter='8848_crm.default_user_id',
        help='Default salesperson for incoming franchise enquiries.'
    )
    
    franchise_ack_template_id = fields.Many2one(
        '8848.communication.template',
        string='Acknowledgement Template',
        config_parameter='8848_crm.ack_template_id',
        help='Communication template used to acknowledge receipt of an enquiry.'
    )

    franchise_brochure_attachment_id = fields.Many2one(
        'ir.attachment',
        string='Franchise Brochure',
        config_parameter='8848_crm.brochure_attachment_id',
        help='The brochure attachment to include in the acknowledgement email.'
    )

    franchise_hot_score_threshold = fields.Integer(
        string='Hot Lead Score Threshold',
        default=80,
        config_parameter='8848_crm.hot_score_threshold',
        help='Leads with a score equal to or above this are categorised as Hot.'
    )

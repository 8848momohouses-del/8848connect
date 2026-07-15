from odoo import api, fields, models


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', '8848.workflow.mixin']

    is_franchise = fields.Boolean(string='Is a Franchise', default=False)
    store_id = fields.Char(string='Store ID', help='Unique identifier for the franchise store')
    royalty_percentage = fields.Float(string='Royalty (%)', default=5.0)
    marketing_fee_percentage = fields.Float(string='Marketing Fee (%)', default=2.0)
    territory = fields.Char(string='Territory', help='Geographical territory assigned to this franchise')
    franchise_status = fields.Selection([
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('terminated', 'Terminated'),
    ], string='Franchise Status', default='active', tracking=True)

    # --- Lifecycle (Franchise Core v2) ------------------------------------
    # One Franchise. One Record. One Source of Truth: the same partner record
    # advances through the whole lifecycle; every stage change is tracked in
    # the chatter and becomes permanent franchise history.
    franchise_stage_id = fields.Many2one(
        '8848.franchise.stage', string='Lifecycle Stage',
        tracking=True, index=True, copy=False,
        group_expand='_read_group_franchise_stage')
    franchise_approved = fields.Boolean(
        string='Franchise Approved', tracking=True, copy=False,
        help='Management has approved this candidate as a franchisee.')

    enquiry_date = fields.Date(string='Enquiry Date', copy=False)
    application_date = fields.Date(string='Application Date', copy=False)
    agreement_signed_date = fields.Date(
        string='Agreement Signed', tracking=True, copy=False)
    deposit_received_date = fields.Date(
        string='Deposit Received', tracking=True, copy=False)
    training_completed_date = fields.Date(string='Training Completed', copy=False)
    grand_opening_date = fields.Date(
        string='Grand Opening', tracking=True, copy=False)
    renewal_date = fields.Date(string='Renewal Date', copy=False)

    is_operational = fields.Boolean(
        string='Operational', compute='_compute_is_operational', store=True,
        help='True once the franchise is approved, the agreement is signed, '
             'the deposit is received and the grand opening is completed. '
             'Gates portal activation and operational features.')

    @api.depends('franchise_approved', 'agreement_signed_date',
                 'deposit_received_date', 'grand_opening_date')
    def _compute_is_operational(self):
        for partner in self:
            partner.is_operational = bool(
                partner.franchise_approved
                and partner.agreement_signed_date
                and partner.deposit_received_date
                and partner.grand_opening_date
            )

    @api.model
    def _read_group_franchise_stage(self, stages, domain):
        # Show every lifecycle stage as a kanban column, even when empty.
        return stages.search([], order=stages._order)

    def _default_franchise_stage(self):
        # A record created in the backend is at least an enquiry ("Website
        # Visitor" is the pre-record web stage). Fall back to the first stage
        # if the seeded record was removed or renamed by the administrator.
        stage = self.env.ref('8848_franchise.stage_franchise_inquiry',
                             raise_if_not_found=False)
        if not stage:
            stage = self.env['8848.franchise.stage'].search(
                [], order='sequence, id', limit=1)
        return stage

    @api.model_create_multi
    def create(self, vals_list):
        first_stage = None
        for vals in vals_list:
            if vals.get('is_franchise') and not vals.get('franchise_stage_id'):
                if first_stage is None:
                    first_stage = self._default_franchise_stage()
                if first_stage:
                    vals['franchise_stage_id'] = first_stage.id
        return super().create(vals_list)

    def write(self, vals):
        res = super().write(vals)
        if vals.get('is_franchise'):
            missing_stage = self.filtered(
                lambda p: p.is_franchise and not p.franchise_stage_id)
            if missing_stage:
                first_stage = self._default_franchise_stage()
                if first_stage:
                    missing_stage.franchise_stage_id = first_stage
        return res

    def action_start_franchise_approval(self):
        """Starts the Franchise Approval Workflow"""
        for partner in self:
            partner.action_start_workflow('FRANCHISE-APV')

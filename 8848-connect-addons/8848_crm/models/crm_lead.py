from odoo import api, fields, models

class CrmLead(models.Model):
    _name = 'crm.lead'
    _inherit = ['crm.lead', '8848.communication.mixin', '8848.workflow.mixin']

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

    @api.model
    def create_or_update_franchise_enquiry(self, payload):
        """
        CRM Intake Service for Franchise Enquiries.
        Returns a stable internal reference and lead ID.
        """
        # 1. Validate Mandatory
        if not payload.get('contact_name'):
            return {'success': False, 'error': 'contact_name is required'}
        if not payload.get('email_from'):
            return {'success': False, 'error': 'email_from is required'}

        # 2. Normalize
        email_from = payload['email_from'].strip().lower()
        mobile = payload.get('mobile', '').strip()
        external_entry_id = payload.get('external_entry_id')

        # 3. Idempotency Check
        if external_entry_id:
            existing_by_ext = self.search([('external_entry_id', '=', external_entry_id)], limit=1)
            if existing_by_ext:
                return {'success': True, 'reference': existing_by_ext.enquiry_reference, 'lead_id': existing_by_ext.id, 'status': 'idempotent'}

        # 4. Duplicate Check
        existing_lead = False
        territory_interest = payload.get('franchise_territory_interest')
        
        # Check for open leads with same email and territory
        domain = [('email_from', '=', email_from), ('type', '=', 'opportunity')]
        if territory_interest:
            domain.append(('franchise_territory_interest', '=', territory_interest))
            
        open_leads = self.search(domain)
        if open_leads:
            existing_lead = open_leads[0]

        # 5. Partner Check
        existing_partner = self.env['res.partner'].search([
            ('email', '=', email_from), 
            ('is_franchise', '=', True)
        ], limit=1)

        # 6. Prepare Values
        lead_vals = {
            'name': f"Franchise Enquiry: {payload.get('contact_name')} - {territory_interest or 'General'}",
            'contact_name': payload['contact_name'],
            'email_from': email_from,
            'mobile': mobile,
            'franchise_territory_interest': territory_interest,
            'external_entry_id': external_entry_id,
            'type': 'opportunity',
            'description': payload.get('message', ''),
            'marketing_consent': payload.get('marketing_consent', False),
            'privacy_consent': payload.get('privacy_consent', False),
        }

        if existing_partner:
            lead_vals['partner_id'] = existing_partner.id
            lead_vals['name'] = f"Expansion Enquiry: {existing_partner.name} - {territory_interest or 'General'}"

        if existing_lead:
            # Update existing lead
            existing_lead.write(lead_vals)
            existing_lead.message_post(body=f"Received updated enquiry for territory {territory_interest}. External ID: {external_entry_id}")
            lead = existing_lead
        else:
            # Generate Sequence
            lead_vals['enquiry_reference'] = self.env['ir.sequence'].next_by_code('8848.franchise.enquiry') or 'NEW'
            # Create new lead
            lead = self.create(lead_vals)
            lead.message_post(body=f"New Franchise Enquiry received via Gateway. External ID: {external_entry_id}")
            
            # Workflow Integration
            # For MVP, we emit an event if the lead starts a workflow, or just log it. 
            # Often the workflow instance is started explicitly, but we can emit a global event 
            # or rely on the workflow engine observing the create.
            if hasattr(lead, 'action_emit_event'):
                # Note: this will do nothing if no workflow instance is active for this record yet,
                # but it satisfies the architecture contract.
                lead.action_emit_event('franchise_enquiry_received')

            # Automated Acknowledgement
            ICP = self.env['ir.config_parameter'].sudo()
            ack_template_id = int(ICP.get_param('8848_crm.ack_template_id', 0))
            if ack_template_id:
                template = self.env['8848.communication.template'].browse(ack_template_id)
                if template.exists():
                    lead.send_communication(template.code)

        lead._assign_franchise_lead()
        lead._create_followup_activity('Follow up on new franchise enquiry', delay_days=1)

        return {
            'success': True,
            'reference': lead.enquiry_reference,
            'lead_id': lead.id,
            'status': 'updated' if existing_lead else 'created'
        }

    def _assign_franchise_lead(self):
        """Assigns lead based on configuration settings."""
        self.ensure_one()
        if not self.user_id:
            ICP = self.env['ir.config_parameter'].sudo()
            default_user_id = int(ICP.get_param('8848_crm.default_user_id', 0))
            default_team_id = int(ICP.get_param('8848_crm.default_team_id', 0))
            
            if default_user_id:
                self.user_id = default_user_id
            if default_team_id:
                self.team_id = default_team_id

    def _create_followup_activity(self, summary, delay_days=1):
        """Creates a follow-up activity for the assigned user."""
        self.ensure_one()
        
        # Don't create duplicate activities of the same summary
        existing = self.env['mail.activity'].search([
            ('res_model', '=', self._name),
            ('res_id', '=', self.id),
            ('summary', '=', summary)
        ])
        if existing:
            return

        date_deadline = fields.Date.context_today(self) + fields.Datetime.timedelta(days=delay_days)
        self.env['mail.activity'].create({
            'res_model_id': self.env.ref('crm.model_crm_lead').id,
            'res_id': self.id,
            'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
            'summary': summary,
            'user_id': self.user_id.id or self.env.uid,
            'date_deadline': date_deadline,
        })

    def recalculate_franchise_score(self):
        """Calculates lead score based on configured rules or application data."""
        for lead in self:
            score = 0
            app = lead.active_application_id
            if app:
                # Basic mock scoring rules for MVP
                if app.business_experience:
                    score += 20
                if app.hospitality_experience:
                    score += 20
                if app.investment_available > 500000:
                    score += 40
                elif app.investment_available > 250000:
                    score += 20
                if not app.finance_required:
                    score += 10
            
            # Additional points for general completeness
            if lead.mobile:
                score += 5
            if lead.franchise_territory_interest:
                score += 5
                
            lead.franchise_score = score

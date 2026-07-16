from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError

class WorkflowInstance(models.Model):
    _name = '8848.workflow.instance'
    _table = 'connect_workflow_instance'
    _description = 'Workflow Instance'
    _rec_name = 'reference'
    _order = 'id desc'
    _inherit = ['mail.thread']

    workflow_id = fields.Many2one('8848.workflow.definition', string='Workflow Definition', required=True, ondelete='restrict', tracking=True)
    reference = fields.Char(string='Reference', compute='_compute_reference', store=True)
    
    res_model = fields.Char(string='Target Model', required=True, index=True)
    res_id = fields.Integer(string='Target Record ID', required=True, index=True)
    
    company_id = fields.Many2one('res.company', string='Company', related='workflow_id.company_id', store=True)
    active = fields.Boolean(default=True)
    
    current_step_id = fields.Many2one('8848.workflow.step', string='Current Step', tracking=True)
    entered_current_step_at = fields.Datetime(string='Entered Step At', tracking=True)
    escalation_triggered = fields.Boolean(string='Escalation Triggered', default=False)
    
    correlation_id = fields.Char(string='Correlation ID', index=True, tracking=True, help="Idempotency key to prevent duplicate instantiations")
    
    state = fields.Selection([
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='State', default='in_progress', tracking=True, required=True)
    
    started_at = fields.Datetime(string='Started At', default=fields.Datetime.now, readonly=True)
    completed_at = fields.Datetime(string='Completed At', readonly=True)
    deadline = fields.Datetime(string='Deadline', tracking=True)
    
    log_ids = fields.One2many('8848.workflow.log', 'instance_id', string='Logs')
    
    @api.depends('workflow_id', 'res_model', 'res_id')
    def _compute_reference(self):
        for record in self:
            if record.workflow_id and record.res_model and record.res_id:
                record.reference = f"{record.workflow_id.code}-{record.res_model}-{record.res_id}"
            else:
                record.reference = _("New Instance")
    _constraint_unique_active_instance = models.Constraint(
        "unique(workflow_id, res_model, res_id, active)",
        "A business record can only have one active instance of a specific workflow!"
    )

    def _get_business_record(self):
        self.ensure_one()
        try:
            return self.env[self.res_model].browse(self.res_id).exists()
        except KeyError:
            raise ValidationError(_("Target model %s does not exist.") % self.res_model)

    def action_start(self):
        """Starts the workflow instance and places it in the initial step."""
        for instance in self:
            if instance.state != 'in_progress':
                continue
            if not instance.workflow_id.initial_step_id:
                raise ValidationError(_("Workflow '%s' has no initial step defined.") % instance.workflow_id.name)
            
            # Start workflow
            instance.current_step_id = instance.workflow_id.initial_step_id
            instance.entered_current_step_at = fields.Datetime.now()
            instance.escalation_triggered = False
            
            # Execute destination step entry action
            if instance.current_step_id.entry_action_id:
                try:
                    instance.current_step_id.entry_action_id.with_context(
                        active_model=instance.res_model, 
                        active_id=instance.res_id,
                        workflow_instance_id=instance.id
                    ).sudo().run()
                except Exception as e:
                    raise ValidationError(_("Entry action failed on initial step %s: %s") % (instance.current_step_id.name, e))

            # Create activities for the initial step
            instance._create_step_activities(instance.current_step_id)

            # Create a log entry
            self.env['8848.workflow.log'].sudo().create({
                'instance_id': instance.id,
                'action': 'started',
                'destination_step_id': instance.current_step_id.id,
                'comment': _("Workflow started automatically.")
            })

    def action_cancel(self, reason=None):
        """Cancels the active workflow instance."""
        for instance in self:
            if instance.state == 'completed':
                raise ValidationError(_("Cannot cancel a completed workflow."))
            instance.write({
                'state': 'cancelled',
                'active': False,
                'completed_at': fields.Datetime.now()
            })
            self.env['8848.workflow.log'].sudo().create({
                'instance_id': instance.id,
                'action': 'cancelled',
                'comment': reason or _("Workflow cancelled.")
            })

    def _create_step_activities(self, step):
        self.ensure_one()
        if step.step_type != 'approval':
            return
            
        activity_type = self.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)
        if not activity_type:
            return
            
        users_to_assign = self.env['res.users']
        if step.responsible_user_id:
            users_to_assign |= step.responsible_user_id
        elif step.responsible_group_id:
            users_to_assign |= step.responsible_group_id.user_ids
            
        model_id = self.env['ir.model']._get_id(self.res_model)
        for user in users_to_assign:
            self.env['mail.activity'].sudo().create({
                'res_model_id': model_id,
                'res_id': self.res_id,
                'activity_type_id': activity_type.id,
                'summary': _('Approval Required: %s') % step.name,
                'note': _('Workflow %s is waiting for approval at step %s') % (self.workflow_id.name, step.name),
                'user_id': user.id,
            })

    def _complete_step_activities(self):
        self.ensure_one()
        model_id = self.env['ir.model']._get_id(self.res_model)
        activities = self.env['mail.activity'].sudo().search([
            ('res_model_id', '=', model_id),
            ('res_id', '=', self.res_id),
            ('summary', 'like', 'Approval Required: %')
        ])
        for activity in activities:
            activity.action_done()

    def execute_transition(self, transition):
        """Executes a transition on this instance."""
        self.ensure_one()
        if self.state != 'in_progress':
            raise ValidationError(_("Workflow is not in progress."))
        if self.current_step_id != transition.source_step_id:
            raise ValidationError(_("Transition is not valid from the current step."))
            
        if transition.required_group_id:
            ext_id_dict = transition.required_group_id.get_external_id()
            ext_id = ext_id_dict.get(transition.required_group_id.id, '')
            if not ext_id or not self.env.user.has_group(ext_id):
                # Fallback to direct check if external ID is tricky
                if self.env.user not in transition.required_group_id.user_ids:
                    raise AccessError(_("You do not have the required permissions (%s) to perform this transition.") % transition.required_group_id.name)
            
        record = self._get_business_record()
        
        # Check transition condition domain
        if not transition._evaluate_condition(record):
            raise ValidationError(_("Transition conditions are not met."))
        
        # Complete activities for the source step
        self._complete_step_activities()
        
        # Execute source step exit action
        if transition.source_step_id.exit_action_id:
            try:
                transition.source_step_id.exit_action_id.with_context(
                    active_model=self.res_model, 
                    active_id=self.res_id,
                    workflow_instance_id=self.id
                ).sudo().run()
            except Exception as e:
                raise ValidationError(_("Exit action failed on step %s: %s") % (transition.source_step_id.name, e))

        # Move to destination
        self.current_step_id = transition.destination_step_id
        self.entered_current_step_at = fields.Datetime.now()
        self.escalation_triggered = False
        
        # Create activities for destination step
        self._create_step_activities(self.current_step_id)
        
        # Execute destination step entry action
        if self.current_step_id.entry_action_id:
            try:
                self.current_step_id.entry_action_id.with_context(
                    active_model=self.res_model, 
                    active_id=self.res_id,
                    workflow_instance_id=self.id
                ).sudo().run()
            except Exception as e:
                raise ValidationError(_("Entry action failed on step %s: %s") % (self.current_step_id.name, e))
        
        if self.current_step_id.step_type == 'end':
            self.write({
                'state': 'completed',
                'active': False,
                'completed_at': fields.Datetime.now()
            })
            
        self.env['8848.workflow.log'].sudo().create({
            'instance_id': self.id,
            'action': 'transition',
            'source_step_id': transition.source_step_id.id,
            'destination_step_id': transition.destination_step_id.id,
            'comment': _("Transitioned via %s") % transition.name
        })

    def action_open_wizard(self):
        self.ensure_one()
        if self.state != 'in_progress':
            raise ValidationError(_("Workflow is not in progress."))
            
        return {
            'name': _('Execute Transition'),
            'type': 'ir.actions.act_window',
            'res_model': '8848.workflow.action.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_instance_id': self.id,
            }
        }

    @api.model
    def _cron_process_automations_and_slas(self):
        """
        Runs periodically via cron to evaluate automatic transitions and SLAs on active workflow instances.
        """
        active_instances = self.search([('state', '=', 'in_progress'), ('active', '=', True)])
        
        for instance in active_instances:
            # 1. Check Automatic Transitions
            automatic_transitions = self.env['8848.workflow.transition'].search([
                ('source_step_id', '=', instance.current_step_id.id),
                ('is_automatic', '=', True)
            ])
            
            record = None
            for transition in automatic_transitions:
                if not record:
                    # Get record lazily only if there is an automatic transition
                    try:
                        record = instance._get_business_record()
                    except Exception:
                        break # Record might have been deleted
                        
                if transition._evaluate_condition(record):
                    try:
                        instance.execute_transition(transition)
                    except Exception as e:
                        import logging
                        _logger = logging.getLogger(__name__)
                        _logger.error("Cron failed to execute automatic transition %s on instance %s: %s", transition.name, instance.id, e)
                    break # Only execute one automatic transition per cron tick
            
            # 2. Check SLAs and Escalations
            # If the instance was transitioned above, current_step_id has changed, so we evaluate SLA for the NEW step or the OLD step if it didn't transition.
            if instance.state == 'in_progress' and not instance.escalation_triggered and instance.current_step_id.sla_hours > 0 and instance.entered_current_step_at:
                from datetime import timedelta
                sla_deadline = instance.entered_current_step_at + timedelta(hours=instance.current_step_id.sla_hours)
                
                if fields.Datetime.now() > sla_deadline:
                    # SLA Breached!
                    instance.escalation_triggered = True
                    if instance.current_step_id.escalation_action_id:
                        try:
                            instance.current_step_id.escalation_action_id.with_context(
                                active_model=instance.res_model, 
                                active_id=instance.res_id,
                                workflow_instance_id=instance.id
                            ).sudo().run()
                        except Exception as e:
                            import logging
                            _logger = logging.getLogger(__name__)
                            _logger.error("Escalation action failed on step %s: %s", instance.current_step_id.name, e)
                    
                    self.env['8848.workflow.log'].sudo().create({
                        'instance_id': instance.id,
                        'action': 'escalated',
                        'result': 'escalated',
                        'comment': _("SLA Breached on step %s. Escalation triggered.") % instance.current_step_id.name
                    })

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class WorkflowInstance(models.Model):
    _name = '8848.workflow.instance'
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

    _sql_constraints = [
        ('unique_active_instance', 
         'unique(workflow_id, res_model, res_id, active)', 
         'A business record can only have one active instance of a specific workflow!')
    ]

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

    def execute_transition(self, transition):
        """Executes a transition on this instance."""
        self.ensure_one()
        if self.state != 'in_progress':
            raise ValidationError(_("Workflow is not in progress."))
        if self.current_step_id != transition.source_step_id:
            raise ValidationError(_("Transition is not valid from the current step."))
            
        record = self._get_business_record()
        
        # Check transition condition domain
        if not transition._evaluate_condition(record):
            raise ValidationError(_("Transition conditions are not met."))
        
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

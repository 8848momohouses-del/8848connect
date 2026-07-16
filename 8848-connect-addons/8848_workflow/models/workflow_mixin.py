from odoo import api, fields, models, _

class WorkflowMixin(models.AbstractModel):
    _name = '8848.workflow.mixin'
    _table = 'connect_workflow_mixin'
    _description = 'Workflow Mixin'

    workflow_count = fields.Integer(compute='_compute_workflow_count', string='Workflow Count')

    def _compute_workflow_count(self):
        for record in self:
            record.workflow_count = self.env['8848.workflow.instance'].search_count([
                ('res_model', '=', record._name),
                ('res_id', '=', record.id)
            ])

    def action_view_workflows(self):
        self.ensure_one()
        return {
            'name': _('Workflows'),
            'type': 'ir.actions.act_window',
            'res_model': '8848.workflow.instance',
            'view_mode': 'tree,form',
            'domain': [('res_model', '=', self._name), ('res_id', '=', self.id)],
            'context': {
                'default_res_model': self._name,
                'default_res_id': self.id
            },
        }

    def action_start_workflow(self, workflow_code):
        """Helper to programmatically start a workflow from a business record"""
        self.ensure_one()
        workflow = self.env['8848.workflow.definition'].search([
            ('code', '=', workflow_code),
            ('company_id', 'in', [self.env.company.id, False])
        ], limit=1)
        
        if not workflow:
            raise ValueError(_("Workflow %s not found.") % workflow_code)
            
        return workflow.action_instantiate(self._name, self.id)

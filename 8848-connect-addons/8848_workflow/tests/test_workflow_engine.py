from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, AccessError

class TestWorkflowEngine(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestWorkflowEngine, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        
        # We need a generic model to test against. res.partner is universally available.
        cls.target_model = cls.env.ref('base.model_res_partner')
        
        # Create a test business record
        cls.test_partner = cls.env['res.partner'].create({'name': 'Workflow Test Partner'})
        
        # Create Workflow Definition
        cls.workflow_def = cls.env['8848.workflow.definition'].create({
            'name': 'Test Workflow',
            'code': 'TEST-WF',
            'target_model_id': cls.target_model.id,
            'allow_multiple_active_instances': False,
        })
        
        # Create Steps
        cls.step_start = cls.env['8848.workflow.step'].create({
            'name': 'Start',
            'code': 'START',
            'workflow_id': cls.workflow_def.id,
            'step_type': 'start',
            'sequence': 10
        })
        
        cls.step_middle = cls.env['8848.workflow.step'].create({
            'name': 'Middle',
            'code': 'MIDDLE',
            'workflow_id': cls.workflow_def.id,
            'step_type': 'approval',
            'sequence': 20
        })
        
        cls.step_end = cls.env['8848.workflow.step'].create({
            'name': 'End',
            'code': 'END',
            'workflow_id': cls.workflow_def.id,
            'step_type': 'end',
            'sequence': 30
        })
        
        # Set Initial Step
        cls.workflow_def.initial_step_id = cls.step_start
        
        # Create Transitions
        cls.trans_to_middle = cls.env['8848.workflow.transition'].create({
            'name': 'Go to Middle',
            'workflow_id': cls.workflow_def.id,
            'source_step_id': cls.step_start.id,
            'destination_step_id': cls.step_middle.id,
        })
        
        cls.trans_to_end = cls.env['8848.workflow.transition'].create({
            'name': 'Go to End',
            'workflow_id': cls.workflow_def.id,
            'source_step_id': cls.step_middle.id,
            'destination_step_id': cls.step_end.id,
        })

    def test_01_workflow_instantiation(self):
        """Test instantiation and active instance logic"""
        instance = self.workflow_def.action_instantiate('res.partner', self.test_partner.id)
        
        self.assertEqual(instance.state, 'in_progress', "Instance should be in progress")
        self.assertEqual(instance.current_step_id, self.step_start, "Instance should start at the initial step")
        
        # Test duplicate prevention (allow_multiple_active_instances = False)
        with self.assertRaises(ValidationError):
            self.workflow_def.action_instantiate('res.partner', self.test_partner.id)
            
    def test_02_idempotency_correlation_id(self):
        """Test idempotency via correlation_id"""
        instance1 = self.workflow_def.action_instantiate('res.partner', self.test_partner.id, correlation_id='TEST_IDEMPOTENCY_123')
        
        # Calling instantiate again with the SAME correlation_id should return the exact same instance without raising an error
        instance2 = self.workflow_def.action_instantiate('res.partner', self.test_partner.id, correlation_id='TEST_IDEMPOTENCY_123')
        
        self.assertEqual(instance1.id, instance2.id, "Idempotency check failed. Returned a different instance.")

    def test_03_transitions(self):
        """Test moving through transitions and log generation"""
        instance = self.workflow_def.action_instantiate('res.partner', self.test_partner.id)
        
        # Move to middle
        instance.execute_transition(self.trans_to_middle)
        self.assertEqual(instance.current_step_id, self.step_middle)
        
        # Verify log creation
        logs = self.env['8848.workflow.log'].search([('instance_id', '=', instance.id), ('action', '=', 'transition')])
        self.assertTrue(logs)
        self.assertEqual(logs[0].source_step_id, self.step_start)
        self.assertEqual(logs[0].destination_step_id, self.step_middle)
        
        # Move to end
        instance.execute_transition(self.trans_to_end)
        self.assertEqual(instance.current_step_id, self.step_end)
        self.assertEqual(instance.state, 'completed', "Instance should be completed when reaching end step")
        
    def test_04_security_gates(self):
        """Test transition security groups"""
        # Create a new transition that requires ERP Manager
        manager_group = self.env.ref('base.group_erp_manager')
        
        secure_trans = self.env['8848.workflow.transition'].create({
            'name': 'Secure Go to Middle',
            'workflow_id': self.workflow_def.id,
            'source_step_id': self.step_start.id,
            'destination_step_id': self.step_middle.id,
            'required_group_id': manager_group.id
        })
        
        # Create a basic internal user
        basic_user = self.env['res.users'].create({
            'name': 'Basic User',
            'login': 'basic@example.com',
        })
        basic_user.write({'groups_id': [(4, self.env.ref('base.group_user').id)]})
        
        instance = self.workflow_def.action_instantiate('res.partner', self.test_partner.id)
        
        # The basic user should fail to execute this transition
        with self.assertRaises(AccessError):
            instance.with_user(basic_user).execute_transition(secure_trans)
            
        # Add the manager group to the user
        basic_user.write({'groups_id': [(4, manager_group.id)]})
        
        # Now it should succeed
        instance.with_user(basic_user).execute_transition(secure_trans)
        self.assertEqual(instance.current_step_id, self.step_middle)

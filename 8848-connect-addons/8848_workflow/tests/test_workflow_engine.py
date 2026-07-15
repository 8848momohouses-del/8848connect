from odoo.tests.common import TransactionCase
from odoo.exceptions import AccessError

class TestWorkflowEngine(TransactionCase):
    
    def setUp(self):
        super(TestWorkflowEngine, self).setUp()
        self.WorkflowDefinition = self.env['8848.workflow.definition']
        self.WorkflowInstance = self.env['8848.workflow.instance']
        
        # We will create test definitions and steps in Batch W6 / W7 
        # when we build the POC or test the orchestration engine fully.
        
    def test_01_module_loads(self):
        """Test that the workflow foundation module installs and loads correctly."""
        # Simple test to verify the models are in the registry
        self.assertTrue(self.WorkflowDefinition)
        self.assertTrue(self.WorkflowInstance)
        
    def test_02_access_rights_system(self):
        """System Administrator should be able to create definitions."""
        sys_admin = self.env.ref('base.user_admin')
        # This will fail if security rules are wrong
        definition = self.WorkflowDefinition.with_user(sys_admin).create({
            'name': 'Test Workflow',
            'code': 'TEST_WF',
            'target_model_id': self.env.ref('base.model_res_partner').id,
        })
        self.assertTrue(definition.id)

    def test_03_access_rights_user(self):
        """Normal user should NOT be able to create definitions."""
        # Ensure there is a normal user
        normal_user = self.env['res.users'].create({
            'name': 'Normal User',
            'login': 'normal_user',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])]
        })
        
        with self.assertRaises(AccessError):
            self.WorkflowDefinition.with_user(normal_user).create({
                'name': 'Test Workflow User',
                'code': 'TEST_WF_USER',
                'target_model_id': self.env.ref('base.model_res_partner').id,
            })

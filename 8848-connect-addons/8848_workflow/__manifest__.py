{
    'name': '8848 Workflow Engine',
    'version': '19.0.1.0.0',
    'summary': 'Core workflow and orchestration engine for 8848 Connect',
    'description': """
        8848 Workflow Engine
        ====================
        Foundation module providing an orchestrated workflow engine for business models.
        Features:
        - Workflow Definitions & Steps
        - Transitions & Conditions
        - Workflow Instances linked to native business records
        - Immutable Audit Logs
    """,
    'category': 'Hidden/Dependency',
    'author': '8848 Momo House',
    'website': 'https://8848momos.com.au',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'mail',
        '8848_security'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/workflow_menus.xml',
        'views/workflow_definition_views.xml',
        'views/workflow_step_views.xml',
        'views/workflow_transition_views.xml',
        'views/workflow_instance_views.xml',
        'views/workflow_log_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}

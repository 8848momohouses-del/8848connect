{
    'name': '8848 CRM Automation',
    'version': '1.0',
    'category': 'Sales/CRM',
    'summary': 'Franchise Enquiry and Conversion CRM Automation',
    'description': """
        Handles franchise enquiries, application submission, lead scoring, 
        duplicate management, and orchestrated conversion into franchise master records.
    """,
    'author': '8848 Momo House',
    'depends': [
        'base',
        'crm',
        '8848_franchise',
        '8848_workflow',
        '8848_communication',
        '8848_security'
    ],
    'data': [
        'security/crm_security.xml',
        'security/ir.model.access.csv',
        'data/crm_sequence.xml',
        'views/res_config_settings_views.xml',
        'views/crm_lead_views.xml',
        'views/franchise_application_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'OPL-1',
}

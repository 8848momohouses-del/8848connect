{
    'name': '8848 Connect - Driver Application',
    'version': '1.0',
    'category': 'Operations/Delivery',
    'summary': 'Phase 4: 8848_driver',
    'author': '8848 Momo House',
    'depends': ['hr', '8848_delivery'],
    'data': [
        'security/driver_security.xml',
        'security/ir.model.access.csv',
        'views/hr_employee_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}

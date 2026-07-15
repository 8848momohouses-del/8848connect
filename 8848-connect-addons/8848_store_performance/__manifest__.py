{
    'author': '8848 Momo House',
    'name': '8848 Connect - Store Performance',
    'version': '1.1',
    'category': 'Hidden',
    'summary': 'Store KPIs and Franchise Rankings',
    'depends': ['8848_franchise', 'account', '8848_security'],
    'data': [
        'security/ir.model.access.csv',
        'views/store_performance_views.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}

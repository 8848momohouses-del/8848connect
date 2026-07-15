{
    'name': '8848 Connect - 8848_marketing_fee',
    'version': '1.1',
    'category': 'Sales',
    'summary': 'Phase 3: 8848_marketing_fee',
    'author': '8848 Momo House',
    'depends': ['8848_franchise', '8848_royalty', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/marketing_fee_statement_views.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}

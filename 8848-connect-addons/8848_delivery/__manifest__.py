{
    'name': '8848 Connect - Delivery Routes',
    'version': '1.0',
    'category': 'Operations/Delivery',
    'summary': 'Phase 4: 8848_delivery',
    'author': '8848 Momo House',
    'depends': ['stock', 'hr', 'fleet', '8848_security'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/delivery_route_views.xml',
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}

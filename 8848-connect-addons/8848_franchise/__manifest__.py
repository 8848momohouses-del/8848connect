{
    'name': '8848 Connect - Franchise Core',
    'version': '1.1',
    'category': 'Sales',
    'summary': 'Franchise Master Record and lifecycle for the 8848 Business Suite.',
    'description': """
        Central Franchise Core for 8848 Momo House.
        One Franchise. One Record. One Source of Truth: the same partner record
        carries a franchise from first enquiry through agreement, opening and
        ongoing operations. Provides lifecycle stages, milestone tracking and
        the operational gate consumed by the portal and reporting modules.
    """,
    'author': '8848 Momo House',
    'depends': ['base', 'contacts', '8848_security', '8848_workflow'],
    'data': [
        'security/ir.model.access.csv',
        'data/franchise_stage_data.xml',
        'views/res_partner_views.xml',
    ],
    'post_init_hook': '_assign_stage_to_existing_franchises',
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}

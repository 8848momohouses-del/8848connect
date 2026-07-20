{
    'name': '8848 Connect - Communication Hub',
    'version': '1.0',
    'category': 'Productivity',
    'summary': 'Unified communication queue and template engine for the 8848 Business Suite.',
    'description': """
        Centralizes messaging via Email, SMS, Portal, and internal notes.
        Features:
        - Multi-channel unified message queue
        - Channel-agnostic templates
        - Retry engine
        - Full audit history per business record
    """,
    'author': '8848 Momo House',
    'depends': ['base', 'mail', 'sms', '8848_security'],
    'data': [
        'security/ir.model.access.csv',
        'data/communication_channel_data.xml',
        'data/communication_cron.xml',
        'views/communication_menus.xml',
        'views/communication_channel_views.xml',
        'views/communication_template_views.xml',
        'views/communication_message_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}

# -*- coding: utf-8 -*-
{
    'name': '8848 Connect Glass Skin',
    'version': '19.0.1.0.0',
    'category': 'Hidden',
    'summary': 'Re-colors the Liquid Glass theme to the 8848 brand (red / white / blue).',
    'description': """
        Brand layer on top of theme_liquid_glass: swaps the theme's teal
        palette for the 8848 red/white/blue, replaces the background with a
        navy-blue gradient with red glow, and improves text contrast.
        Never modifies the third-party theme files themselves.
    """,
    'author': '8848 Momo House',
    'depends': ['theme_liquid_glass'],
    'assets': {
        'web.assets_backend': [
            # Inject brand palette right after the theme's variables so every
            # subsequent theme SCSS file compiles with 8848 colors.
            (
                'after',
                'theme_liquid_glass/static/src/scss/variables.scss',
                '8848_glass_skin/static/src/scss/palette.scss',
            ),
            # Final overrides (background gradient, contrast fixes) at bundle end.
            '8848_glass_skin/static/src/scss/skin.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

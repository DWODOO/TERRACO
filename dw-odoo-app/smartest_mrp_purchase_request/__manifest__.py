# -*- coding: utf-8 -*-
{
    'name': 'MRP Management',
    'version': '0.1',
    'category': 'Localization',
    'description': """
        This module adapts the Production.
        """,
    'author': 'SMARTEST - ALGERIA',
    'website': 'www.smartest.dz',
    'depends': [
        'mrp',
        'purchase_tier_validation',
    ],
    'data': [
        # data
        # Security
        # views
        'views/mrp_production_views.xml',

    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

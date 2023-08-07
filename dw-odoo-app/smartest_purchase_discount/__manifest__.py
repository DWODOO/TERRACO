# -*- coding: utf-8 -*-
{
    'name': 'Algeria - Purchases Discount BY SMARTEST',
    'version': '1.0.0',
    'category': 'Purchase',
    'description': """
        This module add the Discount features to Purchase module.
        """,
    'author': 'SMARTEST - ALGERIA',
    'website': 'www.smartest.dz',
    'depends': [
        'purchase',
        'smartest_base',
    ],
    'data': [
        'security/security.xml',
        'views/purchase_order_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

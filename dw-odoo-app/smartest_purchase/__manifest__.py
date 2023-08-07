# -*- coding: utf-8 -*-
{
    'name': 'Algeria - Purchases Management System',
    'version': '1.0.0',
    'category': 'Purchase',
    'description': """
        This module add the necessary ffeatures to Purchase module.
        """,
    'author': 'SMARTEST - ALGERIA',
    'website': 'www.smartest.dz',
    'depends': [
        'purchase',
        'smartest_l10n_dz',
    ],
    'data': [
        'views/purchase_order_views.xml',
        'views/account_move_views.xml',
        'report/templates.xml',
        'views/purchase_order_views.xml'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

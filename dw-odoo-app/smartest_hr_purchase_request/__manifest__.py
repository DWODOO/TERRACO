# -*- coding: utf-8 -*-
{
    'name': 'Purchase by Department',
    'version': '0.1',
    'category': 'Localization',
    'description': """
        This module links purchase request with hr.
        """,
    'author': 'SMARTEST - ALGERIA',
    'website': 'www.smartest.dz',
    'depends': [
        'hr',
        'purchase_tier_validation',
    ],
    'data': [
        # data
        # Security
        'security/security.xml',
        # views
        'views/hr_department_views.xml',
        'views/purchase_request_views.xml',
        'views/res_user_views.xml',

    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

# -*- coding: utf-8 -*-
{
    'name': 'Algeria Accounting - By SMARTEST ALGERIA',
    'version': '1.0.0',
    'category': 'Localization',
    'author': 'SMARTEST - ALGERIA',
    'website': 'www.smartest.dz',
    'description': "Improvements of Algeria Accounting By SMARTEST ALGERIA",
    'depends': [
        'account',
    ],
    'data': [
        'views/account_move_views.xml',
        'views/payment_method_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # 'smartest_account/static/src/xml/**/*',
        ],
    },
    'license': 'LGPL-3',
}

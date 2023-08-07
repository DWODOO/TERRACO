# -*- coding: utf-8 -*-
{
    'name': "Discount Accounting Line",
    'summary': "This module allow accounting the invoice line discount in a different account.",
    'version': '1.0.0',
    'depends': ['sale_stock', 'smartest_l10n_dz'],
    'author': 'SMARTEST ALGERIA',
    'sequence': 100,
    'website': 'https://www.smartest.dz',
    'category': 'Account/Accounting',
    'data': [
        'views/res_config_settings_views.xml',
        'views/product_category_views.xml',
        'views/product_template_views.xml',
        'views/account_move_views.xml',
    ],
    'auto_install': False,
    'license': 'LGPL-3',
}

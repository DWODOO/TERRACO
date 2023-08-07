# -*- coding: utf-8 -*-
{
    'name': 'Landed Costs - By SMARTEST',
    'version': '1.0.2',
    'category': 'Stock  ',
    'description': """
        This module improve the core module stock_landed_cost.
        This module actually depends on smartest purchase, but in order to use it multiple project 
        we'll comment its smartest purchase dependency and just point it out.
        """,
    'author': 'SMARTEST - ALGERIA',
    'website': 'www.smartest.dz',
    'depends': [
        'smartest_purchase',
        'stock_landed_costs',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/hs_code_data.xml',
        'views/stock_landed_cost_views.xml',
        'views/stock_hs_code_views.xml',
        'views/product_views.xml',
        'views/product_categorie.xml',
        # 'views/purchase_import_folder.xml',
        # 'views/purchase.xml',
        # 'views/comex_file.xml',
        # 'reports/purchase_import_folder.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

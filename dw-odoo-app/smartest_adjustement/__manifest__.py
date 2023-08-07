# -*- coding: utf-8 -*-
{
    'name': "Smartest Inventory Ajustments",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/smartest_stock_quant.xml',
        'views/template.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
            'web.assets_backend': [
                'smartest_adjustement/static/src/js/smartest_barcode_inventory.js',
                'smartest_adjustement/static/src/view/code_scanner.xml'
            ],
            # 'web.assets_common': [
            #     'smartest_adjustement/static/src/view/code_scanner.xml',
                # 'smartest_barcode/static/src/view/code_scanner_test.xml',
            # ],
        }
}

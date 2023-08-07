# -*- coding: utf-8 -*-
{
    'name': "anouar smartest stock",

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
    'depends': ['base','account_asset','stock','maintenance','account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/account_asset_views.xml',
        'views/equpement_inventory_views.xml',
        # 'views/maintenance_equipment.xml',
        'views/template.xml',
        # 'report/equipment_barcode.xml',
        # 'report/report.xml',
    ],
'assets': {
        'web.assets_backend': [
            'smartest_immobilisation/static/src/js/equipment_barcode_main_menu.js',
            'smartest_immobilisation/static/src/view/code_scanner.xml',
        ],
        # 'web.assets_qweb': [
        #     'smartest_immobilisation/static/src/view/code_scanner.xml',
        # ],
    },

    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

# -*- coding: utf-8 -*-
{
    'name': 'SMARTEST Base Module',
    'version': '1.0.0',
    'description': """
    Adds extra functionality and improvements to odoo 
    """,
    'summary': 'Improvements to base features by SMARTEST',
    'author': 'SMARTEST - ALGERIA',
    'website': 'www.smartest.dz',
    'license': 'AGPL-3',
    'category': 'Hidden',
    'depends': [
        'base_setup',
    ],
    'images': [],
    'data': [
        'data/ir_config_parameter.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/l10n_dz_country_state_data.xml',
        'data/l10n_dz_commune_data.xml',
        'data/sequence_data.xml',
        'views/res_commune_views.xml',
        'views/res_partner_views.xml',
        'views/res_brand_views.xml',
        'wizard/res_config_settings_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

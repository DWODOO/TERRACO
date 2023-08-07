# -*- coding: utf-8 -*-
{
    'name': 'MRP/MAINTENANCE Management',
    'version': '0.1',
    'category': 'Localization',
    'description': """
        This module adapts the Production.
        """,
    'author': 'SMARTEST - ALGERIA',
    'website': 'www.smartest.dz',
    'depends': [
        'mrp',
        'maintenance',
    ],
    'data': [
        # data
        # Security
        # views
        'views/mrp_production_views.xml',
        'views/maintenance_request.xml',

    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

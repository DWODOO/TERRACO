# -*- coding: utf-8 -*-
{
    'name': 'Planning By SMARTEST',
    'version': '1.0.0',
    'category': 'Human Resources/Planning',
    'description': """
        HR Planning improvements By SMARTEST
        """,
    'author': 'SMARTEST - ALGERIA',
    'website': 'www.smartest.dz',
    'depends': [
        'planning',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/planning_slot_views.xml',
        'views/planning_slot_type_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

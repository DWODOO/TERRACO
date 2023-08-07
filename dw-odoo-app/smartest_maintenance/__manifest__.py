# -*- coding: utf-8 -*-
{
    'name': 'Maintenance - By SMARTEST',
    'version': '1.0.1',
    'category': 'Maintenance  ',
    'description': """
        This module improve the core module maintenance.
        """,
    'author': 'SMARTEST - ALGERIA',
    'website': 'www.smartest.dz',
    'depends': [
        'hr_maintenance',
        'repair',
        'stock',
    ],
    'data': [
        'views/equipment_history.xml',
        'views/maintenance_equipment.xml',
        'views/maintenance_request.xml',
        'views/repair_order.xml',
        'views/maintenance_preventive_date.xml',
        'security/ir.model.access.csv',
        'reports/maintenance_request.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

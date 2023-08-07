# -*- coding: utf-8 -*-
{
    'name': 'Online Appraisal Comment',
    'category': 'Website/Website',
    'sequence': 33,
    'summary': 'Employee comments on Website',
    'description': """
    """,
    'author': 'SMARTEST - ALGERIA',
    'website': 'www.smartest.dz',
    'depends': [
        'portal',
        'smartest_hr_appraisal',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/appraisal_templates.xml'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

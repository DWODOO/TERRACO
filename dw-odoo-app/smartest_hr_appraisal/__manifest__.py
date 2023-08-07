# -*- coding: utf-8 -*-
{
    'name': 'HR Appraisal By SMARTEST',
    'version': '1.0.0',
    'category': 'Human Resources/Appraisals',
    'sequence': 32,
    'description': """
        HR Appraisal Improvements By SMARTEST
        """,
    'author': 'SMARTEST - ALGERIA',
    'website': 'www.smartest.dz',
    'depends': [
        'hr_appraisal',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/hr_appraisal_factor_data.xml',
        'data/hr_appraisal_level_data.xml',
        'data/hr_appraisal_objective_data.xml',
        'views/hr_appraisal_views.xml',
        'views/hr_appraisal_line_views.xml',
        'views/hr_appraisal_level_views.xml',
        'views/hr_appraisal_factor_views.xml',
        'views/hr_appraisal_factor_category_views.xml',
        'views/hr_appraisal_objective_views.xml',
        'views/hr_employee_views.xml',
        'wizard/hr_appraisal_comment_wizard_views.xml',
    ],
    'qweb': ['static/src/xml/factor_description_widget.xml'],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'assets': {
        'web.assets_backend': [
            '/smartest_hr_appraisal/static/src/js/factor_description_widget.js',
        ],
    },
    'license': 'LGPL-3',
}

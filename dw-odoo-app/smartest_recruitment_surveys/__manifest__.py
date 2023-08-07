# -*- coding: utf-8 -*-
{
    'name': 'Algeria - HR Recruitment-surveys',
    'version': '12.0.1',
    'category': 'Localization',
    'description': """
         
        """,
    'author': 'SMARTEST - ALGERIA',
    'website': 'www.smartest.dz',
    'depends': [
        'survey',
        'hr_recruitment'
    ],
    'data': [

        'views/recruitmet_stage_view.xml',
        'views/hr_applicant_view.xml',
        'views/survey_survey_view.xml',
        'views/survey_user_input_view.xml',
        'security/ir.model.access.csv',

    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

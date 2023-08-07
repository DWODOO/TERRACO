# -*- coding: utf-8 -*-
{
    'name': 'SMARTEST - Project Management System',
    'version': '1.0.2',
    'category': 'Localization',
    'description': """
        This module add the necessary fields and features for Project module.
        """,
    'author': 'SMARTEST - ALGERIA',
    'website': 'www.smartest.dz',
    'depends': [
        'project',
    ],
    'data': [
        'data/sequences.xml',
        'data/server_action_data.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/project_attendance.xml',
        'views/project_sprint_views.xml',
        'views/project_task_type_views.xml',
        'views/project_task_views.xml',
        'views/project_teams_views.xml',
        'views/project_views.xml',
        'views/res_users_views.xml',
    ],
    'web.assets_backend': [
        'smartest_project/static/src/scss/backend.scss',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

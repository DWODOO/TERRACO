# -*- coding: utf-8 -*-
{
    'name': 'Etat Financiers Management',
    'version': '0.1',
    'category': 'Localization',
    'description': """
        .
        """,
    'author': 'SMARTEST - ALGERIA',
    'website': 'www.smartest.dz',
    'depends': [
        'account_reports',
        'smartest_l10n_dz',

    ],
    'data': [
        # data
        'data/algerian_actif_report.xml',
        'data/algerian_balance_sheet.xml',
        'data/algerian_passive_balance.xml',
        # Security
        # report
        'report/smartest_etat_passif.xml',
        'report/smartest_etat_actif.xml',
        'report/smartest_tcr.xml',

        # views

        # wizard

    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

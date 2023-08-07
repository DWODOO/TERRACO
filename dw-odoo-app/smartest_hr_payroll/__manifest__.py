# -*- coding: utf-8 -*-
# Part of SMARTEST ALGERIA
{
    'name': 'Payroll  - By SMARTEST ALGERIA',
    'version': '1.0.0',
    'category': 'Localization',
    'author': 'SMARTEST - ALGERIA',
    'website': 'www.smartest.dz',
    'description': "Improvements of Payroll By SMARTEST ALGERIA",
    'depends': [
        'hr_payroll', 'hr_contract', 'hr_skills', 'l10n_dz_hr'
    ],
    'data': [
        # Security
        'security/ir.model.access.csv',
        # Data
        'data/ir_config_parameter.xml',
        # 'data/ir_cron_data.xml', # TYP: No need for to the cron job for now because experience fields are no more storable.
        'data/hr_irg_bareme_data.xml',
        'data/hr_iep_matrix_data.xml',
        'data/ir_sequence_data.xml',
        'data/salary_rule_category_data.xml',
        'data/salary_structure_data.xml',
        'data/salary_rule_data.xml',
        'data/work_entry_type_data.xml',
        'data/input_data.xml',
        # wizard
        'wizard/view_dac.xml',
        'wizard/views_301_bis.xml',
        'wizard/das_views.xml',
        'wizard/views_ats.xml',
        'wizard/hr_loan_postpone_wizard_views.xml',
        'wizard/individual_sheet_views.xml',
        'wizard/cnas_payoll_journal_views.xml',
        'wizard/individual_sheet_views.xml',
        'wizard/create_payoll_journal_views.xml',
        'wizard/hr_payslip_run_other_entries.xml',
        # Views
        'views/hr_contract_views.xml',
        'views/res_config_settings_views.xml',
        'views/hr_salary_rule_views.xml',
        'views/hr_salary_rule_category_views.xml',
        'views/hr_payslip_input_type_views.xml',
        'views/hr_bareme_irg_views.xml',
        'views/hr_iep_matrix_views.xml',
        'views/resource_calendar_views.xml',
        'views/hr_work_entry_type_views.xml',
        'views/hr_payslip_views.xml',
        'views/hr_payslip_run_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_loan_views.xml',
        'views/report_individual_sheet.xml',
        'views/hr_loan_internal_layout_template.xml',
        'views/hr_loan_report.xml',
        'views/report_cnas_payroll_journal.xml',
        'views/masse_salariale_views.xml',
        'views/report_cnas_payroll_journal.xml',
        'views/report_payroll_journal.xml',
        'views/report_payroll_journal_csp.xml',
        'views/smartest_layout_standard.xml',
        'views/smartest_layout.xml',
        # report
        'report/payslip_report.xml',
        'report/hr_payslip_run_report_avances.xml',
        'report/hr_payslip_run_report_prets.xml',
        'report/hr_payslip_run_report_retenue_mutuelle.xml',
        'report/hr_payroll_report.xml',

    ],
    'license': 'LGPL-3',
}

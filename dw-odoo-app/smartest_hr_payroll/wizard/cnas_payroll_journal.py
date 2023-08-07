# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from dateutil import relativedelta

from odoo import api, fields, models


class CNASPayrollJournal(models.TransientModel):
    _name = 'cnas.payroll.journal'
    _description = 'Payroll journal'

    def _get_default_employee_ids(self):
        return [(6, 0, self.env['hr.employee'].search([]).mapped('id'))]

    date_start = fields.Date(related='payslip_run_id.date_start', string="Date From")
    date_end = fields.Date(related='payslip_run_id.date_end', string="Date End")
    payslip_run_id = fields.Many2one('hr.payslip.run', string='Payslip Batches', required=True)
    employee_ids = fields.Many2many('hr.employee', string='HR Departments', default=_get_default_employee_ids)

    def print_report_by_employee(self, employee_ids):
        salary_rules = self.env['hr.salary.rule'].search([]).filtered(
            lambda p: p.appears_on_payslip and p.sequence not in [506, 405, 406, 1500])
        data = []

        rule_data2 = []
        total_cotisation = 0
        total_irg = 0
        cotisation = [0 for employee in employee_ids]
        irg = [0 for employee in employee_ids]
        for rule in salary_rules:
            rule_name = 'Retenue IRG absence' if 601 == rule.sequence else rule.name
            rule_data = [rule.sequence, rule_name]
            total = 0
            index = 0
            for employee in employee_ids:
                slip_lines = self.payslip_run_id.slip_ids.filtered(lambda p: p.state == 'done' and p.employee_id.id == employee.id).mapped(
                    'line_ids').filtered(lambda p: p.salary_rule_id.id == rule.id).mapped('total')
                total += round(abs(sum(slip_lines)), 2)
                if rule.sequence in [505,401,402 , 403, 507,408, 409] and total_cotisation >= 0:
                    total_cotisation += round(abs(sum(slip_lines)), 2)
                    cotisation[index] += round(abs(sum(slip_lines)), 2)
                rule_data.append(round(abs(sum(slip_lines)), 2))
                index += 1

            if total > 0:
                if rule.sequence > 409 and total_cotisation >= 0:
                    data.append((['\t', 'Total Cotisation salariale'] + cotisation + [total_cotisation]))
                    total_cotisation = -1
                rule_data.append(round(total, 2))
                data.append(rule_data)

        salary_rules = self.env['hr.salary.rule'].search([]).filtered(
            lambda p: p.sequence in [500, 505, 402, 403, 506, 405, 406, 507, 408, 409, 905, 1500])
        data2 = []
        total_employer_contribution = 0
        employer_contribution = [0 for employee in employee_ids]
        for rule in salary_rules:
            rule_name2 = 'Salaire de poste' if 500 == rule.sequence else rule.name
            rule_data2 = [rule.sequence, rule_name2]
            total2 = 0
            index3 = 0
            for employee in employee_ids:
                if rule.sequence == 905:
                    slip_lines = self.payslip_run_id.slip_ids.filtered(lambda p: p.state == 'done' and p.employee_id.id == employee.id).mapped(
                        'line_ids').filtered(lambda p: p.salary_rule_id.id == rule.id).mapped('amount')
                    total2 += round(abs(sum(slip_lines)), 2)
                else:
                    slip_lines = self.payslip_run_id.slip_ids.filtered(lambda
                                                                           p: p.state == 'done' and p.employee_id.id == employee.id).mapped(
                        'line_ids').filtered(lambda p: p.salary_rule_id.id == rule.id).mapped('total')
                    total2 += round(abs(sum(slip_lines)), 2)

                if rule.sequence in [506,405,406] and total_employer_contribution >= 0:
                    total_employer_contribution += round(abs(sum(slip_lines)), 2)
                    employer_contribution[index3] += round(abs(sum(slip_lines)), 2)
                rule_data2.append(round(abs(sum(slip_lines)), 2))
                index3 += 1
            if total2 > 0:

                if rule.sequence > 406 and total_employer_contribution >= 0:
                    data.append(
                        (['\t', 'Cotisations patronales'] + employer_contribution + [total_employer_contribution]))
                    total_employer_contribution = -1
                rule_data2.append(round(total2, 2))

                data2.append(rule_data2)
        #         Extraction of net taxable**************************************************************

        return [data, data2]

    def print_report(self):

        parsed_ids = []
        data = []
        list_group = []
        employee_ids = self.env['hr.employee'].search([('id', 'in', self.employee_ids.mapped('id')), ('id', 'not in', parsed_ids)], limit=7)
        if len(employee_ids):
            parsed_ids += employee_ids.mapped('id')
            list_group.append(employee_ids.mapped('name'))
            data.append(self.print_report_by_employee(employee_ids))
        while len(employee_ids):
            employee_ids = self.env['hr.employee'].search([('id', 'in', self.employee_ids.mapped('id')), ('id', 'not in', parsed_ids)], limit=7)
            if len(employee_ids):
                parsed_ids += employee_ids.mapped('id')
                list_group.append(employee_ids.mapped('name'))
                data.append(self.print_report_by_employee(employee_ids))

        return self.env.ref('smartest_hr_payroll.cnas_payroll_journal_report').report_action(self, data={
            'data_list': data,
            'employees_list': list_group,
            'company': self.env.user.company_id.name,
            'date_now': datetime.now().strftime("%d/%m/%Y"),
            'hour_now': datetime.now().strftime("%H:%M"),
            'date_start': self.payslip_run_id.date_start.strftime("%d/%m/%Y"),
            'date_end': self.payslip_run_id.date_end.strftime("%d/%m/%Y"),
            'nbr_employee': len(self.payslip_run_id.slip_ids.filtered(lambda p: p.state == 'done'))
        })


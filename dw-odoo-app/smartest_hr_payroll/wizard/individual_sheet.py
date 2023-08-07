# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time, calendar
from datetime import datetime

from odoo import api, fields, models


class IndividualSheet(models.TransientModel):
    _name = 'individual.sheet'
    _description = 'Individual Sheet'

    def _get_default_employee_id(self):
        return [(6, 0, self.env['hr.employee'].search([]).mapped('id'))]

    date_start = fields.Date(string="Date From", default=fields.Date.today().replace(day=1), required=True)
    date_end = fields.Date(string="Date End", required=True)
    payslip_run_id = fields.Many2one('hr.payslip.run', string='Payslip Batches')
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    payslip_ids = fields.Many2many('hr.payslip', string='Payslips', domain="[('state', '=', 'done')]")

    # *******************************Get employee payslips*****************************************
    @api.model
    def _get_payslips(self, date_start, date_end, employee_ids=None):
        domain = [
            ('date_start', '>=', date_start),
            ('date_end', '<=', date_end),
            ('state', '=', 'done'),
        ]
        if employee_ids:
            domain.append(
                ('employee_id', 'in', employee_ids.ids)
            )
        return self.env['hr.payslip'].search(domain)

    # ***********************************get months***************************************
    def _get_months(self, batch_ids):
        global months
        months = []
        for batch in batch_ids:
            date = batch.date_start.strftime("%y-%B-%d")
            month = datetime.strptime(str(date), '%y-%B-%d').strftime('%B-%y')
            months.append(month)

        return months

    # *************************************get payslip batches*********************************
    def _get_payslip_run_ids(self, date_start, date_end):
        domain = [
            ('date_start', '>=', date_start),
            ('date_end', '<=', date_end),
            ('state', '=','close'),
        ]

        return self.env['hr.payslip.run'].search(domain)

    # *********************************Prepare report data ************************************

    def data_by_batch(self, payslip_batches):

        salary_rules = self.env['hr.salary.rule'].search([]).filtered(
            lambda p: p.appears_on_payslip and p.sequence not in [506, 405, 406, 1500])
        data = []
        total_cotisation = 0
        cotisation = [0 for batch in payslip_batches]
        for rule in salary_rules:
            rule_name = 'Retenue IRG absence' if 601 == rule.sequence else rule.name
            rule_data = [rule.sequence, rule_name]
            total = 0
            index = 0
            for batch in payslip_batches:
                slip_lines = batch.slip_ids.filtered(
                    lambda p: p.state == 'done' and p.employee_id == self.employee_id).mapped(
                    'line_ids').filtered(lambda p: p.salary_rule_id.id == rule.id).mapped('total')
                total += round(abs(sum(slip_lines)), 2)
                if rule.sequence in [505,401,402, 403, 507,408, 409] and total_cotisation >= 0:
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

        #         Special allowances
        salary_rules = self.env['hr.salary.rule'].search([]).filtered(
            lambda p: p.sequence in [500, 505,401, 402, 403, 506, 405, 406, 507, 408, 409, 905, 1500])
        data2 = []
        total_employer_contribution = 0
        employer_contribution = [0 for batch in payslip_batches]
        for rule in salary_rules:
            rule_name2 = 'Salaire de poste' if 500 == rule.sequence else rule.name
            rule_data2 = [rule.sequence, rule_name2]
            total2 = 0
            index3 = 0
            for batch in payslip_batches:
                if rule.sequence == 905:
                    slip_lines = batch.slip_ids.filtered(
                        lambda p: p.state == 'done' and p.employee_id == self.employee_id).mapped(
                        'line_ids').filtered(lambda p: p.salary_rule_id.id == rule.id).mapped('amount')
                    total2 += round(abs(sum(slip_lines)), 2)
                else:
                    slip_lines = batch.slip_ids.filtered(
                        lambda p: p.state == 'done' and p.employee_id == self.employee_id).mapped(
                        'line_ids').filtered(lambda p: p.salary_rule_id.id == rule.id).mapped('total')
                    total2 += round(abs(sum(slip_lines)), 2)

                if rule.sequence in [506,405, 406] and total_employer_contribution >= 0:
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
        print([data, data2])
        return [data, data2]

    def print_report(self):
        parsed_ids = []
        data = []
        month_group = []

        payslip_batch_ids = (self._get_payslip_run_ids(self.date_start, self.date_end)).mapped('id')

        payslip_batches = self._get_payslip_run_ids(self.date_start, self.date_end).search(
            [('id', 'in', payslip_batch_ids), ('id', 'not in', parsed_ids)], limit=6)

        if len(payslip_batches):
            parsed_ids += payslip_batches.mapped('id')
            months = self._get_months(payslip_batches)
            month_group.append(months)
            data.append(self.data_by_batch(payslip_batches))
        while len(payslip_batches):
            payslip_batches = self._get_payslip_run_ids(self.date_start, self.date_end).search(
                [('id', 'in', payslip_batch_ids), ('id', 'not in', parsed_ids)], limit=6)
            if len(payslip_batches):
                parsed_ids += payslip_batches.mapped('id')
                months = self._get_months(payslip_batches)
                month_group.append(months)
                data.append(self.data_by_batch(payslip_batches))

        return self.env.ref('smartest_hr_payroll.individual_sheet_report').report_action(self, data={
        'data_list': data,
        'months_group': month_group,
        'employee': self.employee_id.name,
        'employee_number': self.employee_id.registration_number,
        'company': self.env.user.company_id.name,
        'date_now': datetime.now().strftime("%d/%m/%Y"),
        'hour_now': datetime.now().strftime("%H:%M"),
        'date_start': self.date_start.strftime("%d/%m/%Y"),
        'date_end': self.date_end.strftime("%d/%m/%Y")
    })



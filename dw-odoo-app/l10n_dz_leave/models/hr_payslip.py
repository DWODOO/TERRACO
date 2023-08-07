# -*- coding:utf-8 -*-

from datetime import datetime, time

from odoo import fields, models, api


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    is_leave_cumulated = fields.Boolean(
        'Leave already cumulated ?',
        readonly=True,
        store=True,
    )
    leave_days_count = fields.Float(
        'Leave days count',
        readonly=True,
        store=True,
    )
    leave_allowance = fields.Monetary(
        'Leave allowance',
        currency_field="company_currency",
        readonly=True,
        store=True,
    )
    leave_allowance_cumulation = fields.Monetary(
        'Leave allowance cumulation',
        currency_field="company_currency",
    )
    leave_ids = fields.Many2many(
        'hr.leave',
        string='Employee Leaves'
    )

    def _compute_leave_allowance_cumulation(self):
        for payslip in self:
            if payslip.employee_id and payslip.date_from and payslip.date_to:

                time_from = datetime.combine(payslip.date_from, time.min)
                time_to = datetime.combine(payslip.date_to, time.min)

                leaves = payslip.employee_id.leave_ids.filtered(
                    lambda
                        leave: leave.state == 'validate' and leave.date_from >= time_from and leave.date_to <= time_to and not leave.holiday_status_id.unpaid
                )
                payslip.leave_allowance_cumulation = 0
                payslip.leave_ids = False
                if leaves:
                    payslip.leave_ids = [(4, leave.id) for leave in leaves]
                    days_sum = sum(leaves.mapped('holiday_status_id.allocation_ids.number_of_days'))
                    allowance_sum = sum(leaves.mapped('holiday_status_id.allocation_ids.leave_allowance'))
                    payslip.leave_allowance_cumulation = allowance_sum / days_sum if days_sum != 0 else 0
            else:
                payslip.leave_ids = False
                payslip.leave_allowance_cumulation = 0

    # def _compute_leave_cumulation(self):
    #     for payslip in self:
    #         worked_days = (payslip.date_to - payslip.date_from).days
    #         if worked_days >= 2 and worked_days <= 10:
    #             payslip.leave_days_count = 1
    #
    #         elif worked_days >= 11 and worked_days <= 15:
    #                 payslip.leave_days_count = 1.5
    #         else:
    #             payslip.leave_days_count = 2.5
    #         if payslip.credit_note:
    #             payslip.leave_days_count *= -1
    #         payslip.leave_allowance = payslip.post_salary / 30 * payslip.leave_days_count

    def _compute_leave_cumulation(self):
        """
        # if start date of employee is set between the 1st of the month and the 15th (including 15th)
        # the employee wins its 2.5 leave days allocation else 0
        # if employee left the company and leave date between 1 st and 15th (15th not included)
        # the employee get 0 leave days, else he gains 2.5 leave days to be paid in the STC
        :return:
        """
        for payslip in self:
            try:
                worked_days = (payslip.date_to.replace(day=30) - payslip.date_from).days
            except:
                worked_days = (payslip.date_to.replace(day=28) - payslip.date_from).days

            if payslip.date_from.day > 15:
                payslip.leave_days_count = 0
            else:
                payslip.leave_days_count = 2.5
            payslip.leave_allowance = payslip.post_salary / 30 * payslip.leave_days_count

    def compute_sheet(self):
        self._compute_leave_allowance_cumulation()
        res = super(HrPayslip, self).compute_sheet()
        self._compute_leave_cumulation()
        return res

    @api.model
    def update_leave_lines(self, res, date_from, date_to):
        time_from = datetime.combine(date_from, time.min)
        time_to = datetime.combine(date_to, time.min)
        open_days = 0
        for line in res:
            if line.get('sequence', False) == 5:
                line['code'] = 'LEGAL_LEAVE'
                contract = self.env['hr.contract'].browse(line.get('contract_id'))
                employee = contract.employee_id
                leaves = employee.leave_ids.filtered(
                    lambda
                        leave: leave.state == 'validate' and leave.date_from >= time_from and leave.date_to <= time_to and not leave.holiday_status_id.unpaid
                )
                open_days += line['number_of_days']
                line['number_of_days'] = sum(leaves.mapped('number_of_days'))
        for line in res:
            if line.get('code', False) == 'PRES':
                line['number_of_days'] += open_days
                break
        return res

    @api.model
    def get_worked_day_lines(self, contracts, date_from, date_to):
        res = super(HrPayslip, self).get_worked_day_lines(contracts, date_from, date_to)
        return self.update_leave_lines(res, date_from, date_to)

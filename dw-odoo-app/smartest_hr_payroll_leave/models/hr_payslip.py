# -*- coding:utf-8 -*-

from datetime import  date, timedelta
import calendar

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    payroll_leave_ids = fields.Many2many('smartest.hr.payroll.leave.allowance',
                                         'payslip_payroll_leave_rel',
                                         'payslip_id',
                                         'payroll_leave_id',
                                         string='allowance Leave Exercice')

    def _get_1_12_per_exercice(self, payslip_id, leave_id, date_start_exercice, leave_days):
        SmartestPayrollLeaveAttributions = self.env['smartest.hr.payroll.leave.allowance.attributions']
        if not date_start_exercice :
            raise ValidationError("la date de début de L'exercice de La demande de congé est nulle ! ")
        date_end_exercice = fields.Date.from_string(str(date_start_exercice.year + 1) + '-06-30')
        LeavePayroll = self.env['smartest.hr.payroll.leave.allowance'].search([
            ('smartest_date_start_exercice', '<=', date_start_exercice),
            ('smartest_date_end_exercice', '>=', date_end_exercice),
            ('smartest_employee_id', '=', payslip_id.employee_id.id),
            ('smartest_active', '=', True)
        ])
        leave_allowance_per_exercice = 0

        if LeavePayroll.smartest_days_leave_attribution_exercice:
            leave_allowance_per_exercice = leave_days * LeavePayroll.smartest_leave_allowance_exercice / LeavePayroll.smartest_days_leave_attribution_exercice

            payslip_id.write({'payroll_leave_ids': [[6, 0, [LeavePayroll.id]]]})
            payroll_leave_attribution_ids = SmartestPayrollLeaveAttributions.search([
                ('smartest_leave_id', '=', leave_id)
            ])
            payroll_leave_attribution_ids.unlink()
            SmartestPayrollLeaveAttributions.create({
                'smartest_date_start_exercice': date_start_exercice,
                'smartest_date_end_exercice': date_end_exercice,
                'smartest_employee_id': payslip_id.employee_id.id,
                'payroll_leave_id': LeavePayroll.id,
                'smartest_leave_id': leave_id,
                'smartest_payslip_id': payslip_id.id,
                'smartest_days_attributed': leave_days,
                'smartest_leave_allowance_attributed': leave_allowance_per_exercice,
            })

        return leave_allowance_per_exercice

    @api.model
    def payroll_leave_allowance_cumulation(self, payslip):
        payslip_id = self.env['hr.payslip'].browse(payslip)
        work_entries = self.env['hr.work.entry'].search([
            ('date_stop', '<=', payslip_id.date_to),
            ('date_start', '>=', payslip_id.date_from),
            ('employee_id', '=', payslip_id.employee_id.id),
            ('work_entry_type_id.code', '=', "LEGAL_LEAVE"),
        ])
        leave_allowance = 0
        if work_entries:
            leave_exercice = []
            leave_ids = work_entries.leave_id

            for leave_id in leave_ids:
                leave_days = 0
                if payslip_id.contract_id.resource_calendar_id.hours_per_day:
                    leave_days = sum(work_entries.filtered(
                        lambda line: line.leave_id.holiday_allocation_id.id == leave_id.holiday_allocation_id.id).mapped(
                        "duration")) / payslip_id.contract_id.resource_calendar_id.hours_per_day
                leave_exercice.append(
                    {'leave_id': leave_id.id, 'exercice_start': leave_id.holiday_allocation_id.date_from,
                     'number_days': leave_days})

            for exercice in leave_exercice:
                leave_allowance += self._get_1_12_per_exercice(payslip_id, exercice["leave_id"],
                                                               exercice["exercice_start"],
                                                               exercice["number_days"])
        return leave_allowance

    # this method allows to calculate leave allowance while computing sheet (can be set for each client's demand)
    def _calculate_leave_allowance_per_payslip(self, payslip_line_ids):
        # GenericLab Case

        AssietteCotisableRuleId = self.env.ref('smartest_hr_payroll.salary_rule_assiette_cotisable').id
        AllowanceMealRuleId = self.env.ref('smartest_hr_payroll.salary_rule_allowance_meal').id
        AllowanceMealRegulGainRuleId = self.env.ref(
            'smartest_hr_payroll.salary_rule_allowance_meal_month_regulation_gain').id
        AllowanceMealRegulRestraintRuleId = self.env.ref(
            'smartest_hr_payroll.salary_rule_allowance_meal_month_regulation_restraint').id

        return ((1 / 12) * sum(payslip_line_ids.filtered(
            lambda
                line: line.salary_rule_id.id == AssietteCotisableRuleId or line.salary_rule_id.id == AllowanceMealRuleId or line.salary_rule_id.id == AllowanceMealRegulGainRuleId or line.salary_rule_id.id == AllowanceMealRegulRestraintRuleId).mapped(
            "total")))

    def _prepare_plan_allowance_leave_attribution(self, payslips, all_payroll_leave):
        for payslip in payslips:

            payslip_months = []
            date_from = payslip.date_from
            date_to = payslip.date_to
            smartest_allowance_leave_ids = all_payroll_leave.smartest_allowance_leave_ids.filtered(lambda line: (
                                          line.smartest_date_start.month >= date_from.month and line.smartest_date_end.month <= date_to.month)
                                           or line.smartest_payslip_id.id == payslip.id)
            smartest_allowance_leave_ids.unlink()

            payroll_leave_id = all_payroll_leave.filtered(
                lambda line: line.smartest_employee_id.id == payslip.employee_id.id)

            leave_allowance = self._calculate_leave_allowance_per_payslip(payslip.line_ids)
            if date_from.month != date_to.month:
                month_date = date(date_from.year, int(date_from.month), 1)
                date_end = month_date.replace(
                    day=calendar.monthrange(month_date.year, month_date.month)[1])
                payslip_months.append({
                    'smartest_date_start': date_from,
                    'smartest_date_end': date_end,
                    'smartest_leave_allowance': leave_allowance,
                    'smartest_payroll_leave_id': payroll_leave_id.id,
                    'smartest_payslip_id': payslip.id,
                })
                while date_end < date_to:
                    date_start_month = date_end + timedelta(days=1)
                    month_date = date(date_start_month.year, int(date_start_month.month), 1)
                    date_end = month_date.replace(
                        day=calendar.monthrange(month_date.year, month_date.month)[1])
                    payslip_months.append({
                        'smartest_date_start': date_start_month,
                        'smartest_date_end': date_end,
                        'smartest_leave_allowance': leave_allowance,
                        'smartest_payroll_leave_id': payroll_leave_id.id,
                        'smartest_payslip_id': payslip.id,

                    })
            else:

                payslip_months.append({
                    'smartest_date_start': date_from,
                    'smartest_date_end': date_to,
                    'smartest_leave_allowance': leave_allowance,
                    'smartest_payroll_leave_id': payroll_leave_id.id,
                    'smartest_payslip_id': payslip.id,
                })

            return payslip_months

    def _prepare_plan_allowance_leave(self, payslips, payroll_leave_ids):
        SmartestPayrollLeave = self.env['smartest.hr.payroll.leave.allowance']

        employee_without_leave_plan_allowance = list(
            set(payslips.mapped('employee_id')) - set(payroll_leave_ids.mapped('smartest_employee_id')))
        leave_plan_vals_list = []
        date_from = min(payslips.mapped('date_from'))
        year_start = SmartestPayrollLeave.sudo().get_exercice(date_from, start=True)
        year_end = SmartestPayrollLeave.sudo().get_exercice(date_from, start=False)
        for employee in employee_without_leave_plan_allowance:
            leave_plan_vals_list.append({
                'smartest_date_start_exercice': fields.Date.from_string(str(year_start) + '-07-01'),
                'smartest_date_end_exercice': fields.Date.from_string(str(year_end) + '-06-30'),
                'smartest_employee_id': employee.id,
            })
        return leave_plan_vals_list

    def action_payslip_done(self):
        AlgerianSalaryStructure = self.env.ref('smartest_hr_payroll.structure_base_dz').id
        payslips = self.filtered(
            lambda slip: slip.state not in ['cancel'] and slip.struct_id.id == AlgerianSalaryStructure)
        payroll_leave_attribution_ids = self.env['smartest.hr.payroll.leave.allowance.attributions'].search([
            ('smartest_payslip_id', 'in', payslips.ids)
        ])
        payroll_leave_attribution_ids.unlink()
        SmartestPayrollLeave = self.env['smartest.hr.payroll.leave.allowance']
        SmartestPayrollLeaveLine = self.env['smartest.hr.payroll.leave.allowance.line']

        all_payroll_leaves_that_exists = SmartestPayrollLeave.search([
            ('smartest_employee_id', 'in', payslips.mapped('employee_id').ids),
            ('smartest_date_start_exercice', '<=', min(payslips.mapped('date_from'))),
            ('smartest_date_end_exercice', '>=', max(payslips.mapped('date_to'))),
            ('smartest_active', '=', True),
        ])
        leave_plan_vals_list = self._prepare_plan_allowance_leave(payslips, all_payroll_leaves_that_exists)
        all_payroll_leaves = SmartestPayrollLeave.sudo().create(leave_plan_vals_list) + all_payroll_leaves_that_exists
        payslip_month = self._prepare_plan_allowance_leave_attribution(payslips, all_payroll_leaves)
        SmartestPayrollLeaveLine.sudo().create(payslip_month)
        res = super(HrPayslip, self).action_payslip_done()

        return res

    def unlink(self):

        payroll_leave_ids = self.env['smartest.hr.payroll.leave.allowance.line'].search([
            ('smartest_payslip_id', 'in', self.ids)
        ])
        payroll_leave_attribution_ids = self.env['smartest.hr.payroll.leave.allowance.attributions'].search([
            ('smartest_payslip_id', 'in', self.ids)
        ])
        payroll_leave_ids.unlink()
        payroll_leave_attribution_ids.unlink()
        return super().unlink()

    @api.model
    def action_payslip_analysis(self):
        domain = []

        if self.env.context.get('active_ids'):
            domain = [('payroll_leave_ids', 'in', self.env.context.get('active_ids', []))]

        return {
            'name': _('Payslip Analysis'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.payslip',
            'view_mode': 'tree,form',
            'search_view_id': self.env.ref('hr_payroll.view_hr_payslip_filter').id,
            'domain': domain,
            'context': {
                'search_default_group_by_batch': True,
            }
        }

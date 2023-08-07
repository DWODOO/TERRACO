# -*- coding: utf-8 -*-
# Part of SMARTEST ALGERIA
import calendar
from collections import defaultdict
from datetime import date

from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo.tools import format_date

# Import Odoo libs
from odoo import _, api, Command, fields, models

CodeIrgBAse = "R501"
RoundParam = 2


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    company_currency = fields.Many2one(
        'res.currency',
        string='Currency',
        related='company_id.currency_id',
        readonly=True,
    )
    payroll = fields.Monetary(
        'Masse Salariale',
        currency_field="company_currency",
        readonly=True,
        store=True,
        compute='compute_payroll_run'
    )
    net_wage = fields.Monetary(
        'Net salary',
        currency_field="company_currency",
        readonly=True,
        store=True,
        compute='compute_net_wage'
    )

    @api.depends('slip_ids')
    def compute_payroll_run(self):
        for run in self:
            run.payroll = sum(run.slip_ids.mapped('payroll'))

    @api.depends('slip_ids')
    def compute_net_wage(self):
        for run in self:
            run.net_wage = sum(run.slip_ids.mapped('net_wage'))

    @api.onchange('date_start')
    def onchange_date_start(self):
        if self.date_start:
            month_date = date(self.date_start.year, int(self.date_start.month), 1)
            self.date_end = month_date.replace(day=calendar.monthrange(month_date.year, month_date.month)[1])


class SmartestHrPayslip(models.Model):
    _inherit = 'hr.payslip'
    _order = "registration_number asc"

    department_id = fields.Many2one(
        'hr.department',
        related='employee_id.department_id',
        string='Department',
        store=True,
        readonly=True
    )

    smartest_amount_imposable_perfect = fields.Float(
        string="Perfect Imposable Amount",
        digits='Payroll'
    )
    smartest_theoretic_worked_days = fields.Float(
        string="Theoretic Worked Days",
        compute="_compute_worked_days_line_number_of_days"
    )
    smartest_worked_days = fields.Float(
        string="Real Worked Days",
        compute="_compute_worked_days_line_number_of_days"
    )
    smartest_weekend_days = fields.Float(
        string="Weekend Days",
        # store=1,
        # compute="_compute_worked_days_line_number_of_days"
    )
    smartest_theoretic_worked_hours = fields.Float(
        string="Theoretic Worked Hours",
        compute="_compute_worked_days_line_number_of_days"
    )
    smartest_worked_hours = fields.Float(
        string="Real Worked Hours",
        compute="_compute_worked_days_line_number_of_days"
    )
    smartest_company_currency = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        related='company_id.currency_id',
        readonly=True,
    )

    smartest_perfect_line_ids = fields.One2many(
        comodel_name='smartest.hr.payslip.line',
        inverse_name='slip_id',
        string='Perfect Payslip Lines',
        copy=True,
        store=True,
        compute="_compute_perfect_line_ids"
    )
    smartest_payslip_has_configurable_irg = fields.Boolean(
        string="Have Configurable IRG",
        compute="_compute_configurable_irg"
    )
    smartest_payslip_has_regul = fields.Boolean(
        string="Have Configurable Regul",
        compute="_compute_sheet_has_regul"
    )
    smartest_payslip_irg_type_applied = fields.Selection([
        ('bareme', 'IRG Barème'),
        ('abs', 'IRG Abs'),
    ], string='IRG Type',
        compute="_compute_sheet_irg_type",
        store=1, readonly=0
    )

    post_salary = fields.Monetary(
        'Post salary',
        currency_field="smartest_company_currency",
        readonly=True,
        store=True,
    )
    base_salary = fields.Monetary(
        'Base salary',
        currency_field="smartest_company_currency",
        readonly=True,
        store=True,
    )
    irg_base_salary = fields.Monetary(
        'IRG Base salary',
        currency_field="smartest_company_currency",
        readonly=True,
        store=True,
    )
    net_salary = fields.Monetary(
        'Net salary',
        currency_field="smartest_company_currency",
        readonly=True,
        store=True,
    )
    loan_refund_line_ids = fields.One2many(
        'hr.loan.refund.line',
        'payslip_id',
        string="Loan/Advance Refunds",
        readonly=True,
        store=True,
    )
    loan_refund_amount = fields.Monetary(
        'Loan refund amount',
        currency_field="smartest_company_currency",
        readonly=True,
        store=True,
    )
    advance_refund_amount = fields.Monetary(
        'Advance refund amount',
        currency_field="smartest_company_currency",
        readonly=True,
        store=True,
    )
    payroll = fields.Monetary(
        'Masse Salariale',
        currency_field="smartest_company_currency",
        readonly=True,
        store=True,
    )
    smartest_payroll_init = fields.Monetary(
        'Masse Salariale Initiale',
        currency_field="smartest_company_currency",
        readonly=True,
        store=True,
    )
    registration_number = fields.Char(
        "Registration Number",
        related="employee_id.registration_number",
        store=True
    )
    employee_marital = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('cohabitant', 'Legal Cohabitant'),
        ('widower', 'Widower'),
        ('divorced', 'Divorced')
    ], string='Marital Status',
    )
    employee_job_id = fields.Many2one(
        "hr.job",
        "Job",
    )
    employer_number = fields.Char(
        "Employer Number"
    )
    csp_cat = fields.Many2one(
        'hr.socioprofessional.categories.levels',
        related='contract_id.socio_professional_category_level_id')

    @api.onchange('struct_id', 'employee_id')
    def _onchange_contract(self):
        if self.contract_id not in self.contract_domain_ids:
            self.contract_id = None

    @api.depends('company_id', 'employee_id', 'date_from', 'date_to')
    def _compute_contract_domain_ids(self):
        HrContract = self.env['hr.contract']
        for record in self:
            record.contract_domain_ids = None
            domain = [('company_id', '=', record.company_id.id)]
            if record.employee_id:
                domain += [('employee_id', '=', record.employee_id.id)]
            if record.struct_id and not record.struct_id.smartest_is_stc:
                domain += [('state', '!=', 'cancel'), ('date_start', '<=', record.date_to), '|',
                           ('date_end', '>=', record.date_from), (
                               'date_end', '=', False)]
            record.contract_domain_ids = HrContract.search(domain)

    def compute_refunds(self):
        refund_line_obj = self.env['hr.loan.refund.line']
        for payslip in self:
            refunds = refund_line_obj.search([
                ('employee_id', '=', payslip.employee_id.id),
                ('payment_state', '=', 'waiting'),
                ('state', '=', 'confirmed'),
                ('date', '>=', payslip.date_from),
                ('date', '<=', payslip.date_to),
            ])
            payslip.loan_refund_line_ids = [(4, refund.id) for refund in refunds]
            payslip.loan_refund_amount = sum(
                refunds.filtered(lambda r: r.loan_id.type == 'loan').mapped('refund_amount')
            )
            payslip.advance_refund_amount = sum(
                refunds.filtered(lambda r: r.loan_id.type == 'advance').mapped('refund_amount')
            )

        return True

    def action_payslip_done(self):
        """Override this methode in order to validate refund lines"""
        res = super().action_payslip_done()
        self.mapped('loan_refund_line_ids').action_make_paid()
        return res

    @api.onchange('date_from')
    def onchange_date_from(self):
        if self.date_from:
            month_date = date(self.date_from.year, int(self.date_from.month), 1)
            self.date_to = month_date.replace(day=calendar.monthrange(month_date.year, month_date.month)[1])

    @api.depends('worked_days_line_ids', 'input_line_ids')
    def _compute_perfect_line_ids(self):
        if not self.env.context.get("payslip_no_recompute"):
            return
        for payslip in self.filtered(lambda p: p.smartest_perfect_line_ids and p.state in ['draft', 'verify']):
            payslip.smartest_perfect_line_ids = [(5, 0, 0)] + [(0, 0, line_vals) for line_vals in payslip.with_context(
                {'smartest_case_perfect': True})._get_payslip_lines()]

    @api.onchange('input_line_ids')
    def _compute_sheet_has_regul(self):
        for payslip in self:
            payslip_with_regul = payslip.input_line_ids.filtered(
                lambda input_line: input_line.input_type_id.smartest_is_regul)
            if payslip_with_regul:
                payslip.smartest_payslip_has_regul = True
            else:
                payslip.smartest_payslip_has_regul = False

    @api.depends('worked_days_line_ids', 'worked_days_line_ids.work_entry_type_id.smartest_payslip_irg_type_applied')
    def _compute_sheet_irg_type(self):
        for payslip in self:
            payslip_with_abs = payslip.worked_days_line_ids.filtered(
                lambda line: line.work_entry_type_id.smartest_payslip_irg_type_applied == "abs")
            if payslip_with_abs:
                payslip.smartest_payslip_irg_type_applied = 'abs'
            else:
                payslip.smartest_payslip_irg_type_applied = 'bareme'

    def get_worked_days_line_number_of_work_entry_type(self, work_entry_type):
        date_to = self.date_to
        date_from = self.date_from
        WorkEtry = self.env['hr.work.entry']
        work_entries = WorkEtry.search([
            ('date_stop', '<=', date_to),
            ('date_start', '>=', date_from),
            ('employee_id', '=', self.employee_id.id),
            ('work_entry_type_id.code', '=', work_entry_type.code),
        ])
        worked_days_line_ids = self.worked_days_line_ids
        if 'leave_id' in WorkEtry._fields:
            days_for_leave = 0
            leave_id = work_entries.leave_id
            for leave in leave_id:
                date_start_leave = date_from if leave.request_date_from < date_from else leave.request_date_from
                date_to_leave = date_to if date_to < leave.request_date_to else leave.request_date_to
                days_for_leave += (date_to_leave - date_start_leave).days
                days_for_leave += (date_to_leave - date_start_leave).days + 1
            worked_days_work_entry_type = worked_days_line_ids.filtered(
                lambda worked_day: worked_day.work_entry_type_id.code == work_entry_type.code)
            worked_days_work_entry_type_days = worked_days_work_entry_type.mapped('number_of_days')
            worked_days_work_entry_type_hours = worked_days_work_entry_type.mapped('number_of_hours')
            contract_id = self.contract_id
            if leave_id:
                if contract_id.paid_hourly_attendance:
                    return abs(
                        days_for_leave * contract_id.resource_calendar_id.hours_per_day - worked_days_work_entry_type_hours)
                return abs(days_for_leave - worked_days_work_entry_type_days)
        return 0

    @api.onchange('worked_days_line_ids')
    def _compute_worked_days_line_number_of_days(self):
        for payslip in self:
            total_days = 0
            total_hours = 0
            worked_days_line_ids = payslip.worked_days_line_ids
            work100 = worked_days_line_ids.filtered(
                lambda worked_day: worked_day.work_entry_type_id.code == "WORK100")
            contract_id = payslip.contract_id
            resource_calendar_id = contract_id.resource_calendar_id
            WORK100_days = work100.number_of_days
            WORK100_hours = work100.number_of_hours

            for line in worked_days_line_ids:
                if not line.work_entry_type_id.smartest_paid_in_addition and not line.work_entry_type_id.smartest_paid_in_sub and not line.work_entry_type_id.smartest_weekend_days:
                    total_days += line.number_of_days
                    total_hours += line.number_of_hours
                elif line.work_entry_type_id.smartest_paid_in_sub:
                    line.number_of_days = -abs(line.number_of_days)
                    line.number_of_hours = -abs(line.number_of_hours)

            days_off_work = total_days - WORK100_days
            hours_off_work = total_hours - WORK100_hours

            if resource_calendar_id.smartest_calendar_forced:
                work100.number_of_days = WORK100_days = round(
                    resource_calendar_id.smartest_number_days_forced - days_off_work, RoundParam)
                work100.number_of_hours = WORK100_hours = round(
                    resource_calendar_id.full_time_required_hours * 52 / 12 - hours_off_work, RoundParam)

            payslip.smartest_worked_days = WORK100_days
            payslip.smartest_worked_hours = WORK100_hours
            payslip.smartest_theoretic_worked_days = round(WORK100_days + days_off_work, RoundParam)
            payslip.smartest_theoretic_worked_hours = total_hours = round(WORK100_hours + hours_off_work, RoundParam)
            for line in worked_days_line_ids:

                if not contract_id.paid_hourly_attendance and line.work_entry_type_id.smartest_hourly_paid:
                    if payslip.wage_type == "monthly":
                        amount = round(contract_id.wage / total_hours * line.number_of_hours, RoundParam)
                    else:
                        amount = round(contract_id.hourly_wage * line.number_of_hours, RoundParam)
                    line.amount = amount
            work_entries_days_weekend = worked_days_line_ids.filtered(
                lambda worked_day: worked_day.work_entry_type_id.smartest_get_weekend_days)
            weekend_days = 0
            for type in work_entries_days_weekend:
                weekend_days += payslip.get_worked_days_line_number_of_work_entry_type(type)
            smartest_weekend_days = worked_days_line_ids.filtered(
                lambda worked_day: worked_day.work_entry_type_id.smartest_weekend_days)
            weekend_days = sum(
                smartest_weekend_days.mapped("number_of_days")) if not weekend_days and smartest_weekend_days else 0
            payslip.smartest_weekend_days = weekend_days

    @api.onchange('input_line_ids')
    def _compute_configurable_irg(self):
        for payslip in self:
            payslip_with_configurable_irg = payslip.input_line_ids.filtered(
                lambda input_line: input_line.input_type_id.smartest_configurable_irg)
            if payslip_with_configurable_irg:
                payslip.smartest_payslip_has_configurable_irg = True
            else:
                payslip.smartest_payslip_has_configurable_irg = False

    @api.onchange('input_line_ids')
    def _onchange_input_line_ids_manual_irg_amount(self):
        for payslip in self:
            for line in payslip.input_line_ids:
                if line.smartest_auto_irg:
                    R501 = line.amount * 0.91
                    if not line.smartest_irg_prorata:

                        line.smartest_manual_irg_amount = abs(
                            self.env['hr.salary.rule'].calculate_irg(abs(R501), payslip.date_to))
                    else:
                        ai_parfait = payslip.contract_id.wage * 0.91
                        irg_parfait = abs(
                            self.env['hr.salary.rule'].calculate_irg(ai_parfait, payslip.date_to))
                        line.smartest_manual_irg_amount = R501 * irg_parfait / ai_parfait if ai_parfait else 0

    @api.onchange('input_line_ids','input_line_ids.smartest_paid_in_days', 'input_line_ids.smartest_paid_in_hours',
                  'input_line_ids.smartest_number_of_days', 'input_line_ids.smartest_number_of_hours')
    def _onchange_amount_manual_irg(self):
        for payslip in self:
            contract_id = payslip.contract_id
            for line in payslip.input_line_ids:
                amount = 0
                if line.smartest_auto_irg:

                    if line.smartest_paid_in_days:
                        amount = contract_id.wage / 30 * line.smartest_number_of_days
                    elif line.smartest_paid_in_hours:
                        amount = contract_id.wage / 173.33 * line.smartest_paid_in_hours

                line.amount = amount

    def compute_resume(self):
        payslips = self.filtered(lambda slip: slip.state in ['draft', 'verify'])
        for payslip in payslips:
            LineIds = payslip.mapped('line_ids')

            assiette_cot = sum(
                LineIds.filtered(
                    lambda
                        line: not line.salary_rule_id.smartest_is_ss and (
                            line.category_id.smartest_category_type == 'contribution' or line.category_id.smartest_category_type == 'contribution_10')
                ).mapped('total')
            )

            if assiette_cot <= 0:
                payslip.post_salary = assiette_cot = 0
            else:
                payslip.post_salary = assiette_cot

            assiette_imp = sum(
                LineIds.filtered(
                    lambda
                        line: line.salary_rule_id.smartest_is_ss or (not line.salary_rule_id.smartest_is_irg and (
                            line.category_id.smartest_category_type == 'taxable' or line.category_id.smartest_category_type == 'taxable_10'))
                ).mapped('total')
            ) + assiette_cot

            if assiette_imp <= 0:
                payslip.irg_base_salary = assiette_imp = 0
            else:
                payslip.irg_base_salary = assiette_imp

            net = sum(
                LineIds.filtered(
                    lambda line: line.category_id.smartest_category_type == 'net'
                ).mapped('total')
            )

            if net <= 0:
                payslip.net_salary = 0
            else:
                payslip.net_salary = net

            payslip.smartest_payroll_init = somme_initial = sum(map(abs,
                                                                    LineIds.filtered(
                                                                        lambda
                                                                            line: line.category_id.smartest_category_type == 'ni_impo_ni_coti'
                                                                    ).mapped(
                                                                        'total'))) + assiette_imp + assiette_cot * payslip.employee_id.cnas_salary_contribution / 100
            payslip.payroll = somme_initial * 1.04 + assiette_cot * payslip.employee_id.cnas_patronage_contribution / 100

    def compute_sheet(self):
        self.compute_refunds()
        payslips = self.filtered(lambda slip: slip.state in ['draft', 'verify'])
        # delete old payslip lines
        payslips.smartest_perfect_line_ids.unlink()
        SalaryRule = self.env['hr.salary.rule']
        for payslip in payslips:
            payslip_amount_perfect = 0
            lines_perfect = []
            for line in payslip.with_context(smartest_case_perfect=True)._get_payslip_lines():
                salary_rule_id = SalaryRule.browse(line['salary_rule_id'])
                lines_perfect.append(Command.create(line))
                if salary_rule_id.code == "R501_perfect":
                    payslip_amount_perfect = line["amount"] * line["quantity"] * line["rate"] / 100

            payslip.write({
                'smartest_amount_imposable_perfect': payslip_amount_perfect,
                'smartest_perfect_line_ids': lines_perfect,
            })
        res = super(SmartestHrPayslip, self).compute_sheet()
        self.compute_resume()
        return res

    def _get_worked_day_lines(self, domain=None, check_out_of_contract=True):
        """
        :returns: a list of dict containing the worked days values that should be applied for the given payslip
        """
        res = []
        # fill only if the contract as a working schedule linked
        self.ensure_one()
        contract = self.contract_id

        if contract.resource_calendar_id:
            res = self._get_worked_day_lines_values(domain=domain)

            if not check_out_of_contract:
                return res

            # If the contract doesn't cover the whole month, create
            # worked_days lines to adapt the wage accordingly
            out_days, out_hours = 0, 0
            worked_previous_days_contract = 0
            worked_previous_hours_contract = 0
            reference_calendar = self._get_out_of_contract_calendar()
            contract_ids = self.employee_id.contract_ids.filtered(lambda
                                                                      cntrct: cntrct.id != contract.id and cntrct.state != 'cancel' and cntrct.date_end and self.date_to >= cntrct.date_end >= self.date_from)

            if self.date_from < contract.date_start:

                start = fields.Datetime.to_datetime(self.date_from)
                for previous_contract in contract_ids:
                    end_previous = fields.Datetime.to_datetime(previous_contract.date_end) + relativedelta(days=1)

                    if previous_contract.date_end and previous_contract.date_start.month == previous_contract.date_end.month:
                        ref = reference_calendar.get_work_duration_data(
                            fields.Datetime.to_datetime(self.date_from), end_previous
                            , compute_leaves=False,
                            domain=['|', ('work_entry_type_id', '=', False), (
                                'work_entry_type_id.is_leave', '=', False)])
                        worked_previous_days_contract += ref['days']
                        worked_previous_hours_contract += ref['hours']
                    else:
                        ref = reference_calendar.get_work_duration_data(
                            fields.Datetime.to_datetime(self.date_from), end_previous, compute_leaves=False,
                            domain=['|', ('work_entry_type_id', '=', False), (
                                'work_entry_type_id.is_leave', '=', False)])
                        worked_previous_days_contract += ref['days']
                        worked_previous_hours_contract += ref['hours']

                stop = fields.Datetime.to_datetime(contract.date_start) + relativedelta(days=-1, hour=23, minute=59)
                out_time = reference_calendar.get_work_duration_data(start, stop, compute_leaves=False,
                                                                     domain=['|', ('work_entry_type_id', '=', False), (
                                                                         'work_entry_type_id.is_leave', '=', False)])
                out_days += out_time['days']
                out_hours += out_time['hours']
            if contract.date_end and contract.date_end < self.date_to:
                start = fields.Datetime.to_datetime(contract.date_end) + relativedelta(days=1)
                stop = fields.Datetime.to_datetime(self.date_to) + relativedelta(hour=23, minute=59)
                out_time = reference_calendar.get_work_duration_data(start, stop, compute_leaves=False,
                                                                     domain=['|', ('work_entry_type_id', '=', False), (
                                                                         'work_entry_type_id.is_leave', '=', False)])
                out_days += out_time['days']
                out_hours += out_time['hours']

            if out_days or out_hours:
                work_entry_type = self.env.ref('hr_payroll.hr_work_entry_type_out_of_contract')
                res.append({
                    'sequence': work_entry_type.sequence,
                    'work_entry_type_id': work_entry_type.id,
                    'number_of_days': out_days - worked_previous_days_contract,
                    'number_of_hours': out_hours - worked_previous_hours_contract,
                })

        return res

    def _get_worked_day_lines_values(self, domain=None):
        self.ensure_one()
        res = []
        work_hours = self.contract_id._get_work_hours(self.date_from, self.date_to, domain=domain)
        contract_ids = self.employee_id.contract_ids.filtered(lambda
                                                                  cntrct: cntrct.id != self.contract_id.id and cntrct.state != 'cancel' and cntrct.date_end and self.date_to >= cntrct.date_end >= self.date_from)

        hours_per_day = self._get_worked_day_lines_hours_per_day()
        for contract in contract_ids:
            for key, value in contract._get_work_hours(self.date_from, self.date_to, domain=domain).items():
                if key in work_hours.keys():
                    work_hours[key] += value
                else:
                    work_hours[key] = value

        work_hours_ordered = sorted(work_hours.items(), key=lambda x: x[1])
        biggest_work = work_hours_ordered[-1][0] if work_hours_ordered else 0
        add_days_rounding = 0
        for work_entry_type_id, hours in work_hours_ordered:
            work_entry_type = self.env['hr.work.entry.type'].browse(work_entry_type_id)
            days = round(hours / hours_per_day, 5) if hours_per_day else 0
            if work_entry_type_id == biggest_work:
                days += add_days_rounding
            day_rounded = self._round_days(work_entry_type, days)
            add_days_rounding += (days - day_rounded)
            attendance_line = {
                'sequence': work_entry_type.sequence,
                'work_entry_type_id': work_entry_type_id,
                'number_of_days': day_rounded,
                'number_of_hours': hours,
            }
            res.append(attendance_line)
        return res


class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    def _filter_contracts(self, contracts):

        return contracts

    def compute_sheet(self):
        self.ensure_one()
        if not self.env.context.get('active_id'):
            from_date = fields.Date.to_date(self.env.context.get('default_date_start'))
            end_date = fields.Date.to_date(self.env.context.get('default_date_end'))
            today = fields.date.today()
            first_day = today + relativedelta(day=1)
            last_day = today + relativedelta(day=31)
            if from_date == first_day and end_date == last_day:
                batch_name = from_date.strftime('%B %Y')
            else:
                batch_name = _('From %s to %s', format_date(self.env, from_date), format_date(self.env, end_date))
            payslip_run = self.env['hr.payslip.run'].create({
                'name': batch_name,
                'date_start': from_date,
                'date_end': end_date,
            })
        else:
            payslip_run = self.env['hr.payslip.run'].browse(self.env.context.get('active_id'))

        employees = self.with_context(active_test=False).employee_ids
        if not employees:
            raise UserError(_("You must select employee(s) to generate payslip(s)."))

        # Prevent a payslip_run from having multiple payslips for the same employee
        employees -= payslip_run.slip_ids.employee_id
        success_result = {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.payslip.run',
            'views': [[False, 'form']],
            'res_id': payslip_run.id,
        }
        if not employees:
            return success_result

        Payslip = self.env['hr.payslip']
        contracts = employees._get_contracts(
            payslip_run.date_start, payslip_run.date_end, states=['open', 'close']
        ).filtered(lambda c: c.active and (
                (c.leave and c.leave_date and c.leave_date >= payslip_run.date_start) or not c.leave))
        contracts._generate_work_entries(payslip_run.date_start, payslip_run.date_end)
        work_entries = self.env['hr.work.entry'].search([
            ('date_start', '<=', payslip_run.date_end),
            ('date_stop', '>=', payslip_run.date_start),
            ('employee_id', 'in', employees.ids),
        ])
        self._check_undefined_slots(work_entries, payslip_run)

        if (self.structure_id.type_id.default_struct_id == self.structure_id):
            work_entries = work_entries.filtered(lambda work_entry: work_entry.state != 'validated')
            if work_entries._check_if_error():
                work_entries_by_contract = defaultdict(lambda: self.env['hr.work.entry'])

                for work_entry in work_entries.filtered(lambda w: w.state == 'conflict'):
                    work_entries_by_contract[work_entry.contract_id] |= work_entry

                for contract, work_entries in work_entries_by_contract.items():
                    conflicts = work_entries._to_intervals()
                    time_intervals_str = "\n - ".join(['', *["%s -> %s" % (s[0], s[1]) for s in conflicts._items]])
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Some work entries could not be validated.'),
                        'message': _('Time intervals to look for:%s', time_intervals_str),
                        'sticky': False,
                    }
                }

        default_values = Payslip.default_get(Payslip.fields_get())
        payslips_vals = []
        for contract in contracts:
            contract_taken = True
            if contract.state == "close":
                cntrcts = contract.employee_id.contract_ids.filtered(
                    lambda
                        c: c.active and c.state == "open" and c.date_start >= payslip_run.date_start and c.date_start.month == payslip_run.date_start.month)
                if cntrcts:
                    contract_taken = False

            if contract_taken:
                values = dict(default_values, **{
                    'name': _('New Payslip'),
                    'employee_id': contract.employee_id.id,
                    # 'credit_note': payslip_run.credit_note,
                    'payslip_run_id': payslip_run.id,
                    'date_from': payslip_run.date_start,
                    'date_to': payslip_run.date_end,
                    'contract_id': contract.id,
                    'struct_id': self.structure_id.id or contract.structure_type_id.default_struct_id.id,
                })
                payslips_vals.append(values)
        payslips = Payslip.with_context(tracking_disable=True).create(payslips_vals)
        payslips._compute_name()
        payslips.compute_sheet()
        payslip_run.state = 'verify'

        return success_result

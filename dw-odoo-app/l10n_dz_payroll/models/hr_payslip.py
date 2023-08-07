# -*- coding:utf-8 -*-
import calendar
import pdb
from datetime import datetime, time

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


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

    @api.depends('slip_ids')
    def compute_payroll_run(self):
        for run in self:
            run.payroll = sum(run.slip_ids.mapped('payroll'))


class HrPayslipInputType(models.Model):
    _inherit = 'hr.payslip.input.type'

    name = fields.Char(
        translate=True
    )


class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    department_id = fields.Many2one(
        'hr.department',
        related='employee_id.department_id',
        store=True
    )
    name = fields.Char(
        translate=True
    )

    def _get_payslip_lines(self):
        res = super(HrPayslipLine, self)._get_payslip_lines()
        pdb.set_trace()


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        store=True,
        readonly=True
    )

    csp_cat = fields.Many2one(
        'hr.socioprofessional.categories.levels',
        string='socio',
        store=True,
        readonly=True
    )

    company_currency = fields.Many2one(
        'res.currency',
        string='Currency',
        related='company_id.currency_id',
        readonly=True,
    )

    post_salary = fields.Monetary(
        'Post salary',
        currency_field="company_currency",
        readonly=True,
        store=True,
    )
    base_salary = fields.Monetary(
        'Base salary',
        currency_field="company_currency",
        readonly=True,
        store=True,
    )
    irg_base_salary = fields.Monetary(
        'IRG Base salary',
        currency_field="company_currency",
        readonly=True,
        store=True,
    )
    net_salary = fields.Monetary(
        'Net salary',
        currency_field="company_currency",
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
        currency_field="company_currency",
        readonly=True,
        store=True,
    )
    advance_refund_amount = fields.Monetary(
        'Advance refund amount',
        currency_field="company_currency",
        readonly=True,
        store=True,
    )
    payroll = fields.Monetary(
        currency_field="company_currency",
        readonly=True,
        store=True,
    )
    smartest_to_send = fields.Boolean(
        'Send by email?'
    )
    employee_marital = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('cohabitant', 'Legal Cohabitant'),
        ('widower', 'Widower'),
        ('divorced', 'Divorced')],
        string='Marital Status',
        store=True
    )
    employee_job_id = fields.Many2one(
        "hr.job",
        "Job",
        store=True
    )
    employer_number = fields.Many2one(
        'res.company.cnas',
        "Employer Number",
        store=True
    )

    @api.onchange('date_from')
    def _onchange_date_from(self):
        if self.date_from:
            self.date_to = self.date_from.replace(
                day=calendar.monthrange(self.date_from.year, self.date_from.month)[1],
                month=self.date_from.month
            )

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

    def compute_resume(self):
        for payslip in self:
            payslip.base_salary = sum(
                payslip.mapped('line_ids').filtered(
                    lambda line: line.salary_rule_id.is_base_salary
                ).mapped('total')

            )

            payslip.post_salary = sum(
                payslip.mapped('line_ids').filtered(
                    lambda line: line.salary_rule_id.is_post_salary
                ).mapped('total')
            )
            payslip.irg_base_salary = sum(
                payslip.mapped('line_ids').filtered(
                    lambda line: line.salary_rule_id.is_irg_base_salary
                ).mapped('total')
            )
            payslip.net_salary = sum(
                payslip.mapped('line_ids').filtered(
                    lambda line: line.salary_rule_id.is_net_salary
                ).mapped('total')
            )

    def get_salary_rules(self):
        salary_rule_cat = self.env.ref('l10n_dz_payroll.NCNI')
        salary_rule = self.env['hr.salary.rule'].search([('category_id.id','=',salary_rule_cat.id)])
        salary_rule_values = []
        for rec in salary_rule:
            salary_rule_values.append(rec.code)
        salary_rule_values += ["R401", "R501"]
        return salary_rule_values

    def _compute_payroll(self):
        for payslip in self:
            sum_payroll = sum(map(abs,
                payslip.line_ids.filtered(lambda o: o if o.code in self.get_salary_rules()
                else None).mapped('total')
            ))
            sum_payroll = sum_payroll * 1.04
            sum_payroll += sum(map(abs,
                                 payslip.line_ids.filtered(
                                     lambda o: o if o.code in ["R404"]
                                     else None).mapped('total')
                                 ))
            payslip.payroll = sum_payroll

    def compute_sheet(self):
        self.compute_refunds()
        res = super(HrPayslip, self).compute_sheet()
        self.compute_resume()
        self._compute_payroll()
        # self.mapped('line_ids').filtered(lambda line: not line.appears_on_payslip).unlink()
        return res

    def update_department(self):
        for r in self:
            r.department_id = r.employee_id.department_id

    @api.model
    def get_additional_hours(self, contracts, date_from, date_to):
        day_from = datetime.combine(fields.Date.from_string(date_from), time.min)
        day_to = datetime.combine(fields.Date.from_string(date_to), time.max)
        hours = []
        for contract in contracts:
            employee = contract.employee_id
            hours_ids = self.env['hr.additional.working.hours.line'].search([
                ('employee_id', '=', employee.id),
                ('state', '=', 'confirmed'),
                ('date_from', '>=', day_from),
                ('date_to', '<=', day_to),
            ])
            h50 = sum(hours_ids.mapped('h50'))
            h75 = sum(hours_ids.mapped('h75'))
            h100 = sum(hours_ids.mapped('h100'))
            if h50 > 0:
                hours.append({
                    'work_entry_type_id': self.env.ref('l10n_dz_payroll.hr_additional_hours50_work_entry', False),
                    'number_of_days': 0.0,
                    'number_of_hours': sum(hours_ids.mapped('h50')),
                    'contract_id': contract.id
                })
            if h75 > 0:
                hours.append({
                    'work_entry_type_id': self.env.ref('l10n_dz_payroll.hr_additional_hours100_work_entry', False),
                    'number_of_days': 0.0,
                    'number_of_hours': sum(hours_ids.mapped('h75')),
                    'contract_id': contract.id,
                })
            if h100 > 0:
                hours.append({
                    'work_entry_type_id': self.env.ref('l10n_dz_payroll.hr_additional_hours150_work_entry', False),
                    'number_of_days': 0.0,
                    'number_of_hours': sum(hours_ids.mapped('h100')),
                    'contract_id': contract.id,
                })
        return hours

    @api.model
    def get_worked_day_lines(self, contracts, date_from, date_to):
        res = super(HrPayslip, self).get_worked_day_lines(contracts, date_from, date_to)
        res.extend(self.get_additional_hours(contracts, date_from, date_to))
        return res

    def action_payslip_done(self):
        """Override this methode in order to accept validation of out of date contract"""
        # invalid_payslips = self.filtered(lambda p: p.contract_id and (p.contract_id.date_start > p.date_to or (
        #             p.contract_id.date_end and p.contract_id.date_end < p.date_from)))
        # if invalid_payslips:
        #     raise ValidationError(_('The following employees have a contract outside of the payslip period:\n%s',
        #                             '\n'.join(invalid_payslips.mapped('employee_id.name'))))
        if any(slip.contract_id.state == 'cancel' for slip in self):
            raise ValidationError(_('You cannot valide a payslip on which the contract is cancelled'))
        if any(slip.state == 'cancel' for slip in self):
            raise ValidationError(_("You can't validate a cancelled payslip."))
        self.write({'state': 'done'})

        line_values = self._get_line_values(['NET'])

        self.filtered(lambda p: not p.credit_note and line_values['NET'][p.id]['total'] < 0).write(
            {'has_negative_net_to_report': True})
        self.mapped('payslip_run_id').action_close()
        # Validate work entries for regular payslips (exclude end of year bonus, ...)
        regular_payslips = self.filtered(lambda p: p.struct_id.type_id.default_struct_id == p.struct_id)
        work_entries = self.env['hr.work.entry']
        for regular_payslip in regular_payslips:
            work_entries |= self.env['hr.work.entry'].search([
                ('date_start', '<=', regular_payslip.date_to),
                ('date_stop', '>=', regular_payslip.date_from),
                ('employee_id', '=', regular_payslip.employee_id.id),
            ])
        if work_entries:
            work_entries.action_validate()

        if self.env.context.get('payslip_generate_pdf'):
            if self.env.context.get('payslip_generate_pdf_direct'):
                self._generate_pdf()
            else:
                self.write({'queued_for_pdf': True})
                payslip_cron = self.env.ref('hr_payroll.ir_cron_generate_payslip_pdfs', raise_if_not_found=False)
                if payslip_cron:
                    payslip_cron._trigger()

        self.mapped('loan_refund_line_ids').action_make_paid()

        # return super(HrPayslip, self).action_payslip_done()

    def _get_worked_day_lines(self):
        res = super(HrPayslip, self)._get_worked_day_lines()
        default_work_entry_type = self.contract_id.structure_type_id.default_work_entry_type_id

        # Additional working hours
        contract = self.employee_id._get_contracts(self.date_from, self.date_to)
        res.extend(self.get_additional_hours(contract, self.date_from, self.date_to))
        # Worked days 100%
        for r in res:
            if r.get('work_entry_type_id') == default_work_entry_type.id:
                r['number_of_days'] = self.contract_id.days_per_month
                r['number_of_hours'] = self.contract_id.hours_per_month
                break
        return res

    @api.model
    def create(self, vals):
        employee_id = self.env['hr.employee'].browse(vals['employee_id'])
        contract_id = self.env['hr.contract'].browse(vals['contract_id'])
        vals['employee_marital'] = employee_id.marital
        vals['department_id'] = contract_id.department_id.id
        vals['employer_number'] = employee_id.company_cnas_id.id
        vals['employee_job_id'] = contract_id.job_id.id
        vals['csp_cat'] = contract_id.socio_professional_category_level_id
        res = super(HrPayslip, self).create(vals)
        return res



# -*- coding: utf-8 -*-
# Part of SMARTEST ALGERIA

# Import Odoo libs
from odoo import api, fields, models


class SmartestHrPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    smartest_manual_irg_amount = fields.Float(
        string="IRG amount",
        digits='Payroll'
    )
    smartest_number_of_days = fields.Float(
        string="Days",
    )
    smartest_number_of_hours = fields.Float(
        string="Hours",
    )
    smartest_auto_irg = fields.Boolean(string="Automatic IRG", store=True, readonly=False,
                                               related="input_type_id.smartest_auto_irg")
    smartest_paid_in_calendar = fields.Boolean(string="Paid in Calendar", store=True, readonly=False,
                                               related="input_type_id.smartest_paid_in_calendar")
    smartest_irg_prorata = fields.Boolean(string="Paid in Calendar", store=True, readonly=False,
                                               related="input_type_id.smartest_irg_prorata")
    smartest_configurable_irg = fields.Boolean(related="input_type_id.smartest_configurable_irg", store=True)
    smartest_paid_in_hours = fields.Boolean(related="input_type_id.smartest_paid_in_hours", store=True)
    smartest_paid_in_days = fields.Boolean(related="input_type_id.smartest_paid_in_days", store=True)


class SmartestHrPayslipInputType(models.Model):
    _inherit = 'hr.payslip.input.type'

    smartest_configurable_irg = fields.Boolean(string="Configurable IRG", default=False)
    name = fields.Char(translate=True)
    smartest_is_regul = fields.Boolean(string="IS Regulation", default=False)
    smartest_paid_in_calendar = fields.Boolean(string="Paid in Calendar")
    smartest_paid_in_hours = fields.Boolean(string="Paid in Hours")
    smartest_paid_in_days = fields.Boolean(string="Paid in Days")
    smartest_auto_irg = fields.Boolean(string="Automatic IRG", default=False)
    smartest_irg_prorata = fields.Boolean(string="IRG prorata", default=False)

    @api.model
    def create(self, vals):
        vals['code'] = self.env['ir.sequence'].next_by_code('hr.input.code.sequence')
        return super(SmartestHrPayslipInputType, self).create(vals)

    @api.onchange('smartest_paid_in_hours')
    def _onchange_smartest_paid_in_hours(self):
        if self.smartest_paid_in_hours:
            self.smartest_paid_in_days = False

    @api.onchange('smartest_paid_in_days')
    def _onchange_smartest_paid_in_days(self):
        if self.smartest_paid_in_days:
            self.smartest_paid_in_hours = False


class HrWorkEntryRegenerationWizard(models.TransientModel):
    _inherit = 'hr.work.entry.regeneration.wizard'

    employee_id = fields.Many2one('hr.employee', 'Employee', required=False)

    def regenerate_work_entries(self):
        return super(HrWorkEntryRegenerationWizard, self).regenerate_work_entries()

    def regenerate_work_entries_employee_ids(self):
        self.ensure_one()

        date_from = max(self.date_from,
                        self.earliest_available_date) if self.earliest_available_date else self.date_from
        date_to = min(self.date_to, self.latest_available_date) if self.latest_available_date else self.date_to
        employee_ids = self.env['hr.employee'].search([
            ('contract_id.date_start', '<=', date_to), ('contract_id.state', '!=', 'cancel'), ])
        for employee_id in employee_ids:
            work_entries = self.env['hr.work.entry'].search([
                ('employee_id', '=', employee_id.id),
                ('date_stop', '>=', date_from),
                ('date_start', '<=', date_to),
                ('state', '!=', 'validated')])

            work_entries.write({'active': False})
            employee_id.generate_work_entries(date_from, date_to, True)
        action = self.env["ir.actions.actions"]._for_xml_id('hr_work_entry.hr_work_entry_action')
        return action

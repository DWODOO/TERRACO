# -*- coding: utf-8 -*-
# Part of SMARTEST ALGERIA

# Import Odoo libs
from odoo import fields, models


class HrPayrollAccount(models.TransientModel):
    _name = 'hr.payroll.account'

    payslip_run_id = fields.Many2one(
        'hr.payslip.run',
        string='Journal'
    )
    date_from = fields.Date(
        string='From',
        readonly=True
    )
    date_to = fields.Date(
        string='To',
        readonly=True
    )

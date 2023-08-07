# -*- coding: utf-8 -*-
# Part of SMARTEST ALGERIA

# Import Odoo libs
from odoo import models


class SmartestHrPayslipLine(models.Model):
    _name = 'smartest.hr.payslip.line'
    _inherit = 'hr.payslip.line'
    _description = 'Smartest Payslip Line'
    _order = 'contract_id, sequence, code'

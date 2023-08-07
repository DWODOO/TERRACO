# -*- coding:utf-8 -*-
import calendar
from datetime import datetime, time

from odoo import api, fields, models, _


class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    def _get_available_contracts_domain(self):
        return [('contract_ids.state', '=', 'open'), ('company_id', '=', self.env.company.id)]

# -*- coding: utf-8 -*-
# Part of SMARTEST ALGERIA

# Import Odoo libs
from odoo import api, fields, models


class SmartestHrPayrollStructure(models.Model):
    _inherit = "hr.payroll.structure"

    rule_ids = fields.Many2many(
        comodel_name='hr.salary.rule',
        relation='smartest_rule_struct_rel',
        column1='struct_id',
        column2='rule_id',
        string='Salary Rules'
    )
    smartest_is_stc = fields.Boolean(
        string="Is STC",
        default=False
    )

    def _get_default_rule_ids(self):
        return []

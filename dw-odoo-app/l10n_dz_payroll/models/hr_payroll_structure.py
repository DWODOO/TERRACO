# -*- coding:utf-8 -*-

from odoo import fields, models


class HrPayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'

    rule_ids = fields.Many2many(
        'hr.salary.rule',
        'payroll_structure_rule_rel',
        'struct_id',
        'rule_id',
        string='Salary Rules'
    )

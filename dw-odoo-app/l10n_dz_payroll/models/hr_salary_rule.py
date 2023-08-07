# -*- coding:utf-8 -*-

from odoo import fields, models


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    is_post_salary = fields.Boolean(
        'Post salary rule ?',
    )
    is_net_salary = fields.Boolean(
        'Net salary rule ?',
    )
    is_base_salary = fields.Boolean(
        'Base salary rule ?',
    )
    is_irg_base_salary = fields.Boolean(
        'IRG base salary rule ?',
    )
    struct_id = fields.Many2many(
        'hr.payroll.structure',
        'payroll_structure_rule_rel',
        'rule_id',
        'struct_id',
        string='Salary Structures'
    )

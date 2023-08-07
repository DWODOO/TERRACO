# -*- coding:utf-8 -*-

from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    leave_ids = fields.One2many(
        'hr.leave',
        'employee_id',
        string='Leaves',
    )

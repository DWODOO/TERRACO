# -*- coding:utf-8 -*-

from odoo import fields, models


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    smartest_need_verif = fields.Boolean("Need Verification")


# class HrEmployee(models.Model):
#     _inherit = 'hr.employee'
#
#     activity_user_id = fields.Many2one("res.users", store=1)

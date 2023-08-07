# -*- coding:utf-8 -*-

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    department_ids = fields.Many2many('hr.department', 'purchase_request_res_users_request_rel',
                                              column1='user_id', column2='department_id',
                                              string='Requested Departments')
    author_department_ids = fields.Many2many('hr.department', 'purchase_request_res_users_val_rel',
                                             column1='user_autho_id', column2='department_autho_id',
                                             string='Validation Departments')
    # team_id = fields.Many2one("smartest.hr.team", string="Team")


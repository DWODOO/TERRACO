# -*- coding:utf-8 -*-

from odoo import fields, models


class HrTeam(models.Model):
    _name = 'smartest.hr.team'

    name = fields.Char("Nom")
    leader_id = fields.Many2one("res.users", string="Team Leader")
    member_ids = fields.Many2many("res.users", 'hr_team_res_users_val_rel',
                                  column1='team_id', column2='user_id',
                                  string='Members')

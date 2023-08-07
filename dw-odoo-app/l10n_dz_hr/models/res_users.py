# -*- coding:utf-8 -*-
from odoo import api, fields, models, _


class ResUsers(models.Model):
    _inherit = 'res.users'

    work_location = fields.Many2one(
        'res.country.state',
        related='employee_id.work_location'
    )
    place_of_birth = fields.Char(
        related='employee_id.place_of_birth'
    )

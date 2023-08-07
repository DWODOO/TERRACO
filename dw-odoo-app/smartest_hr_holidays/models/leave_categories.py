# -*- coding:utf-8 -*-
from odoo import models, fields, api, _



class LeaveCategories(models.Model):
    _name = 'leave.categories'

    name = fields.Char(
        string="Name",
        required=True,
    )
    code = fields.Char(
        string="Code",
        required=True,
    )
    sequence = fields.Integer(
        string="Sequence",
        required=True,
    )

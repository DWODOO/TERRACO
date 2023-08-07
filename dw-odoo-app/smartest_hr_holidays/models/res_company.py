# -*- coding:utf-8 -*-
from odoo import models, fields


class HrResCompany(models.Model):
    _inherit = 'res.company'

    jours_conge = fields.Integer(
        string="Jours"
    )

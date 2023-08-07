# -*- coding: utf-8 -*-

from odoo import api, fields, models


class rescompany(models.Model):
    _inherit ='res.company'

    activ = fields.Char(
        string="activ"
    )

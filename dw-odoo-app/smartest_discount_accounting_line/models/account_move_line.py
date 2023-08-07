# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_discount_line = fields.Boolean(
        'Is Discount Line'
    )

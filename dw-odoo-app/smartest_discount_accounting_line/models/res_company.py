# -*- coding: utf-8 -*-
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    use_discount_accounting = fields.Boolean(
        'Use Discount Accounting?'
    )
    discount_account_id = fields.Many2one(
        'account.account',
        'Discount Account',
    )

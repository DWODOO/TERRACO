# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    discount_account_id = fields.Many2one(
        'account.account',
        'Discount Account',
        default=lambda self: self.env.user.company_id.discount_account_id
    )

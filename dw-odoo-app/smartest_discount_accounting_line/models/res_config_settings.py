# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    use_discount_accounting = fields.Boolean(
        related='company_id.use_discount_accounting',
        readonly=False
    )
    discount_account_id = fields.Many2one(
        related='company_id.discount_account_id',
        readonly=False
    )

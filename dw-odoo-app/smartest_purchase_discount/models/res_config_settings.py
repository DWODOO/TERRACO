# -*- coding: utf-8 -*-

# Import Odoo libs
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_smartest_discount_per_po_line = fields.Boolean(
        "Discounts",
        implied_group='smartest_purchase_discount.group_smartest_discount_per_po_line'
    )

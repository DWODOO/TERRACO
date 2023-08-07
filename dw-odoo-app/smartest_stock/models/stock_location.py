# -*- coding:utf-8 -*-
from odoo import models, fields


class StockLocation(models.Model):
    _inherit = 'stock.location'

    allow_negative_stock = fields.Boolean(
        string='Allow Negative Stock',
        help="Allow negative stock levels for the stockable products "
        "attached to this location."
    )  # If this field is checked, the negative stock will be authorized on this location

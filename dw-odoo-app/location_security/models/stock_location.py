# -*- coding:utf-8 -*-
from odoo import models, fields


class StockLocation(models.Model):
    _inherit = 'stock.location'

    user_ids = fields.Many2many(
        'res.users',
        'user_location_rel',
        'location_id',
        'user_id',
        'Allowed Users',
    )  # The users allowed to use the location. Be careful ! The users that not belongs to stock_restriction_group
    # security group are also authorized to use this location but they not figure on this field.

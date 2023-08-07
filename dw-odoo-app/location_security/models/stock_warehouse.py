# -*- coding:utf-8 -*-
from odoo import models, fields


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    user_ids = fields.Many2many(
        'res.users',
        'user_warehouse_rel',
        'warehouse_id',
        'user_id',
        'Allowed Users',
    )  # The users allowed to use the warehouse. Be careful ! The users that not belongs to stock_restriction_group
    # security group are also authorized to use this warehouse but they not figure on this field.

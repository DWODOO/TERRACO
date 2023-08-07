# -*- coding: utf-8 -*-
from odoo import models, fields, tools
from odoo.exceptions import UserError, ValidationError
from itertools import chain
import json


class SmartestPricelistLine(models.Model):
    _name = 'pricelist.margin.line'

    pricelist_coefficient_id = fields.Many2one(
        'pricelist.coefficient',
    )
    coefficient = fields.Float(
        'Coefficient'
    )
    product_new_price = fields.Float(
        'Price'
    )
    product_line_id = fields.Many2one(
        'pricelist.margin',
        string='priclist id'
    )
    product_id = fields.Many2one(
        'product.product'
    )
    purchase_price = fields.Float(
        'prix d\'achat',
        digit=(10, 2)
    )
    last_cost = fields.Float(
        'last cost',
        digit=(10, 2)
    )
    use_highest_cost = fields.Boolean()
    highest_cost = fields.Float(
        'Highest cost',
        digit=(10, 2)
    )
    state = fields.Selection([
        ('draft', 'draft'),
        ('confirmed', 'Calculate'),
        ('validation', 'Validation'),
        ('done', 'done'),
    ],
        string="State",
        default="draft",
        invisible=True
    )
    add_articles = fields.Boolean(
        'New Article',
        help="By checking this, we can add a product from the selection below that doesn't exist in the price list"
    )
    use_product_sale_price = fields.Boolean()

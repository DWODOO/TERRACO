from odoo import models, fields, api


class smartest_stock_inventory_line(models.Model):
    _name = 'smartest.inventory.line'

    product_id = fields.Many2one(
        'product.product'
    )
    location = fields.Many2one('stock.location', string='Location')

    emplacement_id = fields.Many2one('stock.location', string='Emplacement')

    first_count = fields.Integer(
        'First Count',
    )
    second_count = fields.Integer(
        'Second Count'
    )

    third_count = fields.Integer(
        'Third Count',
    )

    difference_qty = fields.Integer(
        'Difference',
        readonly="true"
    )
    inventory_id = fields.Many2one('smartest.inventory',string='inventory id')

    deff = fields.Boolean('',default=False)

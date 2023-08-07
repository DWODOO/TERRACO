from odoo import models, fields, api


class InetermIventLine(models.Model):
    _name = 'interm.inv.line'

    product_id = fields.Char()
    location = fields.Char(
        'Location'
    )
    just_id = fields.Integer()
    emplacement_id = fields.Many2one('stock.location', string='Emplacement')





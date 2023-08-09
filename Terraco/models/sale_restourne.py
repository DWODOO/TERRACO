from odoo import models,fields,api,_
from odoo.exceptions import ValidationError

class SaleRestourne(models.Model):

    _name = 'sale.restourne'
    _description = 'Matrice des remise'

    amount_min = fields.Monetary(
        required=True,
        string="Amount min",
        currency_field="currency_id",store=True
    )
    amount_max = fields.Monetary(
        required=True,
        string="Amount max",
        currency_field="currency_id",store=True
    )
    percentage = fields.Float(
        required=True,
        string="Percentage"
    )
    payment_type = fields.Selection([
        ('cash', 'Cash'),
        ('aterm', 'A term'),
    ], string="payment", default="aterm", required=True)

    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id, readonly=True)


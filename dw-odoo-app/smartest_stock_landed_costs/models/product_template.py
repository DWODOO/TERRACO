from odoo import fields, models


class SmartestProductTemplate(models.Model):
    _inherit = 'product.template'

    smartest_product_last_cost = fields.Float(string='Last Cost', company_dependent=True)

    hs_code_id = fields.Many2one(
        'stock.hs.code',
        string='Hs Code'
    )
    hs_code_rate = fields.Float(
        string='Clearance Rate',
        related='hs_code_id.percentage'
    )


from odoo import api, fields, models

class ProductCategory(models.Model):
    _inherit = "product.category"

    hs_code_id = fields.Many2one(
        'stock.hs.code',
        string='Hs Code'
    )
    hs_code_rate = fields.Float(
        string='Clearance Rate',
        related='hs_code_id.percentage'
    )

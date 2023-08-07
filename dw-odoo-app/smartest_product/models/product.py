# -*- coding: utf-8 -*-
from odoo import fields, models


class SmartestProductTemplate(models.Model):
    _inherit = 'product.template'

    brand_id = fields.Many2one(
        'res.brand',
        index=True
    )
    vendor_reference = fields.Char(
        'Vendor Reference',
        index=True
    )

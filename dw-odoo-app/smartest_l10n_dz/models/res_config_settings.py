# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    use_stamp_tax = fields.Boolean(
        related='company_id.use_stamp_tax',
        readonly=False
    )
    stamp_tax_account_id = fields.Many2one(
        related='company_id.stamp_tax_account_id',
        readonly=False
    )
    invoice_amount_min = fields.Monetary(
        related='company_id.invoice_amount_min',
        readonly=False
    )
    stamp_tax_max = fields.Monetary(
        related='company_id.stamp_tax_max',
        readonly=False
    )
    stamp_tax_min = fields.Monetary(
        related='company_id.stamp_tax_min',
        readonly=False
    )
    slice = fields.Monetary(
        related='company_id.slice',
        readonly=False
    )
    slice_amount = fields.Monetary(
        related='company_id.slice_amount',
        readonly=False
    )

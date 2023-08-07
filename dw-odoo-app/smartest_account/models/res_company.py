# -*- coding: utf-8 -*-
from odoo import models, fields


class SmartestResCompany(models.Model):
    _inherit = 'res.company'

    use_stamp_tax = fields.Boolean(
        'Use Stamp Duty Tax?'
    )
    stamp_tax_account_id = fields.Many2one(
        'account.account',
        'Account',
    )
    invoice_amount_min = fields.Monetary(
        'Amount Max.',
        currency_field='currency_id',
        default=20,
    )
    stamp_tax_max = fields.Monetary(
        'Tax Amount Max.',
        currency_field='currency_id',
        default=2500,
    )
    stamp_tax_min = fields.Monetary(
        'Tax Amount Min.',
        currency_field='currency_id',
        default=5,
    )
    slice = fields.Monetary(
        'Slice',
        currency_field='currency_id',
        default=100,
    )
    slice_amount = fields.Monetary(
        'Slice Amount',
        currency_field='currency_id',
        default=1,
    )


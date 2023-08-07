# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    currency_rate_purchase = fields.Float(
        'Purchase Currency Rate',
        readonly=False,
        store=True,
        default=1
    )

    # adding currency_rate_purchase to dependencies
    @api.depends(
        'currency_rate_purchase',
    )
    def _compute_tax_totals(self):
        return super()._compute_tax_totals()

    @api.onchange('currency_id')
    def _onchange_current_currency_id(self):
        self.currency_rate_purchase = self.currency_id.rate


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    # adding currency_rate_purchase to dependencies
    @api.depends('move_id.currency_rate_purchase')
    def _compute_currency_rate(self):
        res = super()._compute_currency_rate()
        for line in self:
            currency_rate = line.move_id.currency_rate_purchase
            if currency_rate and 1 / currency_rate != line.currency_rate:
                line.currency_rate = 1 / currency_rate
        return res

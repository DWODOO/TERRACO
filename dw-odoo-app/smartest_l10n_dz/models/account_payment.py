# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    is_reconciled_with_invoice = fields.Boolean(
        'Invoice reconciled?',
        store=True,
        compute='_compute_is_reconciled_with_invoice'
    )
    amount_open = fields.Monetary(
        "Opened Amount",
        compute='_compute_amount_open',
        store=True
    )

    @api.onchange('partner_type')
    def _onchange_partner_type(self):
        """
        According to the payment partner_type field add domain filter for partner_id field to force selecting only
        customer (resp) or supplier (resp) if the partner_type field value is 'customer' (resp) or 'supplier' (resp)
        :return: Domain Dict
        """
        return {
            'domain': {
                'partner_id': [('is_%s' % self.partner_type, '=', True)]
            }
        }

    def _compute_is_reconciled_with_invoice(self):
        for pay in self:
            pay.is_reconciled_with_invoice = False  # TODO: adapt this method to V14

    @api.depends('reconciled_invoice_ids', 'amount')
    def _compute_amount_open(self):
        for pay in self:
            amount_open = pay.amount
            for invoice in pay.reconciled_invoice_ids:
                amount_open -= invoice.currency_id._convert(
                    invoice.amount_total,
                    pay.currency_id,
                    pay.company_id,
                    pay.date
                )
                if amount_open <= 0:
                    amount_open = 0
                    break
            pay.amount_open = amount_open

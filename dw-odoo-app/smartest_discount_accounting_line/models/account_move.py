# -*- coding: utf-8 -*-
from odoo import models, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _check_balanced(self):
        if not self.ids:
            return
        return super(AccountMove, self)._check_balanced()

    @api.onchange('invoice_line_ids')
    def _onchange_invoice_line_ids(self):
        super(AccountMove, self)._onchange_invoice_line_ids()
        current_company = self.env.user.company_id
        for invoice in self.filtered(lambda inv: inv.is_invoice() and (inv.company_id or current_company).use_discount_accounting):
            discount_lines = invoice.invoice_line_ids.filtered(lambda l: l.discount)
            new_line_ids = []
            for line in discount_lines:
                amount_discount = abs(line.price_subtotal - (line.quantity * line.price_unit))
                company_id = line.company_id or line.move_id.company_id
                product_id = line.product_id
                account_id = (
                        product_id.discount_account_id or
                        product_id.categ_id.discount_account_id or
                        company_id.discount_account_id
                )
                new_line_ids += [
                    (0, 0, {
                        'name': _('Discount'),
                        'account_id': account_id.id,
                        'move_id': invoice.id,
                        'partner_id': invoice.partner_id.id,
                        'company_id': company_id.id,
                        'company_currency_id': line.company_currency_id.id,
                        "credit": line.debit and amount_discount or 0.0,
                        "debit": line.credit and amount_discount or 0.0,
                        'quantity': 1.0,
                        'exclude_from_invoice_tab': True,
                        'is_discount_line': True,
                    }),
                    (0, 0, {
                        'name': line.name,
                        'account_id': line.account_id.id,
                        'move_id': line.move_id.id,
                        'partner_id': line.partner_id.id,
                        'company_id': company_id.id,
                        'company_currency_id': line.company_currency_id.id,
                        "credit": line.credit and amount_discount or 0.0,
                        "debit": line.debit and amount_discount or 0.0,
                        'quantity': 1.0,
                        'exclude_from_invoice_tab': True,
                        'is_discount_line': True,
                    }),
                ]
            already_inserted = invoice.line_ids.filtered(lambda l: l.is_discount_line)
            if already_inserted:
                new_line_ids += [(2, inserted.id) for inserted in already_inserted]
            if new_line_ids:
                invoice.write({
                    'line_ids': new_line_ids
                })
                if invoice != invoice._origin:
                    invoice.invoice_line_ids = invoice.line_ids.filtered(lambda line: not line.exclude_from_invoice_tab)
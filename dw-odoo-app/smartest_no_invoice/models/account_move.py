# -*- coding: utf-8 -*-

from odoo import api, fields, models, Command, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from odoo.tools import float_compare, date_utils, email_split, email_re, html_escape, is_html_empty
from odoo.tools.misc import formatLang, format_date, get_lang

from datetime import date, timedelta
from collections import defaultdict
from contextlib import contextmanager
from itertools import zip_longest
from hashlib import sha256
from json import dumps

import ast
import json
import re
import warnings



class SmartestAccountMove(models.Model):
    _inherit = 'account.move'

    no_invoice = fields.Boolean(
        string="ND",
        default=False
    )

    def _recompute_payment_terms_lines(self):
        #I couldn't inherit this nested fct so i have overwrited it
        #the purpose is to inerit the fct _get_payment_terms_account and take property_account_receivable_id on the fiscal position
        ''' Compute the dynamic payment term lines of the journal entry.'''
        self.ensure_one()
        self = self.with_company(self.company_id)
        in_draft_mode = self != self._origin
        today = fields.Date.context_today(self)
        self = self.with_company(self.journal_id.company_id)

        def _get_payment_terms_computation_date(self):
            ''' Get the date from invoice that will be used to compute the payment terms.
            :param self:    The current account.move record.
            :return:        A datetime.date object.
            '''
            if self.invoice_payment_term_id:
                return self.invoice_date or today
            else:
                return self.invoice_date_due or self.invoice_date or today

        def _get_payment_terms_account(self, payment_terms_lines):
            ''' Get the account from invoice that will be set as receivable / payable account.
            :param self:                    The current account.move record.
            :param payment_terms_lines:     The current payment terms lines.
            :return:                        An account.account record.
            '''
            # here is the changes I made, if no invoice than use account of the fiscal position
            if self.move_type == 'out_invoice' and self.no_invoice and self.fiscal_position_id and self.fiscal_position_id.property_account_receivable_id :
                return self.fiscal_position_id.property_account_receivable_id
            else:
                if payment_terms_lines:
                    # Retrieve account from previous payment terms lines in order to allow the user to set a custom one.
                    return payment_terms_lines[0].account_id
                elif self.partner_id:
                    # Retrieve account from partner.
                    if self.is_sale_document(include_receipts=True):
                        return self.partner_id.property_account_receivable_id
                    else:
                        return self.partner_id.property_account_payable_id
                else:
                    # Search new account.
                    domain = [
                        ('company_id', '=', self.company_id.id),
                        ('internal_type', '=', 'receivable' if self.move_type in ('out_invoice', 'out_refund', 'out_receipt') else 'payable'),
                    ]
                    return self.env['account.account'].search(domain, limit=1)

        def _compute_payment_terms(self, date, total_balance, total_amount_currency):
            ''' Compute the payment terms.
            :param self:                    The current account.move record.
            :param date:                    The date computed by '_get_payment_terms_computation_date'.
            :param total_balance:           The invoice's total in company's currency.
            :param total_amount_currency:   The invoice's total in invoice's currency.
            :return:                        A list <to_pay_company_currency, to_pay_invoice_currency, due_date>.
            '''
            if self.invoice_payment_term_id:
                to_compute = self.invoice_payment_term_id.compute(total_balance, date_ref=date, currency=self.company_id.currency_id)
                if self.currency_id == self.company_id.currency_id:
                    # Single-currency.
                    return [(b[0], b[1], b[1]) for b in to_compute]
                else:
                    # Multi-currencies.
                    to_compute_currency = self.invoice_payment_term_id.compute(total_amount_currency, date_ref=date, currency=self.currency_id)
                    return [(b[0], b[1], ac[1]) for b, ac in zip(to_compute, to_compute_currency)]
            else:
                return [(fields.Date.to_string(date), total_balance, total_amount_currency)]

        def _compute_diff_payment_terms_lines(self, existing_terms_lines, account, to_compute):
            ''' Process the result of the '_compute_payment_terms' method and creates/updates corresponding invoice lines.
            :param self:                    The current account.move record.
            :param existing_terms_lines:    The current payment terms lines.
            :param account:                 The account.account record returned by '_get_payment_terms_account'.
            :param to_compute:              The list returned by '_compute_payment_terms'.
            '''
            # As we try to update existing lines, sort them by due date.
            existing_terms_lines = existing_terms_lines.sorted(lambda line: line.date_maturity or today)
            existing_terms_lines_index = 0

            # Recompute amls: update existing line or create new one for each payment term.
            new_terms_lines = self.env['account.move.line']
            for date_maturity, balance, amount_currency in to_compute:
                currency = self.journal_id.company_id.currency_id
                if currency and currency.is_zero(balance) and len(to_compute) > 1:
                    continue

                if existing_terms_lines_index < len(existing_terms_lines):
                    # Update existing line.
                    candidate = existing_terms_lines[existing_terms_lines_index]
                    existing_terms_lines_index += 1
                    candidate.update({
                        'date_maturity': date_maturity,
                        'amount_currency': -amount_currency,
                        'debit': balance < 0.0 and -balance or 0.0,
                        'credit': balance > 0.0 and balance or 0.0,
                    })
                else:
                    # Create new line.
                    create_method = in_draft_mode and self.env['account.move.line'].new or self.env['account.move.line'].create
                    candidate = create_method({
                        'name': self.payment_reference or '',
                        'debit': balance < 0.0 and -balance or 0.0,
                        'credit': balance > 0.0 and balance or 0.0,
                        'quantity': 1.0,
                        'amount_currency': -amount_currency,
                        'date_maturity': date_maturity,
                        'move_id': self.id,
                        'currency_id': self.currency_id.id,
                        'account_id': account.id,
                        'partner_id': self.commercial_partner_id.id,
                        'exclude_from_invoice_tab': True,
                    })
                new_terms_lines += candidate
                if in_draft_mode:
                    candidate.update(candidate._get_fields_onchange_balance(force_computation=True))
            return new_terms_lines

        existing_terms_lines = self.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
        others_lines = self.line_ids.filtered(lambda line: line.account_id.user_type_id.type not in ('receivable', 'payable'))
        company_currency_id = (self.company_id or self.env.company).currency_id
        total_balance = sum(others_lines.mapped(lambda l: company_currency_id.round(l.balance)))
        total_amount_currency = sum(others_lines.mapped('amount_currency'))

        if not others_lines:
            self.line_ids -= existing_terms_lines
            return

        computation_date = _get_payment_terms_computation_date(self)
        account = _get_payment_terms_account(self, existing_terms_lines)
        to_compute = _compute_payment_terms(self, computation_date, total_balance, total_amount_currency)
        new_terms_lines = _compute_diff_payment_terms_lines(self, existing_terms_lines, account, to_compute)

        # Remove old terms lines that are no longer needed.
        self.line_ids -= existing_terms_lines - new_terms_lines

        if new_terms_lines:
            self.payment_reference = new_terms_lines[-1].name or ''
            self.invoice_date_due = new_terms_lines[-1].date_maturity




    @api.onchange('no_invoice')
    def on_change_no_invoice(self):
        for this in self:
            if this.state == 'draft' and this.no_invoice:
                this.fiscal_position_id = self.env.ref('smartest_no_invoice.smartest_no_invoice_fiscal_position')
                if this.line_ids:
                    raise UserError(
                        _('There is already move lines, You have to check this field before adding line !.'))
                return this.fiscal_position_id.check_fiscal_position_configuration()
            elif this.state == 'draft' and not this.no_invoice:
                this.fiscal_position_id = False




    def action_register_payment(self):
        action = super(SmartestAccountMove, self).action_register_payment()

        no_invoice = any(self.mapped('no_invoice'))

        action['context']['default_no_invoice_payment'] = no_invoice

        return action

    def action_post(self):
        IrSequence = self.env['ir.sequence']
        for invoice in self:
            if invoice.move_type == 'out_invoice' and invoice.name == '/' and invoice.no_invoice:
                invoice.name = IrSequence.next_by_code('account.invoice.not.declared')

        return super(SmartestAccountMove, self).action_post()

    def _get_last_sequence_domain(self, relaxed=False):
        where_string, param = super(SmartestAccountMove, self)._get_last_sequence_domain(relaxed)
        if not self.no_invoice:
            where_string += " and  no_invoice = False"
        return where_string, param


class SmartestAccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    no_invoice_payment = fields.Boolean(
        string="ND",
        default=False
    )

    def _create_payments(self):
        payments = super(SmartestAccountPaymentRegister, self)._create_payments()
        context = self.env.context
        no_invoice_payment = context.get('default_no_invoice_payment')
        if no_invoice_payment:
            payments.write({
                "no_invoice_payment": no_invoice_payment,
                "name": self.env['ir.sequence'].next_by_code('account.payment.not.declared')
            })

        return payments

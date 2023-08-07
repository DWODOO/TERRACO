# -*- coding: utf-8 -*-
from num2words import num2words
from contextlib import contextmanager
from odoo.tools.misc import formatLang
from odoo import _, api, fields, models


class SmartestAccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_stamp_tax_line = fields.Boolean(
        'Stamp Duty',
    )  # This is a technical field that used to now which account.move.line correspond to the Stamp Duty Tax



class AccountMove(models.Model):
    _inherit = 'account.move'

    amount_total_words = fields.Char(
        compute="_compute_amount_to_words"
    )
    use_stamp_tax = fields.Boolean(
        related='company_id.use_stamp_tax',
    )
    amount_stamp_tax = fields.Monetary(
        string='Stamp Duty',
        currency_field='company_currency_id',
        store=True,
        readonly=True,
        tracking=True,
    )  # This field used to store the amount of stamp duty tax if it exist
    amount_total_with_tva = fields.Monetary(
        string='Total With TVA',
        currency_field='company_currency_id',
        store=True,
        readonly=True,
        tracking=True,
        compute='_compute_amount'
    )  # This field used to store the total amount with taxes. Because the amount_stamp_tax is not yet included
    payment_method_id = fields.Many2one(
        comodel_name="account.payment.method",
        readonly=True,
        tracking=True,
        states={'draft': [('readonly', False)]},
    )  # This field is used to get the payment method and derive if the stamp duty tax is applicable or not.
    apply_stamp_duty_tax = fields.Boolean(
        string="Apply Stamp Duty?",
        readonly=True,
        tracking=True,
        states={'draft': [('readonly', False)]}
    )  # This field is used to compute amount_stamp_tax. The Stamp duty taxed is used only when this field is true

    # ----------------------------------------------------------------
    # Onchange methods                                               -
    # ----------------------------------------------------------------
    @api.onchange('payment_method_id', 'use_stamp_tax')
    def _onchange_payment_method_id(self):
        if not self.use_stamp_tax:
            self.apply_stamp_duty_tax = False
        elif self.payment_method_id:
            self.apply_stamp_duty_tax = self.payment_method_id.apply_stamp_duty_tax

    @api.onchange('apply_stamp_duty_tax')
    def _onchange_apply_stamp_duty_tax(self):
        stamp_base_amount = sum(self.mapped('invoice_line_ids.price_total'))
        self.amount_stamp_tax = self._get_stamp_tax_amount(stamp_base_amount)
        self._compute_tax_totals()

    # ----------------------------------------------------------------
    # Compute methods                                               -
    # ----------------------------------------------------------------
    @api.depends('amount_total')
    def _compute_amount_to_words(self):
        for move in self:
            # Initialize variables
            amount_total_words = ''

            if move.move_type == 'out_invoice':
                # Convert to Float
                flo = float(round(move.amount_total,2))

                # Compute entire
                entire_num = int((str(flo).split('.'))[0])

                # Compute decimals
                str_decimal_num = (str(flo).split('.'))[1]
                decimal_num = int((str(flo).split('.'))[1])

                # Build Total text
                amount_total_words = num2words(entire_num, lang='fr')
                amount_total_words += ' Dinars Algériens '

                if decimal_num != 0:
                    if len(str_decimal_num) != 1:
                        if decimal_num > 10:
                            amount_total_words += ' et %s %s' % (num2words(decimal_num, lang='fr'), ' Centimes')
                        else:
                            amount_total_words += ' et zero %s %s' % (num2words(decimal_num, lang='fr'), ' Centimes')
                    else:
                        decimal_num = decimal_num * 10
                        amount_total_words += ' et %s %s' % (num2words(decimal_num, lang='fr'), ' Centimes')

            # Populate field
            move.amount_total_words = amount_total_words

    @api.depends(
        'invoice_line_ids.currency_rate',
        'invoice_line_ids.tax_base_amount',
        'invoice_line_ids.tax_line_id',
        'invoice_line_ids.price_total',
        'invoice_line_ids.price_subtotal',
        'invoice_payment_term_id',
        'partner_id',
        'currency_id',
    )
    def _compute_tax_totals(self):
        super(AccountMove, self)._compute_tax_totals()
        for move in self:
            tax_totals = move.tax_totals
            if tax_totals and 'amount_total' in tax_totals and tax_totals['amount_total']:
                base_amount = tax_totals['amount_total']
                stamp_tax_amount = move._get_stamp_tax_amount(base_amount)
                move.amount_stamp_tax = stamp_tax_amount
                amount_total = base_amount + stamp_tax_amount
                tax_totals.update({
                    'stamp_tax_amount': stamp_tax_amount,
                    'formatted_stamp_tax_amount': formatLang(self.env, stamp_tax_amount, currency_obj=move.currency_id),
                    'formatted_amount_total_with_stamp': formatLang(self.env, amount_total, currency_obj=move.currency_id),
                    'amount_total': amount_total,
                    'formatted_amount_total': formatLang(self.env, amount_total, currency_obj=move.currency_id),
                })
            move.tax_totals = tax_totals

    # ----------------------------------------------------------------
    # Helpers methods                                               -
    # ----------------------------------------------------------------
    def _get_stamp_tax_amount(self, base_amount):
        company_id = self.company_id
        if not self.use_stamp_tax \
                or not self.apply_stamp_duty_tax \
                or self.move_type not in ['out_invoice', 'out_refund', 'in_invoice', 'in_refund'] \
                or 0 in company_id.read(['slice', 'slice_amount']) \
                or not self.is_invoice() \
                or base_amount < company_id.invoice_amount_min:

            return 0.0
        else:
            slice_count = base_amount // company_id.slice
            rest = base_amount % company_id.slice
            if rest:
                slice_count += 1
            amount_stamp_tax = slice_count * company_id.slice_amount
            if amount_stamp_tax > company_id.stamp_tax_max:
                amount_stamp_tax = company_id.stamp_tax_max
            elif amount_stamp_tax < company_id.stamp_tax_min:
                amount_stamp_tax = company_id.stamp_tax_min

            return amount_stamp_tax

    @contextmanager
    def _sync_dynamic_line(self, existing_key_fname, needed_vals_fname, needed_dirty_fname, line_type, container):
        with super(AccountMove, self)._sync_dynamic_line(existing_key_fname, needed_vals_fname, needed_dirty_fname, line_type, container):
            move = container['records']
            if line_type == 'payment_term' and len(move) == 1 and move.state == 'draft':
                move.line_ids.filtered('is_stamp_tax_line').with_context(skip_invoice_sync=True, dynamic_unlink=True, force_delete=True).unlink()

                sign = -1 if move.move_type in ('out_invoice', 'in_refund') else 1
                stamp_tax_amount = move.amount_stamp_tax
                if not stamp_tax_amount:
                    base_amount = move.amount_total
                    if not base_amount:
                        base_amount = sum(move.invoice_line_ids.mapped('price_total'))
                    stamp_tax_amount = move._get_stamp_tax_amount(base_amount)
                if stamp_tax_amount:
                    to_write = {}
                    for line in move.line_ids.filtered(lambda l: l.display_type == 'payment_term'):
                        to_write[line] = {'balance': line.balance + stamp_tax_amount}
                        break

                    self.env['account.move.line'].create({
                        'name': _('Stamp Duty'),
                        'account_id': move.company_id.stamp_tax_account_id.id,
                        'partner_id': move.partner_id.id,
                        'company_id': move.company_id.id,
                        'company_currency_id': move.company_currency_id.id,
                        'quantity': 1.0,
                        'balance': sign * stamp_tax_amount,
                        'display_type': 'tax',
                        'is_stamp_tax_line': True,
                        'move_id': move.id,
                    })
            yield

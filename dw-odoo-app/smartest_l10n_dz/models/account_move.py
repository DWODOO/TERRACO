# -*- coding: utf-8 -*-
from num2words import num2words

from odoo import _, api, fields, models

from odoo.exceptions import UserError


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_stamp_tax_line = fields.Boolean(
        'Stamp Duty',
    )  # This is a technical field that used to now which account.move.line correspond to the Stamp Duty Tax

    _sql_constraints = [(
        'check_credit_debit',
        'CHECK(credit * debit=0)',
        'Wrong credit or debit value in accounting entry !'
    )]
    smartest_external_document = fields.Char('External Document')


class AccountMove(models.Model):
    _inherit = 'account.move'

    amount_total_words = fields.Char(
        compute="_compute_amount_to_words"
    )

    journal_id = fields.Many2one('account.journal',
                                 check_company=True, domain="[]")
    is_closing = fields.Boolean(
        'is Closing'
    )
    use_stamp_tax = fields.Boolean(
        related='company_id.use_stamp_tax',
    )
    amount_stamp_tax = fields.Monetary(
        'Stamp Duty',
        currency_field='company_currency_id',
        store=True,
        readonly=True,
        tracking=True,
        compute='_compute_amount'
    )  # This field used to store the amount of stamp duty tax if it exist
    amount_total_with_tva = fields.Monetary(
        'Total With TVA',
        currency_field='company_currency_id',
        store=True,
        readonly=True,
        tracking=True,
        compute='_compute_amount'
    )  # This field used to store the total amount with taxes. Because the amount_stamp_tax is not yet included
    payment_method_id = fields.Many2one(
        "account.payment.method",
        readonly=True,
        tracking=True,
        states={'draft': [('readonly', False)]},
    )  # This field is used to get the payment method and derive if the stamp duty tax is applicable or not.
    apply_stamp_duty_tax = fields.Boolean(
        "Apply Stamp Duty?",
        readonly=True,
        tracking=True,
        states={'draft': [('readonly', False)]}
    )  # This field is used to compute amount_stamp_tax. The Stamp duty taxed is used only when this field is true
    smartest_move_payment_amount = fields.Float(string='Total', compute='_compute_total_payment', store=True)
    # This field is used to compute display the amount on the analyses of invoices.

    def _compute_total_payment(self):
        for move in self:
            if move.move_type == 'out_invoice':
                move.smartest_move_payment_amount = move.amount_total_signed
            elif move.move_type == 'entry':
                move.smartest_move_payment_amount = - move.amount_total_signed
            else :
                move.smartest_move_payment_amount = 0

    @api.onchange('move_type')
    def _onchange_type(self):
        """
        According to the account.move type, dynamically generate a partner_id field domain:
            1- If the account.invoice record is an out_invoice, out_refund or out_receipt allow selecting only customers
            2- If the account.invoice record is an in_invoice, in_refund or in_receipt allow selecting only suppliers
        :return: Action dict
        """
        # super(AccountMove, self)._onchange_type()
        res = {
            'domain': {
                'partner_id': []
            }
        }
        if self.move_type in ['out_invoice', 'out_refund', 'out_receipt']:
            res['domain']['partner_id'] = [('is_customer', '=', True)]
        if self.move_type in ['in_invoice', 'in_refund', 'in_receipt']:
            res['domain']['partner_id'] = [('is_supplier', '=', True)]
        return res

    @api.onchange('payment_method_id', 'move_type', 'use_stamp_tax')
    def _onchange_payment_method_id(self):
        if not self.use_stamp_tax or self.move_type in ('in_invoice', 'in_refund', 'entry'):
            self.apply_stamp_duty_tax = False
        elif self.payment_method_id:
            self.apply_stamp_duty_tax = self.payment_method_id.apply_stamp_duty_tax
        self._compute_amount()

    @api.onchange('apply_stamp_duty_tax')
    def _onchange_apply_stamp_duty_tax(self):
        self._compute_amount()
    #
    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'line_ids.full_reconcile_id')
    def _compute_amount(self):
        """
        Overriding this method to proceed amount_stamp_tax computation after the default computations
        """
        res = super(AccountMove, self)._compute_amount()
        self._compute_stamp_tax_value()
        return res

    def _compute_stamp_tax_value(self):
        """
        This method is used by the overrated method _compute_amount. The goal of this method is to compute the stamp
        duty tax and add the correspondent account move line.
        """
        for move in self:
            company_id = move.company_id
            initial_amount = move.amount_stamp_tax
            amount_total_with_tva = move.amount_untaxed + move.amount_tax
            if not move.use_stamp_tax \
                    or not move.apply_stamp_duty_tax \
                    or move.move_type not in ['out_invoice', 'out_refund', 'in_invoice', 'in_refund'] \
                    or 0 in company_id.read(['slice', 'slice_amount']) \
                    or not move.is_invoice() \
                    or move.amount_total < company_id.invoice_amount_min:

                # Update amounts
                move.amount_total_with_tva = amount_total_with_tva
                move.amount_stamp_tax = 0.0
            else:
                slice_count = amount_total_with_tva // company_id.slice
                rest = amount_total_with_tva % company_id.slice
                if rest:
                    slice_count += 1
                amount_stamp_tax = slice_count * company_id.slice_amount
                if amount_stamp_tax > company_id.stamp_tax_max:
                    amount_stamp_tax = company_id.stamp_tax_max
                elif amount_stamp_tax < company_id.stamp_tax_min:
                    amount_stamp_tax = company_id.stamp_tax_min

                # Update Amounts
                move.amount_total_with_tva = amount_total_with_tva
                move.amount_stamp_tax = amount_stamp_tax
                move.amount_total = move.amount_total + amount_stamp_tax

        # self._recompute_dynamic_lines()

    def _check_balanced(self, container):
        ''' Assert the move is fully balanced debit = credit.
        An error is raised if it's not the case.
        '''
        to_check = self
        if self.env.context.get('allow_unbalanced_with_stamp_tax'):
            to_check -= to_check.filtered(lambda m: m.apply_stamp_duty_tax)
            if not to_check:
                return
        return super(AccountMove, to_check)._check_balanced( container)

    def _reverse_moves(self, default_values_list=None, cancel=False):
        ''' Reverse a recordset of account.move.
        If cancel parameter is true, the reconcilable or liquidity lines
        of each original move will be reconciled with its reverse's.

        :param default_values_list: A list of default values to consider per move.
                                    ('type' & 'reversed_entry_id' are computed in the method).
        :return:                    An account.move recordset, reverse of the current self.
        '''
        if not default_values_list:
            default_values_list = [{} for move in self]

        if cancel:
            lines = self.mapped('line_ids')
            # Avoid maximum recursion depth.
            if lines:
                lines.remove_move_reconcile()

        reverse_type_map = {
            'entry': 'entry',
            'out_invoice': 'out_refund',
            'out_refund': 'entry',
            'in_invoice': 'in_refund',
            'in_refund': 'entry',
            'out_receipt': 'entry',
            'in_receipt': 'entry',
        }

        move_vals_list = []
        for move, default_values in zip(self, default_values_list):
            default_values.update({
                'move_type': reverse_type_map[move.move_type],
                'reversed_entry_id': move.id,
            })
            move_vals_list.append(move._reverse_move_vals(default_values, cancel=cancel))
        reverse_moves = self.env['account.move'].create(move_vals_list)
        for move, reverse_move in zip(self, reverse_moves.with_context(check_move_validity=False)):
            # Update amount_currency if the date has changed.
            if move.date != reverse_move.date:
                for line in reverse_move.line_ids:
                    if line.currency_id:
                        line._onchange_currency()
            # reverse_move._recompute_dynamic_lines(recompute_all_taxes=False)
        container = {'records': reverse_moves}

        reverse_moves._check_balanced( container)

        # Reconcile moves together to cancel the previous one.
        if cancel:
            reverse_moves.with_context(move_reverse_cancel=cancel).post()
            for move, reverse_move in zip(self, reverse_moves):
                accounts = move.mapped('line_ids.account_id') \
                    .filtered(lambda account: account.reconcile or account.internal_type == 'liquidity')
                for account in accounts:
                    (move.line_ids + reverse_move.line_ids) \
                        .filtered(lambda line: line.account_id == account and line.balance) \
                        .reconcile()

        return reverse_moves

    # def _recompute_dynamic_lines(self, recompute_all_taxes=False, recompute_tax_base_amount=False):
    #     # Call super
    #     super(AccountMove, self)._recompute_dynamic_lines(recompute_all_taxes, recompute_tax_base_amount)
    #
    #     # Stamp accounting
    #     for invoice in self:
    #         if invoice.move_type in ['out_invoice', 'out_refund', 'in_invoice', 'in_refund'] and invoice.apply_stamp_duty_tax:
    #             # Get receivable/payable line
    #             partner_line = invoice.line_ids.filtered(
    #                 lambda line: line.account_id.user_type_id.type in ('receivable', 'payable')
    #             )
    #             if invoice.move_type in ('out_invoice', 'in_refund'):
    #                 partner_line = partner_line.filtered(
    #                     lambda line: line.debit and not line.credit
    #                 )
    #             else:
    #                 partner_line = partner_line.filtered(
    #                     lambda line: line.credit and not line.debit
    #                 )
    #
    #             # Get Stamp line
    #             stamp_tax_line = invoice.line_ids.filtered(
    #                 lambda line: line.is_stamp_tax_line
    #             )
    #
    #             # Get other lines
    #             other_lines = invoice.line_ids - partner_line - stamp_tax_line
    #
    #             if invoice.amount_stamp_tax:
    #                 # If no stamp line is already exists then create a new one
    #                 if not stamp_tax_line:
    #                     stamp_tax_line = self.env['account.move.line'].new({
    #                         'name': _('Stamp Duty'),
    #                         'account_id': invoice.company_id.stamp_tax_account_id.id,
    #                         'partner_id': invoice.partner_id.id,
    #                         'company_id': invoice.company_id.id,
    #                         'company_currency_id': invoice.company_currency_id.id,
    #                         'quantity': 1.0,
    #                         'debit': invoice.move_type in ('in_invoice', 'in_refund') and invoice.amount_stamp_tax or 0.0,
    #                         'credit': invoice.move_type in ('out_invoice', 'out_refund') and invoice.amount_stamp_tax or 0.0,
    #                         'exclude_from_invoice_tab': True,
    #                         'is_stamp_tax_line': True,
    #                     })
    #                 else:
    #                     if stamp_tax_line.debit:
    #                         stamp_tax_line.debit = invoice.amount_stamp_tax
    #
    #                     if stamp_tax_line.credit:
    #                         stamp_tax_line.credit = invoice.amount_stamp_tax
    #
    #                 if partner_line.debit:
    #                     partner_line.debit = invoice.amount_total_with_tva + invoice.amount_stamp_tax
    #
    #                 if partner_line.credit:
    #                     partner_line.credit = invoice.amount_total_with_tva + invoice.amount_stamp_tax
    #             else:
    #                 if partner_line.debit:
    #                     partner_line.debit = invoice.amount_total
    #
    #                 if partner_line.credit:
    #                     partner_line.credit = invoice.amount_total
    #
    #                 stamp_tax_line.debit = stamp_tax_line.credit = 0.0
    #
    #             invoice.line_ids = other_lines + partner_line + stamp_tax_line
    #
    #             # If no stamp tax then remove the related line
    #             if not invoice.amount_stamp_tax:
    #                 invoice.line_ids = invoice.line_ids.filtered(lambda line: not line.is_stamp_tax_line)

    def _reverse_move_vals(self, default_values, cancel=True):
        """
        Override this method to implement negative debit/credit account entry reverse
        """
        reversal_type = self._context.get('reversal_type')
        move_vals = super(AccountMove, self)._reverse_move_vals(default_values, cancel)
        if reversal_type == 'negative_debit_credit':
            lines = move_vals.get('line_ids', [])
            for line in lines:
                line_vals = line[2]
                credit = line_vals.get('credit', 0)
                debit = line_vals.get('debit', 0)
                if credit > 0:
                    line_vals['credit'], line_vals['debit'] = 0, -credit
                elif debit > 0:
                    line_vals['debit'], line_vals['credit'] = 0, -debit
        return move_vals

    # def write(self, vals):
    #     context = dict(self.env.context, allow_unbalanced_with_stamp_tax=True)
    #     res = super(AccountMove, self.with_context(context)).write(vals)
    #     return res


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

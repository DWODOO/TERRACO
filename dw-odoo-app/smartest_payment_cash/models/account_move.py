# -*- coding: utf-8 -*-
from odoo import models, fields, _, api
from odoo.exceptions import UserError,AccessError
from datetime import date, timedelta
from odoo.tools import float_is_zero, float_compare, safe_eval, date_utils, email_split, email_escape_char, email_re
from odoo.tools.misc import formatLang, format_date, get_lang


class AccountMove(models.Model):
    _inherit = 'account.move'

    ticket_ids = fields.Many2many(
        'cash.ticket',
        string="Ticket"
    )  # With a single Ticket we can pay more than one invoice & a single invoice can be paid with more than one ticket
    sale_order_ids = fields.Many2many(
        'sale.order',
        string="Sales"
    )  # The sale.order model has a Many2many relationship with account.move to represent its related invoices

    # Inherit this field in order to add cash_group_user
    invoice_outstanding_credits_debits_widget = fields.Text(
        groups="account.group_account_invoice,smartest_payment_cash.group_cash_user",
        compute='_compute_payments_widget_to_reconcile_info'
    )
    cash_id = fields.Many2one(
        'cash.statement'
    )

    def _prepare_ticket_values(self):
        """
        Prepare the ticket dicts vals to use it in _create_tickets method
        :return: List of Dicts
        """
        vals_list = []
        current_company = self.env.user.company_id
        for partner in self.mapped('partner_id'):
            amount = 0
            partner_invoice = self.filtered(lambda inv: inv.partner_id == partner)
            date = min(self.mapped('invoice_date')) or fields.date.today()
            for invoice in partner_invoice:
                amount += invoice.currency_id._convert(
                    invoice.amount_residual,
                    current_company.currency_id,
                    current_company,
                    date
                )
            vals_list.append({
                'date': date,
                'invoice_ids': [(4, invoice.id) for invoice in partner_invoice],
                'partner_id': partner.id,
                'amount': amount,
                'currency_id': current_company.currency_id.id,
            })
        return vals_list

    def _create_tickets(self):
        """
        The goal of this method is to create ticket and associate it to the Invoice
        :return: Record of cash.ticket -> The created tickets
        """
        if self.filtered(lambda move: move.type in ['entry', 'in_receipt', 'out_receipt']):
            raise UserError(
                _("You can not create ticket for no invoice account move")
            )
        ticket_ids = self.env['cash.ticket'].create(self._prepare_ticket_values())
        return ticket_ids

    def post(self):
        # `user_has_group` won't be bypassed by `sudo()` since it doesn't change the user anymore.
        if not self.env.su and not self.env.user.has_group('account.group_account_invoice') and not self.env.user.has_group('smartest_payment_cash.group_cash_user')and not self.env.user.has_group('car_workshop_management.group_workshop_advisor')  :
            raise AccessError(_("You don't have the access rights to post an invoice."))
        for move in self:
            if not move.line_ids.filtered(lambda line: not line.display_type):
                raise UserError(_('You need to add a line before posting.'))
            if move.auto_post and move.date > fields.Date.today():
                date_msg = move.date.strftime(get_lang(self.env).date_format)
                raise UserError(_("This move is configured to be auto-posted on %s" % date_msg))

            if not move.partner_id:
                if move.is_sale_document():
                    raise UserError(
                        _("The field 'Customer' is required, please complete it to validate the Customer Invoice."))
                elif move.is_purchase_document():
                    raise UserError(
                        _("The field 'Vendor' is required, please complete it to validate the Vendor Bill."))

            if move.is_invoice(include_receipts=True) and float_compare(move.amount_total, 0.0,
                                                                        precision_rounding=move.currency_id.rounding) < 0:
                raise UserError(_(
                    "You cannot validate an invoice with a negative total amount. You should create a credit note instead. Use the action menu to transform it into a credit note or refund."))

            # Handle case when the invoice_date is not set. In that case, the invoice_date is set at today and then,
            # lines are recomputed accordingly.
            # /!\ 'check_move_validity' must be there since the dynamic lines will be recomputed outside the 'onchange'
            # environment.
            if not move.invoice_date and move.is_invoice(include_receipts=True):
                move.invoice_date = fields.Date.context_today(self)
                move.with_context(check_move_validity=False)._onchange_invoice_date()

            # When the accounting date is prior to the tax lock date, move it automatically to the next available date.
            # /!\ 'check_move_validity' must be there since the dynamic lines will be recomputed outside the 'onchange'
            # environment.
            if (move.company_id.tax_lock_date and move.date <= move.company_id.tax_lock_date) and (
                    move.line_ids.tax_ids or move.line_ids.tag_ids):
                move.date = move.company_id.tax_lock_date + timedelta(days=1)
                move.with_context(check_move_validity=False)._onchange_currency()

        # Create the analytic lines in batch is faster as it leads to less cache invalidation.
        self.mapped('line_ids').create_analytic_lines()
        for move in self:
            if move.auto_post and move.date > fields.Date.today():
                raise UserError(_("This move is configured to be auto-posted on {}".format(
                    move.date.strftime(get_lang(self.env).date_format))))

            move.message_subscribe([p.id for p in [move.partner_id] if p not in move.sudo().message_partner_ids])

            to_write = {'state': 'posted'}

            if move.name == '/':
                # Get the journal's sequence.
                sequence = move._get_sequence()
                if not sequence:
                    raise UserError(_('Please define a sequence on your journal.'))

                # Consume a new number.
                to_write['name'] = sequence.with_context(ir_sequence_date=move.date).next_by_id()

            move.write(to_write)

            # Compute 'ref' for 'out_invoice'.
            if move.type == 'out_invoice' and not move.invoice_payment_ref:
                to_write = {
                    'invoice_payment_ref': move._get_invoice_computed_reference(),
                    'line_ids': []
                }
                for line in move.line_ids.filtered(
                        lambda line: line.account_id.user_type_id.type in ('receivable', 'payable')):
                    to_write['line_ids'].append((1, line.id, {'name': to_write['invoice_payment_ref']}))
                move.write(to_write)

            if move == move.company_id.account_opening_move_id and not move.company_id.account_bank_reconciliation_start:
                # For opening moves, we set the reconciliation date threshold
                # to the move's date if it wasn't already set (we don't want
                # to have to reconcile all the older payments -made before
                # installing Accounting- with bank statements)
                move.company_id.account_bank_reconciliation_start = move.date

        for move in self:
            if not move.partner_id: continue
            if move.type.startswith('out_'):
                move.partner_id._increase_rank('customer_rank')
            elif move.type.startswith('in_'):
                move.partner_id._increase_rank('supplier_rank')
            else:
                continue

        # Trigger action for paid invoices in amount is zero
        self.filtered(
            lambda m: m.is_invoice(include_receipts=True) and m.currency_id.is_zero(m.amount_total)
        ).action_invoice_paid()

        # Force balance check since nothing prevents another module to create an incorrect entry.
        # This is performed at the very end to avoid flushing fields before the whole processing.
        self._check_balanced()
        return True

    @api.onchange('move_type')
    def _onchange_type(self):
        """
        inherit fct declared in smartest l10n_dz and add is_employee
        """
        # super(AccountMove, self)._onchange_type()
        res = {
            'domain': {
                'partner_id': []
            }
        }
        if self.move_type in ['out_invoice', 'out_refund', 'out_receipt']:
            res['domain']['partner_id'] = ['|',('is_customer', '=', True),('is_employee', '=', True)]
        if self.move_type in ['in_invoice', 'in_refund', 'in_receipt']:
            res['domain']['partner_id'] = ['|',('is_supplier', '=', True),('is_employee', '=', True)]
        return res

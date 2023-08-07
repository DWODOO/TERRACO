# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    ticket_line_id = fields.Many2one(
        "cash.ticket.line",
        "Cash Ticket Line",
        readonly=True,
        store=True,
        tracking=True,
        ondelete='cascade'
    )  # Each cash.ticket.line record will be converted to an account.payment after closing it's parent cash.ticket
    # We add this field to make a relation between the account.payment record and its source cash.ticket.line record
    cash_ticket_id = fields.Many2one(
        related="ticket_line_id.cash_ticket_id",
        string="Cash Ticket",
        store=True
    )  # This field is to facilitate referencing account.payment record by its source cash.ticket
    cash_statement_id = fields.Many2one(
        "cash.statement",
        "Cash Statement",
        readonly=False,
        store=True,
        ondelete='cascade'
    )
    smartest_partner_type = fields.Char('Type de Partenaire', compute="compute_smartest_payment_type", store=False)

    @api.onchange('partner_type')
    def _onchange_partner_type(self):
        """this fct over wright the same fonction in smartest_l10n_dz to remove the domain"""
        return {
            'domain': {
                'partner_id': [(1,"=",1)]
            }
        }\

    @api.onchange('date','partner_id','journal_id')
    def onchange_ongoing_cash_statement(self):
        for payment in self:
            get_ongoing_cash_statement = self.env['cash.statement'].search(
                [('date', '=', payment.date), ('journal_id', '=', payment.journal_id.id),
                 ('state', '=', 'ongoing')])
            if payment.state == 'draft' and payment.journal_id.type == 'cash':
                payment.cash_statement_id = get_ongoing_cash_statement[0].id if get_ongoing_cash_statement else False

    def compute_smartest_payment_type(self):
        for payment in self:
            if payment.is_internal_transfer:
                payment.smartest_partner_type = 'Interne'
            elif payment.partner_id.is_customer and not payment.is_internal_transfer :
                payment.smartest_partner_type = 'Client'
            elif payment.partner_id.is_supplier and not payment.is_internal_transfer :
                payment.smartest_partner_type = 'Fournisseur'
            elif payment.partner_id and not payment.partner_id.is_customer and not payment.partner_id.is_supplier and not payment.is_internal_transfer :
                payment.smartest_partner_type = 'Employee'
            else:
                payment.smartest_partner_type = False

    @api.model_create_multi
    def create(self, vals_list):
        """inherit create function to add the payment to the cash statement if the cash_statement_state == ongoing with the correct date"""
        for vals in vals_list:
            if not vals.get('posted_before') :
                get_ongoing_cash_statement = self.env['cash.statement'].search(
                    [('date', '=', vals.get('date')), ('journal_id', '=', vals.get('journal_id')), ('state', '=', 'ongoing')])
                vals['cash_statement_id'] = get_ongoing_cash_statement[0].id if get_ongoing_cash_statement else False
            return super(AccountPayment, self).create(vals_list)

    def open_linked_invoices(self):
        """
        This method is used to opens a tree view with invoice(s) to link the payment with
        :return: Action Dict
        """
        for payment in self:
            if payment.payment_type == 'outbound':
                partner_invoices = self.env['account.move'].search(
                    [('partner_id', '=', payment.partner_id.id), ('move_type', '=', 'in_invoice'),
                     ('state', '=', 'posted'),('payment_state', 'not in', ['paid','reversed'])])
            else:
                partner_invoices = self.env['account.move'].search(
                    [('partner_id', '=', payment.partner_id.id), ('move_type', '=', 'out_invoice'),
                     ('state', '=', 'posted'),('payment_state', 'not in', ['paid','reversed'])])
            tree_view = self.env.ref('account.view_out_invoice_tree')
            form_view = self.env.ref('account.view_move_form')
            action = {'name': _('Invoices(s)'), 'type': 'ir.actions.act_window', 'res_model': 'account.move',
                      'context': {'create': False, 'edit': False, },
                      'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
                      'domain': [('id', 'in', partner_invoices.ids)]}
            return action

    def open_this_payment_form(self):
        """open form view from cash statement"""
        for payment in self:
            form_view = self.env.ref('account.view_account_payment_form')
            action = {'name': _('Payment'), 'type': 'ir.actions.act_window', 'res_model': 'account.payment',
                      'context': {'create': False, 'edit': True, },
                      'views': [(form_view.id, 'form')],
                      'res_id': payment.id }
            return action
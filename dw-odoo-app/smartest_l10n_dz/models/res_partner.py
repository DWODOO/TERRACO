# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class Partner(models.Model):
    _inherit = 'res.partner'

    partner_account_group_id = fields.Many2one(
        'partner.account.group',
        'Account Group',
    )  # This field represent partner's account group.
    affected_partner = fields.Selection(
        related='partner_account_group_id.affected_partner'
    )
    customer_clearance = fields.Float(
        compute='_compute_customer_clearance'
    )  # This is a computed field used by a smart button on the partner form view. This is represent the amount
    # of clearance of a customer partner regrading his payment & open invoices.
    supplier_clearance = fields.Float(
        compute='_compute_supplier_clearance'
    )  # This is a computed field used by a smart button on the partner form view. This is represent the amount
    # of clearance of a supplier partner regrading his payment & open invoices.
    _sql_constraints = [
        ('name_uniq', 'unique (name,ref)', 'Contacts name, referance must be unique'),
    ]

    @api.onchange('is_customer', 'is_supplier')
    def _onchange_partner_type(self):
        if self.is_customer:
            self.partner_account_group_id = self.env.ref('smartest_l10n_dz.partner_account_group_customer').id
        elif self.is_supplier:
            self.partner_account_group_id = self.env.ref('smartest_l10n_dz.partner_account_group_supplier').id
        else:
            self.partner_account_group_id = False

    @api.onchange('is_customer', 'is_supplier')
    def _onchange_is_customer(self):
        res = {
            'domain': {
                'partner_account_group_id': []
            }
        }
        self.partner_account_group_id = self.property_account_receivable_id = self.property_account_payable_id = False
        if self.is_customer:
            res['domain']['partner_account_group_id'].append(('affected_partner', '!=', 'supplier'))
        if self.is_supplier:
            res['domain']['partner_account_group_id'].append(('affected_partner', '!=', 'customer'))
        return res

    @api.onchange('partner_account_group_id')
    def _onchange_partner_account_group_id(self):
        if self.is_supplier and self.is_customer:
            self.property_account_receivable_id = self.partner_account_group_id.customer_account_id
            self.property_account_payable_id = self.partner_account_group_id.supplier_account_id
        else:
            if self.is_customer:
                self.property_account_receivable_id = self.partner_account_group_id.customer_account_id
            elif self.is_supplier:
                self.property_account_payable_id = self.partner_account_group_id.supplier_account_id

    def _compute_customer_clearance(self):
        """
        This method used by customer_clearance to compute it's value.
        """
        invoice_obj = self.env['account.move']
        payment_obj = self.env['account.payment']
        company = self.env.user.company_id
        currency = company.currency_id
        for partner in self:
            debit = 0
            credit = 0
            # invoice_ids = invoice_obj.search([
            #     ('partner_id', '=', partner.id),
            #     ('state', '=', 'posted'),
            #     ('type', '=', 'out_invoice'),
            #     ('company_id', '=', company.id),
            # ])
            # payment_ids = payment_obj.search([
            #     ('partner_id', '=', partner.id),
            #     ('state', '=', 'posted'),
            #     ('journal_id.company_id', '=', company.id),
            # ])
            # for invoice in invoice_ids:
            #     credit += invoice.currency_id._convert(
            #         invoice.amount_residual,
            #         currency,
            #         company,
            #         invoice.invoice_date or fields.Date.today()
            #     )
            #
            # for payment in payment_ids:
            #     if not payment.has_invoices:
            #         debit += payment.currency_id._convert(
            #             payment.amount,
            #             currency,
            #             company,
            #             payment.payment_date or fields.Date.today())
            partner.customer_clearance = debit - credit

    def _compute_supplier_clearance(self):
        """
        This method used by customer_clearance to compute it's value.
        """
        invoice_obj = self.env['account.move']
        payment_obj = self.env['account.payment']
        company = self.env.user.company_id
        currency = company.currency_id
        for partner in self:
            debit = 0
            credit = 0
            # invoice_ids = invoice_obj.search([
            #     ('partner_id', '=', partner.id),
            #     ('state', '=', 'posted'),
            #     ('type', '=', 'in_invoice'),
            #     ('company_id', '=', company.id),
            # ])
            # payment_ids = payment_obj.search([
            #     ('partner_id', '=', partner.id),
            #     ('state', '=', 'posted'),
            #     ('journal_id.company_id', '=', company.id),
            # ])
            # for invoice in invoice_ids:
            #     credit += invoice.currency_id._convert(
            #         invoice.amount_residual,
            #         currency,
            #         company,
            #         invoice.invoice_date or fields.Date.today()
            #     )
            #
            # for payment in payment_ids:
            #     if not payment.has_invoices:
            #         debit += payment.currency_id._convert(
            #             payment.amount,
            #             currency,
            #             company,
            #             payment.payment_date or fields.Date.today())
            partner.supplier_clearance = debit - credit

    def action_view_payment(self):
        """
        This method is an action called by the Clearance Smart Button on the res.partner form View.
        This method show a form view or a tree view according to the number of the record related payments.
        :return: Action Dict
        """
        payment_ids = self.env['account.payment'].search([
            ('partner_id', 'in', self.ids),
            ('state', '=', 'posted'),
            ('journal_id.company_id', '=', self.env.user.company_id.id),
        ])
        if not payment_ids:
            raise UserError(
                _('There is no payment to view.')
            )
        tree_view = self.env.ref('account.view_account_payment_tree')
        form_view = self.env.ref('account.view_account_payment_form')
        action = {
            'name': _('Payment(s)'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
        }
        if len(payment_ids) == 1:
            action['views'] = [(form_view.id, 'form')]
            action['res_id'] = payment_ids.id
            action['view_mode'] = 'form'
        else:
            action['views'] = [(tree_view.id, 'tree'), (form_view.id, 'form')]
            action['domain'] = [('id', 'in', payment_ids.ids)]
        return action

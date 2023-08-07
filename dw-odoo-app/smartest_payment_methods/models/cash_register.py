import datetime
import pdb

from odoo import models, api, fields, _
from odoo.exceptions import UserError


class CashRegisterLines(models.Model):
    _name = 'cash.register.line'
    _description = "Cash Register Lines"

    cash_register_id = fields.Many2one(
        'cash.statement'
    )
    product_id = fields.Many2one(
        'product.product',
        domain="[('type', '=', 'service')]"
    )
    currency_id = fields.Many2one(
        "res.currency",
        string='Currency',
        default=lambda self: self.env.user.company_id.currency_id,
        tracking=True,
    )
    amount = fields.Monetary(
        'Amount',
        required=True,
        currency_field="currency_id",
        tracking=True,
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('posted', 'Posted')
    ],
        default='draft'
    )
    move_id = fields.Many2one(
        'account.move'
    )
    partner_id = fields.Many2one(
        'res.partner',
        related='cash_register_id.partner_id'
    )
    journal_id = fields.Many2one(
        'account.journal',
        related='cash_register_id.journal_id'
    )
    is_allowed_to_post = fields.Boolean(
        compute='_compute_is_allowed_to_post'
    )

    def _compute_is_allowed_to_post(self):
        group_id = self.env.ref('account.group_account_manager')
        self.is_allowed_to_post = group_id in self.env.user.groups_id

    def prepare_account_move_lines_data(self, move_id):
        # pdb.set_trace()
        lines = [
            {
                'account_id': self.journal_id.default_account_id.id,
                'partner_id': self.partner_id.id,
                'name': self.product_id.name,
                'currency_id': self.currency_id.id,
                'debit': 0,
                'credit': self.amount,
                'move_id': move_id.id
            },
            {
                'account_id': self.product_id.property_account_expense_id.id,
                'partner_id': self.partner_id.id,
                'name': self.product_id.name,
                'currency_id': self.currency_id.id,
                'debit': self.amount,
                'credit': 0,
                'move_id': move_id.id
            }
        ]
        return lines

    def prepare_account_moves_data(self):
        return {
            'date': self.cash_register_id.date,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id.id,
            'ref': self.cash_register_id.name,
            'move_type': 'entry',
            'extract_state': 'no_extract_requested',
            'state': 'draft',
            'amount_untaxed': self.amount,
            'amount_total': self.amount,
            'cash_id': self.cash_register_id
        }

    def action_create_accounting_document(self):
        move_data = self.prepare_account_moves_data()
        move_id = self.env['account.move'].create(move_data)
        move_line_ids = self.prepare_account_move_lines_data(move_id)
        self.env['account.move.line'].create(move_line_ids)
        return self.write({
            'state': 'done',
            'move_id': move_id.id
        })

    def action_post_accounting_document(self):
        self.move_id.action_post()
        return self.write({
            'state': 'posted'
        })

    def unlink(self):
        if self.state == 'done':
            self.move_id.unlink()
            return super().unlink()
        elif self.state == 'posted':
            raise UserError(_('You cannot delete a posted record'))
        return super().unlink()


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    cash_register = fields.Boolean()

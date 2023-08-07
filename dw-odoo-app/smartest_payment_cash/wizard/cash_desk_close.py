# -*- coding: utf-8 -*-
from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class CashDeskClose(models.TransientModel):
    _name = 'cash.desk.close'
    _description = "Cash Desk Close"

    date_from = fields.Date(
        "Date Start",
        default=fields.date.today()
    )
    date_to = fields.Date(
        "Date To",
        default=fields.date.today()
    )
    cash_desk_id = fields.Many2one(
        'cash.desk',
        'Cash Desk',
        required=True,
        default=lambda self: self.env.user.cash_desk_ids.ids[0] if self.env.user.cash_desk_ids else False
    )
    journal_id = fields.Many2one(
        'account.journal',
        'Journal',
        required=True,
        default=lambda self: self.env.user.company_id.cash_close_journal_id.id
    )
    close_account_id = fields.Many2one(
        'account.account',
        'Closing Account',
        required=True,
    )

    @api.onchange('cash_desk_id')
    def _onchange_cash_desk_id(self):
        default_account_id = self.env.user.company_id.cash_close_account_id
        self.close_account_id = self.cash_desk_id.close_account_id or default_account_id

    def action_close(self):
        self.ensure_one()
        today = fields.date.today()
        date_from = self.date_from or today
        date_to = self.date_to or today
        domain = [
            ('date', '>=', date_from),
            ('date', '<=', date_to),
            ('state', '=', 'validated'),
            ('is_closed', '=', False)
        ]
        ticket_ids = self.env['cash.ticket'].search(domain)
        payment_ids = ticket_ids.mapped('payment_ids')
        move_line_ids = payment_ids.mapped('move_line_ids')

        if not move_line_ids:
            raise ValidationError(
                _("No Account Entry found to close!")
            )

        default_debit_account_id = self.cash_desk_id.journal_id.default_debit_account_id
        amount = 0
        for line in move_line_ids:
            if line.account_id == default_debit_account_id:
                amount += line.debit

        if not amount:
            raise ValidationError(
                _("The total Amount is null!")
            )

        reference = "%s: %s - %s" % (_("Cash Desk Closing"), self.cash_desk_id.name, str(today))
        move_vals = {
            'date': today,
            'ref': reference,
            'journal_id': self.journal_id.id,
            'company_id': self.env.user.company_id.id,
            'line_ids': [
                (0, 0, {
                    'account_id': default_debit_account_id.id,
                    'name': reference,
                    'credit': amount,
                    'debit': 0,
                }),
                (0, 0, {
                    'account_id': self.close_account_id.id,
                    'name': reference,
                    'credit': 0,
                    'debit': amount,
                }),
            ]
        }
        move_id = self.env['account.move'].create(move_vals)
        move_id.action_post()
        ticket_ids.write({
            'is_closed': True
        })
        return {'type': 'ir.actions.act_window_close'}

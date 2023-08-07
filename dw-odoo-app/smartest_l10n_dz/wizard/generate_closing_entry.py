# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
from datetime import  datetime
from odoo.exceptions import UserError, ValidationError


class AccountClosingEntry(models.TransientModel):
    _name = 'account.close.entry'
    _description = 'Account Period Close'

    close_year = fields.Date(string="Close Date" , default = fields.Date.today().replace(month=12, day=31))
    journal_id = fields.Many2one(
        'account.journal', string='Journal',
        domain="[('type', '=', 'general')]",
        default= lambda self : self.env['account.journal'].search([('type', '=', 'general')], limit=1).id)
    account_id = fields.Many2one('account.account', 'Account', required=True,
                                 default=lambda self: self.env.user.company_id.get_unaffected_earnings_account(),
                                 domain=lambda self: [('user_type_id', '=', self.env.ref("account.data_unaffected_earnings").id)])
    def execute(self):
        # Income
        # eval="[(4,ref('account.data_account_type_other_income')), (4,ref('account.data_account_type_revenue'))]"/>
        # Expense
        # eval="[(4,ref('account.data_account_type_expenses')), (4,ref('account.data_account_type_direct_costs')), (4,ref('account.data_account_type_depreciation'))]"/>
        move = self.env['account.move'].search([('is_closing', '=', True),
                                                ('date','>=',self.close_year.replace(month=1, day=1)),
                                                ('date','<=',self.close_year.replace(month=12, day=31))])
        if move:
            if move.state == 'draft':
                move.name = '/'
                move.unlink()
                move = False
            elif move.state == 'posted':
                raise ValidationError("La pièce comptable de clôture de l'année : " + self.close_year.strftime('%Y') + " existe déjà")
        if not move :
            expense = [self.env.ref('account.data_account_type_expenses').id, self.env.ref('account.data_account_type_direct_costs').id , self.env.ref('account.data_account_type_depreciation').id ]
            income = [self.env.ref('account.data_account_type_other_income').id, self.env.ref('account.data_account_type_revenue').id]
            income_accounts = []
            for account in self.env['account.account'].search([('user_type_id','in',income)]):
                income_accounts.append(account.id)
            expense_accounts = []
            for account in self.env['account.account'].search([('user_type_id','in',expense)]):
                expense_accounts.append(account.id)
            income_lines = self.env['account.move.line'].search([('move_id.state', '=', 'posted'),('account_id','in',income_accounts),
                                                                 ('date','>=',self.close_year.replace(month=1, day=1)),
                                                                 ('date','<=',self.close_year.replace(month=12, day=31))])
            income_debit = 0
            income_credit = 0
            move = self.env['account.move'].create({
                'type': 'entry',
                'date':self.close_year.replace(month=12, day=31),
                'is_closing': True,
                'journal_id': self.journal_id.id
            })

            lines = []
            for income_line in income_lines:
                lines.append({
                    'name': income_line.name,
                    'move_id': move.id,
                    'account_id': income_line.account_id.id,
                    'debit': income_line.credit,
                    'credit': income_line.debit,
                })
                income_credit += income_line.debit
                income_debit += income_line.credit

            expense_lines = self.env['account.move.line'].search([('move_id.state', '=', 'posted'),('account_id','in',expense_accounts),
                                                                  ('date', '>=', self.close_year.replace(month=1, day=1)),
                                                                  ('date', '<=', self.close_year.replace(month=12, day=31))])
            expense_debit = 0
            expense_credit = 0
            for expense_line in expense_lines:
                lines.append({
                    'name': expense_line.name,
                    'move_id': move.id,
                    'account_id': expense_line.account_id.id,
                    'debit': expense_line.credit,
                    'credit': expense_line.debit,
                })
                expense_credit += expense_line.debit
                expense_debit += expense_line.credit
            credit = income_credit + expense_credit
            debit = income_debit + expense_debit
            lines.append(
                {
                    'name': 'Result',
                    'move_id': move.id,
                    'account_id': self.account_id.id,
                    'credit': (debit - credit) if debit > credit else 0,
                    'debit': (credit - debit )if credit > debit else 0
                }
            )
            move_lines = self.env['account.move.line'].create(lines)
            action_data = self.env.ref('account.action_move_journal_line').read()[0]
            action_data['res_id'] = move.id
            action_data['view_mode'] = 'form,tree,kanban'
            action_data['view_id'] = self.env.ref('account.view_move_form').id
            return {
                'name': _('Invoice created'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'account.move',
                'view_id': self.env.ref('account.view_move_form').id,
                'target': 'current',
                'res_id': move.id,
            }
        return self.env.ref('account.action_move_journal_line').read()[0]


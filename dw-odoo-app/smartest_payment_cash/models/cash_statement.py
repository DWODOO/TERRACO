# -*- coding: utf-8 -*-
import pdb

from odoo import models, api, fields, _
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta
from odoo.tools.float_utils import float_is_zero, float_compare


class CashStatement(models.Model):
    _name = 'cash.statement'
    _description = "Cash Statement"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Number', readonly=True, default='/')
    date = fields.Date("Date", required=True, default=fields.date.today(), tracking=True)
    note = fields.Text("Note", readonly=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('ongoing', 'En cours'),
        ('validated', 'Validated'),
        ('done', 'Cloturé'),
        ('canceled', 'Canceled'),
    ], default='draft', compute="_compute_cash_statement_state", store=True, tracking=True)
    journal_id = fields.Many2one('account.journal', domain="[('type', 'in', ['cash'])]", required=True, string="Journal")
    code_journal = fields.Char(related="journal_id.code")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    open_amount = fields.Monetary('Open Amount', currency_field="currency_id", tracking=True)
    total_amount = fields.Monetary('Total', compute="compute_payment_total_amount", currency_field="currency_id")
    close_amount = fields.Monetary('Close Amount', currency_field="currency_id", tracking=True)
    currency_id = fields.Many2one("res.currency", string='Currency', default=lambda self: self.env.user.company_id.currency_id)

    payment_customer_ids = fields.One2many('account.payment','cash_statement_id', string="Clients Payment(s)", readonly=True,  states={'ongoing': [('readonly', False)]}, domain=[('payment_type','=', 'inbound')])
    payment_supplier_ids = fields.One2many('account.payment','cash_statement_id', string="Supplier Payment(s)", readonly=True, states={'ongoing': [('readonly', False)]}, domain=[('payment_type','=', 'outbound')])

    use_last_cash_statement_closed_amount = fields.Boolean("Use Last Closed Amount", default=True)
    allow_negative_closed_amount = fields.Boolean("Allow negative closing Amount", default=False)
    # Cash register
    partner_id = fields.Many2one(
        'res.partner',
    )
    line_ids = fields.One2many(
        'cash.register.line',
        'cash_register_id'
    )
    line_total_amount = fields.Monetary(
        compute="compute_lines_total_amount",
        currency_field="currency_id",
        string='Lines Amount'
    )
    cash_register = fields.Boolean(
        related='journal_id.cash_register'
    )
    move_ids = fields.One2many(
        'account.move',
        'cash_id'
    )
    move_count = fields.Integer(
        compute='_compute_move_count'
    )

    _sql_constraints = [
        ('date_range_uniq', 'unique (date, journal_id, company_id)',
         'A Cash Statement can be opened once per day !')]

    def _compute_move_count(self):
        for record in self:
            record.move_count = len(record.move_ids)

    def action_view_moves(self):
        """
        This method is used by the picking smart button. It opens a form view or a tree view according to the
        declarations related pickings
        :return: Action Dict
        """
        move = self.mapped('move_ids')
        if not move:
            raise UserError(
                _('There is no Moves to view.')
            )
        tree_view = self.env.ref('account.view_move_tree')
        form_view = self.env.ref('account.view_move_form')
        action = {
            'name': _('Move(s)'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
        }

        action['views'] = [(tree_view.id, 'tree'), (form_view.id, 'form')]
        action['view_mode'] = 'tree'
        action['domain'] = [('id', 'in', move.ids)]
        action['context'] = {'default_cash_id': self.id}
        # action['search_view_id'] = (self.env.ref('biko.stock_production_lots_search').id,)

        return action

    def compute_lines_total_amount(self):
        for cash in self:
            cash.line_total_amount = sum(cash.line_ids.mapped('amount'))

    def compute_payment_total_amount(self):
        """compute total amount"""
        for cash in self:
            cash.total_amount = sum(cash.payment_customer_ids.mapped('amount_company_currency_signed')) \
                                + sum(cash.payment_supplier_ids.mapped('amount_company_currency_signed')) \
                + cash.open_amount - sum(cash.line_ids.mapped('amount')) \
                if (cash.payment_supplier_ids or cash.payment_customer_ids or cash.line_ids) else cash.open_amount

    def action_validate_statement(self):
        for cash in self:
            if cash.state == 'draft':
                cash._check_previous_cash_statement_state()
                cash._compute_name()
                cash['state'] = 'ongoing'
            elif cash.state == 'ongoing':
                cash._check_total_closed()
                cash._check_payments_states()

    def _compute_name(self):
        for cash in self:
            cash['name'] = str(cash.code_journal) + '/' + str(cash.date)

    def _check_total_closed(self):
        """check total amount closed """
        for cash in self:
            if cash.total_amount != cash.close_amount:
                raise ValidationError(
                    _('You can\'t close an unbalanced cash statement, Please make sure the Total and the Closed Amount are equals.')
                )
            elif cash.close_amount < 0 and not cash.allow_negative_closed_amount:
                raise ValidationError(
                    _('You can\'t close a negative cash statement, Please make sure all the operation has been correct.')
                )
            elif any(cash.line_ids.filtered(lambda o: o.state == 'draft')):
                raise ValidationError(
                    _('You can\'t close cash statement, Please make sure all the lines are posted.')
                )

    @api.onchange('use_last_cash_statement_closed_amount', 'journal_id', 'date')
    def on_change_use_last_cash_statement_closed_amount(self):
        for this in self:
            this.open_amount = 0
            last_cash_payment_closed_amount = self.env['cash.statement'].search([
                ('date', '<', this.date), ('journal_id', '=', this.journal_id.id)], order="date desc",
                limit=1).close_amount
            if this.use_last_cash_statement_closed_amount and this.journal_id and last_cash_payment_closed_amount:
                this.open_amount = last_cash_payment_closed_amount
            elif not this.use_last_cash_statement_closed_amount and this.open_amount != 0 and last_cash_payment_closed_amount:
                this.open_amount = 0

    def _check_previous_cash_statement_state(self):
        for this in self:
            previous_statements = self.env['cash.statement'].search([('date','<',this.date),('journal_id','=',this.journal_id.id),('state','in',['draft','ongoing'])])
            if previous_statements:
                raise ValidationError(
                    _('You have old cash statement unclosed, Please make sure to Close them !.')
                )

    def _check_payments_states(self):
        for cash_statement in self:
            no_posted_payments = cash_statement.mapped('payment_customer_ids').filtered(lambda this: this.state == 'draft')
            no_posted_bills = cash_statement.mapped('payment_supplier_ids').filtered(lambda this: this.state not in  ['posted','cancel'])
            no_posted_entries = cash_statement.mapped('line_ids').filtered(lambda this: this.state not in ['posted', 'cancel'])
            if no_posted_bills or no_posted_payments or no_posted_entries and cash_statement.state in ['ongoing']:
                cash_statement['state'] = 'validated'
                return
            else:
                cash_statement['state'] = 'done'
                return

    @api.depends('payment_customer_ids.state', 'payment_supplier_ids.state')
    def _compute_cash_statement_state(self):
        for cash_statement in self:
            if cash_statement.state == 'validated':
                no_posted_payments = cash_statement.mapped('payment_customer_ids').filtered(lambda this: this.state == 'draft')
                no_posted_bills = cash_statement.mapped('payment_supplier_ids').filtered(lambda this: this.state not in  ['posted','cancel'])
                if not no_posted_payments and not no_posted_bills :
                    cash_statement['state'] = 'done'

    def action_add_incoming_payment_from_show_invoice(self):
        invoices = self.env['account.move'].search([('state', '=', 'posted'),('payment_state', 'not in', ['paid','in_payment']), ('move_type', '=', 'out_invoice')])
        tree_view = self.env.ref('account.view_out_invoice_tree')
        action = {
            'name': _('Facture(s)'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'views':[(tree_view.id, 'tree')],
            'domain':[('id', 'in', invoices.ids)],
            'context':{'group_by': ['partner_id'],'create': False,
                       },
        }

        return action

    def action_add_outgoing_payment_from_show_invoice(self):
        invoices = self.env['account.move'].search([('state', '=', 'posted'),('payment_state', 'not in', ['paid','in_payment']), ('move_type', '=', 'in_invoice')])
        tree_view = self.env.ref('account.view_out_invoice_tree')
        action = {
            'name': _('Facture(s)'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'views':[(tree_view.id, 'tree')],
            'domain':[('id', 'in', invoices.ids)],
            'context':{'group_by': ['partner_id'],'create': False,},
        }

        return action

    def unlink(self):
        """
        Overriding unlink method to disallow unlink no draft statement
        """
        if self.filtered(lambda t: t.state != 'draft'):
            raise UserError(
                _('Only draft cash statement can be deleted')
            )
        return super(CashStatement, self).unlink()
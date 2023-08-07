import pdb

from odoo import models, api, fields, _
from odoo.exceptions import UserError


class CashTicketCancel(models.Model):
    _name = 'cash.ticket.cancel'
    _description = "Cash Ticket Cancel"
    _order = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        "Name",
        readonly=True,
        store=True,
    )
    date = fields.Date(
        "Date",
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=fields.date.today()
    )
    note = fields.Text(
        "Note",
        readonly=True,
        states={'draft': [('readonly', False)]},
        tracking=True
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
    ],
        default='draft',
        tracking=True,
    )
    cash_ticket_id = fields.Many2one(
        'cash.ticket',
        'Cash Ticket',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
        domain="[('state', '=', 'validated')]",
        tracking=True,
        ondelete="cascade"
    )
    partner_id = fields.Many2one(
        related='cash_ticket_id.partner_id'
    )
    cash_desk_id = fields.Many2one(
        related='cash_ticket_id.cash_desk_id'
    )
    currency_id = fields.Many2one(
        related='cash_ticket_id.currency_id',
    )
    amount = fields.Monetary(
        "Ticket Amount",
        currency_field="currency_id",
        compute="_compute_amounts",
    )
    amount_residual = fields.Monetary(
        "Ticket Amount Residual",
        currency_field="currency_id",
        compute="_compute_amounts",
    )
    amount_paid = fields.Monetary(
        "Ticket Amount Paid",
        currency_field="currency_id",
        compute="_compute_amounts",
    )

    @api.depends('cash_ticket_id')
    def _compute_amounts(self):
        """
        According to ticket to be cancelled this method compute the values of the following fields: amount,
        amount_residual and amount_paid
        """
        for ticket in self:
            ticket.amount = ticket.cash_ticket_id.amount
            ticket.amount_residual = ticket.cash_ticket_id.amount_residual
            ticket.amount_paid = -ticket.cash_ticket_id.amount_paid

    def _action_cancel_ticket(self):
        """
        This method is called by the action button method 'action_confirm'.
        Calling this method cause canceling the ticket payments, updating related cash.ticket record state to cancel
        and update its related cancel_ticket to the current record.
        """
        payment_ids = self.mapped('cash_ticket_id.payment_ids')
        payment_ids.filtered(lambda p: p.state != 'draft').action_draft()
        payment_ids.action_cancel()
        for ticket in self:
            ticket.cash_ticket_id.write({
                'state': 'canceled',
                'ticket_cancel_id': ticket.id
            })

    def action_confirm(self):
        """
        This method is used by the action button 'confirm'.
        This method call the '_action_cancel_ticket' method and update the cancel ticket state to 'confirm'
        :return:
        """
        if self.filtered(lambda tc: tc.state != 'draft'):
            raise UserError(
                _("Only draft ticket can be confirmed")
            )
        self._action_cancel_ticket()
        return self.write({
            'state': 'confirm'
        })

    @api.model_create_multi
    def create(self, vals_list):
        """
        Overriding the create method to setup automatically the  cancel ticket name by getting sequence
        :param vals_list: List of dicts of the aimed created cancel tickets
        :return: List of cash.ticket.cancel records
        """
        sequence_id = self.env.ref('smartest_payment_cash.cash_ticket_cancel_sequence')
        for vals in vals_list:
            vals['name'] = sequence_id.next_by_id()
        return super(CashTicketCancel, self).create(vals_list)

    def unlink(self):
        """
        Overriding unlink method to disallow unlink no draft cancel tickets
        """
        if self.filtered(lambda tc: tc.state != 'draft'):
            raise UserError(
                _("Only draft ticket can be deleted")
            )
        return super(CashTicketCancel, self).unlink()
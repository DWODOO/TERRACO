# -*- coding: utf-8 -*-
from odoo import models, api, fields, _


class CashDesk(models.Model):
    _name = 'cash.desk'
    _description = "Cash Desk"
    _order = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        "Name",
        required=True,
        tracking=True,
    )
    code = fields.Char(
        "Code",
        tracking=True,
        copy=False,
    )
    active = fields.Boolean(
        'Active',
        default=True
    )
    journal_id = fields.Many2one(
        "account.journal",
        domain="[('type', 'in', ('sale', 'cash'))]",
        required=True,
        store=True,
        tracking=True,
    )
    close_account_id = fields.Many2one(
        "account.account",
        tracking=True,
    )
    description = fields.Text(
        "Description",
        tracking=True,
    )
    user_ids = fields.Many2many(
        'res.users',
        string='Users',
        tracking=True,
    )
    user_count = fields.Integer(
        "Users count",
        compute="_compute_user_count"
    )
    ticket_ids = fields.One2many(
        'cash.ticket',
        'cash_desk_id',
        'Tickets',
    )
    ticket_count = fields.Integer(
        compute="_compute_ticket_count"
    )

    _sql_constraints = [
        ('uniq_code', 'unique(code)', 'The cash point must be unique.')
    ]

    @api.depends('user_ids')
    def _compute_user_count(self):
        """
        Compute the number of related users.
        This computed value is used on the Smart Button that open the associated users.
        :return: int -> number of user
        """
        for desk in self:
            desk.user_count = len(desk.user_ids)

    @api.depends('ticket_ids')
    def _compute_ticket_count(self):
        """
        Compute the number of related tickets.
        This computed value is used on the Smart Button that open the associated tickets.
        :return: int -> number of tickets
        """
        for desk in self:
            desk.ticket_count = len(desk.ticket_ids)

    def action_view_tickets(self):
        """
        This method is an action called by the Tickets Smart Button on the cash.desk form View.
        This method show a form view or a tree view according to the number of the record related tickets.
        :return: Action Dict
        """
        ticket_ids = self.mapped('ticket_ids')
        if not ticket_ids:
            raise ticket_ids(
                _('There is no ticket to view.')
            )
        tree_view = self.env.ref('smartest_payment_cash.cash_ticket_view_tree')
        form_view = self.env.ref('smartest_payment_cash.cash_ticket_view_form')
        action = {
            'name': _('Ticket(s)'),
            'type': 'ir.actions.act_window',
            'res_model': 'cash.ticket',
        }
        if len(ticket_ids) == 1:
            action['views'] = [(form_view.id, 'form')]
            action['res_id'] = ticket_ids.id
            action['view_mode'] = 'form'
        else:
            action['views'] = [(tree_view.id, 'tree'), (form_view.id, 'form')]
            action['domain'] = [('id', 'in', ticket_ids.ids)]
        return action

    def action_view_users(self):
        """
        This method is an action called by the Users Smart Button on the cash.desk form View.
        This method show a form view or a tree view according to the number of the record associated users.
        :return: Action Dict
        """
        user_ids = self.mapped('user_ids')
        if not user_ids:
            raise user_ids(
                _('There is no user to view.')
            )
        tree_view = self.env.ref('base.view_users_tree')
        form_view = self.env.ref('base.view_users_form')
        action = {
            'name': _('User(s)'),
            'type': 'ir.actions.act_window',
            'res_model': 'res.users',
        }
        if len(user_ids) == 1:
            action['views'] = [(form_view.id, 'form')]
            action['res_id'] = user_ids.id
            action['view_mode'] = 'form'
        else:
            action['views'] = [(tree_view.id, 'tree'), (form_view.id, 'form')]
            action['domain'] = [('id', 'in', user_ids.ids)]
        return action

    def name_get(self):
        """
        We override this method in order to display the name of a cash.desk record as [CODE] NAME if the record
        has a code value
        :return: list((id, display_name))
        """
        desk_with_code = self.filtered(lambda d: d.code)
        return [
                   (desk.id, "[{code}] {name}".format(code=desk.code, name=desk.name)) for desk in desk_with_code
               ] + super(CashDesk, self - desk_with_code).name_get()

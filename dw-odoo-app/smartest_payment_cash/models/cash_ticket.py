# -*- coding: utf-8 -*-
from odoo import models, api, fields, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero, float_compare


class CashTicketLine(models.Model):
    _name = 'cash.ticket.line'
    _description = "Cash Ticket Line"
    _order = 'cash_ticket_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _get_default_cash_desk_id(self):
        return self.env['cash.desk'].search([], limit=1)

    cash_ticket_id = fields.Many2one(
        'cash.ticket',
        'Cash Ticket',
        required=True,
        readonly=True,
        store=True,
        ondelete='cascade',
        tracking=True,
    )
    payment_method_id = fields.Many2one(
        "account.payment.method",
        string="Method",
        default=lambda self: self.env.ref('smartest_payment_cash.account_payment_method_cash_in', False),
        domain="['|', ('code', '=', 'cash.ticket.cash'), ('code', '=', 'cash.ticket.check'), "
               "('payment_type', '=', 'inbound')]",
        required=True,
        tracking=True,
    )
    reference = fields.Char(
        'Reference'
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
    account_payment_ids = fields.One2many(
        'account.payment',
        'ticket_line_id',
        'Payment'
    )
    cash_desk_id = fields.Many2one(
        'cash.desk',
        'Cash Desk',
        readonly=True,
        store=True,
        default=_get_default_cash_desk_id
    )
    company_id = fields.Many2one(
        related="cash_ticket_id.company_id"
    )

    def _get_reconciliation_invoice(self, invoice_ids=None):
        """
        This method reconcile the the cash.ticket.line payment amount with the given invoices.
        :param invoice_ids: The invoice to reconcile with the payment. If this parameter is not defined
        the cash_ticket_id.invoice_ids will be used
        :return: List of fully paid and reconciled invoices and List of partially paid invoices
        """
        self.ensure_one()
        amount = self.amount
        reconciliation_invoices = self.env['account.move']
        partially_paid_invoices = self.env['account.move']
        if not invoice_ids:
            invoice_ids = self.cash_ticket_id.invoice_ids
        for invoice in invoice_ids:
            reconciliation_invoices += invoice
            amount -= invoice.amount_residual
            if float_compare(amount, 0, precision_rounding=self.currency_id.rounding) == 0:
                break
            elif float_compare(amount, 0, precision_rounding=self.currency_id.rounding) == -1:
                partially_paid_invoices += invoice
                break
        return reconciliation_invoices, partially_paid_invoices

    def _prepare_payment_vals(self):
        """
        This method is used to generate values of account.payment records when closing the ticket.
        :return: List of Dict containing account.payment values
        """
        company = self.env.user.company_id
        vals_list = []
        ticket_ids = self.mapped('cash_ticket_id')
        for ticket in ticket_ids:
            invoice_ids = ticket.invoice_ids
            for line in self.filtered(lambda l: l.cash_ticket_id == ticket):
                vals = {
                    'partner_id': ticket.partner_id.id,
                    'journal_id': ticket.journal_id.id,
                    'amount': line.amount,
                    'currency_id': line.currency_id.id,
                    'ticket_line_id': line.id,
                    'payment_method_id': line.payment_method_id.id,
                    'payment_reference': line.reference,
                    'payment_type': 'inbound',
                    'partner_type': 'customer',
                }
                if (line.company_id or company).auto_reconciliation:
                    reconciliation_invoice, partially_paid_invoice = line._get_reconciliation_invoice(invoice_ids)
                    vals['reconciled_invoice_ids'] = [(4, inv.id) for inv in reconciliation_invoice]
                    invoice_ids -= reconciliation_invoice
                    invoice_ids += partially_paid_invoice
                vals_list.append(vals)
        return vals_list

    def create_account_payments(self):
        """
        This method create and return the related account.payment record
        :return: List of newly created account.payment records
        """
        if self.filtered(lambda line: line.account_payment_ids):
            raise UserError(
                "You can not create multiple Account Payment for a single Ticket Line"
            )
        return self.env['account.payment'].create(self._prepare_payment_vals())

    @api.model_create_multi
    def create(self, vals_list):
        """
        Override the create method in order to :
            1- Add cash desk control: User can not create a ticket line on a not associated cash desk
            2- If no cash.desk is defined on the ticket.line, Associate the user current cash.desk
        :param vals_list: List of dicts that will be created
        :return: List of cash.ticket.line records
        """
        user = self.env.user
        cash_desk_ids = user.cash_desk_ids
        if not cash_desk_ids:
            raise UserError(
                _("You are not allowed to create cash payment lines. "
                  "Please ask your administrator to associate your profile to a cash desk")
            )
        for vals in vals_list:
            ticket_cash_desk_id = vals.get("cash_desk_id")
            if ticket_cash_desk_id and ticket_cash_desk_id not in cash_desk_ids.ids:
                raise UserError(
                    _("You are not allowed to create cash payment lines on this cash desk. ")
                )
            if not ticket_cash_desk_id:
                vals["cash_desk_id"] = user.cash_desk_id.id or cash_desk_ids.ids[0]
        return super(CashTicketLine, self).create(vals_list)


class CashTicket(models.Model):
    _name = 'cash.ticket'
    _description = "Cash Ticket"
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
        readonly=False,
        states={'validated': [('readonly', True)], 'canceled': [('readonly', True)]},
        default=fields.date.today()
    )
    note = fields.Text(
        "Note",
        readonly=False,
        states={'validated': [('readonly', True)], 'canceled': [('readonly', True)]},
        tracking=True
    )
    source = fields.Char(
        "Source",
        tracking=True,
        readonly=False,
        states={'validated': [('readonly', True)], 'canceled': [('readonly', True)]},
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('partially_paid', 'Partially Paid'),
        ('paid', 'Paid'),
        ('validated', 'validated'),
        ('canceled', 'Canceled'),
    ],
        default='draft',
        compute='_compute_state',
        store=True,
        tracking=True,
    )
    invoice_ids = fields.Many2many(
        "account.move",
        string="Invoices",
        readonly=False,
        states={'validated': [('readonly', True)], 'canceled': [('readonly', True)]},
        store=True,
        required=True,
        domain="[('move_type', '=', 'out_invoice'), ('amount_residual', '>', 0), ('payment_state', 'in', ['not_paid', 'in_payment', 'partial'])]"
    )
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.user.company_id,
        readonly=False,
        states={'validated': [('readonly', True)], 'canceled': [('readonly', True)]},
    )
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.user.company_id.currency_id,
        readonly=False,
        states={'validated': [('readonly', True)], 'canceled': [('readonly', True)]},
    )
    sale_order_ids = fields.Many2many(
        'sale.order',
        'ticket_so_rel',
        'ticket_id',
        'so_id',
        string="Sale orders",
        compute="_compute_order_ids"
    )
    partner_id = fields.Many2one(
        'res.partner',
        'Customer',
        required=True,
        store=True,
        readonly=False,
        states={'validated': [('readonly', True)], 'canceled': [('readonly', True)]},
        domain=[('is_customer', '=', True)],
    )
    amount = fields.Monetary(
        string="Amount",
        currency_field="currency_id",
        compute="_compute_amount",
    )
    amount_residual = fields.Monetary(
        string="Amount Residual",
        compute="_compute_amounts",
        currency_field="currency_id",
    )
    amount_paid = fields.Monetary(
        string="Amount Paid",
        compute="_compute_amounts",
        currency_field="currency_id",
    )
    payment_ids = fields.One2many(
        'account.payment',
        "cash_ticket_id",
        tracking=True,
        readonly=True,
    )
    move_line_ids = fields.Many2many(
        'account.move.line',
        compute="_compute_move_line_ids",
    )
    ticket_line_ids = fields.One2many(
        'cash.ticket.line',
        "cash_ticket_id",
        tracking=True
    )
    cash_desk_id = fields.Many2one(
        'cash.desk',
        'Cash Desk',
        domain=lambda self: [('id', 'in', self.env.user.cash_desk_ids.ids)],
        default=lambda self: self.env.user.cash_desk_id,
        required=True,
        store=True,
        readonly=False,
        states={'validated': [('readonly', True)], 'canceled': [('readonly', True)]},
    )
    journal_id = fields.Many2one(
        related="cash_desk_id.journal_id"
    )
    sale_order_count = fields.Integer(
        compute="_compute_order_ids"
    )
    invoice_count = fields.Integer(
        compute="_compute_order_ids"
    )
    ticket_cancel_id = fields.Many2one(
        'cash.ticket.cancel',
        'Cancel Ticket',
        readonly=True,
        store=True,
    )
    is_closed = fields.Boolean(
        'Closed?',
        readonly=True,
        store=True,
    )  # Technical field used to determine if this ticket is already closed or not.

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """
        According to the partner_id field value add a filter on invoice_ids to allow only selecting the related
        partner out invoices with a positive residual amount.
        :return: Invoice Filter Domain
        """
        self.invoice_ids = False
        res = {
            'domain': {
                'invoice_ids': [
                    ('move_type', '=', 'out_invoice'),
                    ('amount_residual', '>', 0),
                    ('payment_state', 'in', ['not_paid', 'in_payment', 'partial'])
                ]
            }
        }
        if self.partner_id:
            res['domain']['invoice_ids'].append(('partner_id', '=', self.partner_id.id))
        return res

    @api.depends('payment_ids', 'ticket_line_ids', 'amount_residual', 'amount_paid', 'amount')
    def _compute_state(self):
        """
        This method is used to compute state according to payment state:
            1- If the total amount paid is great or equal to the total invoices amount mark as 'paid'.
            2- If the total amount paid is not zero and it's less than the total invoices amount mark
            as 'partially_paid'.
            3- If the total amount paid is zero mark  as 'draft'.
            3- If state is 'canceled' or 'validated' do not change it because those state are defined by action buttons.
        """
        current_company = self.env.user.company_id
        mark_as_paid = self.env['cash.ticket']
        mark_as_partially_paid = self.env['cash.ticket']
        mark_as_draft = self.env['cash.ticket']
        for ticket in self.filtered(lambda t: t.state not in ('canceled', 'validated')):
            rounding = ticket.currency_id.rounding or current_company.currency_id.rounding
            if ticket.ticket_line_ids:
                if not float_is_zero(ticket.amount_residual, precision_rounding=rounding) \
                        and float_is_zero(ticket.amount_paid, precision_rounding=rounding):
                    mark_as_draft += ticket
                elif float_is_zero(ticket.amount_residual, precision_rounding=rounding):
                    mark_as_paid += ticket
                elif not float_is_zero(ticket.amount_paid, precision_rounding=rounding) \
                        and not float_is_zero(ticket.amount_residual, precision_rounding=rounding):
                    mark_as_partially_paid += ticket
            else:
                mark_as_draft += ticket
        try:

            if mark_as_paid:
                mark_as_paid.write({'state': 'paid'})
            if mark_as_partially_paid:
                mark_as_partially_paid.write({'state': 'partially_paid'})
            if mark_as_draft:
                mark_as_draft.write({'state': 'draft'})
        except Exception:
            pass

    @api.depends('payment_ids')
    def _compute_move_line_ids(self):
        """
        This method is used to compute account.move.line records related to the account.payment records.
        The move_line_ids field is used only on the cash.ticket form view.
        """
        for ticket in self:
            ticket.move_line_ids = ticket.mapped('payment_ids.invoice_line_ids')

    @api.depends('invoice_ids')
    def _compute_order_ids(self):
        """
        According to invoice_ids field compute the related maintenance.order records, sale.order records,
        maintenance.order records count, sale.order records count and invoice count.
        All above computation fields are used to indicate respectively: The ticket related maintenance orders,
        the ticket related sale orders, the number of related maintenance orders and the number of the related
        sale orders.
        """
        for ticket in self:
            ticket.sale_order_ids = ticket.mapped('invoice_ids.sale_order_ids')
            ticket.sale_order_count = len(ticket.sale_order_ids)
            ticket.invoice_count = len(ticket.invoice_ids)

    @api.depends('invoice_ids', 'date', 'currency_id')
    def _compute_amount(self):
        """
        According to the selected invoices, date and the currency recompute the total amount to pay by this ticket.
        """
        current_company = self.env.user.company_id
        for ticket in self:
            amount = 0
            for invoice in ticket.invoice_ids:
                amount += invoice.currency_id._convert(
                    invoice.amount_residual,
                    ticket.currency_id,
                    ticket.company_id or current_company,
                    ticket.date or fields.Date.today()
                )
            ticket.amount = amount

    @api.depends('ticket_line_ids', 'amount')
    def _compute_amounts(self):
        """
        According to the entered ticket lines and the computed amount to pay recompute paid and the residual amounts.
        """
        current_company = self.env.user.company_id
        for ticket in self:
            amount_paid = 0
            ticket_line_ids = ticket.ticket_line_ids
            for line in ticket_line_ids:
                amount_paid += line.currency_id._convert(
                    line.amount,
                    ticket.currency_id,
                    ticket.company_id or current_company,
                    ticket.date or fields.Date.today()
                )
            amount_residual = ticket.amount - amount_paid
            ticket.update({
                'amount_paid': amount_paid,
                'amount_residual': amount_residual}
            )

    def _unlink_zero_amount_lines(self):
        """
        This Method delete all the Cash Ticket lines with amount zero
        """
        default_rounding = self.env.user.company_id.currency_id.rounding
        return self.mapped('ticket_line_ids').filtered(
            lambda line: float_is_zero(line.amount, precision_rounding=line.currency_id.rounding or default_rounding)
        ).unlink()

    def _action_validate(self):
        """
        This method is called by the button action method 'action_validate'.
        This method change the state of the ticket to 'validate' and associate the current user cash.desk to the ticket and
        unlink all zero amount ticket lines.
        """
        cash_desk_ids = self.env.user.cash_desk_ids
        for ticket in self:
            if ticket.state not in ['paid', 'partially_paid']:
                raise UserError(
                    _("Only paid or partially paid ticket can be validated.")
                )
            if ticket.cash_desk_id not in cash_desk_ids:
                raise UserError(
                    _("You are allowed to confirm a ticket on this cash desk.")
                )
        self.write({'state': 'validated'})
        return self._unlink_zero_amount_lines()

    def action_validate(self):
        """
        This method is used by the validate action button.
        This method validate the ticket by calling '_action_validate' method, generate the related account.payment records
        for each ticket.line then confirm those payments.
        """
        # Close The ticket
        self._action_validate()
        # Post Invoices
        current_company = self.env.user.company_id
        for ticket in self:
            if (ticket.company_id or current_company).auto_invoice_post:
                ticket.invoice_ids.filtered(lambda inv: inv.state == 'draft').action_post()
        # Create Account Payments
        not_payed_lines = self.mapped('ticket_line_ids').filtered(lambda line: not line.account_payment_ids)
        payment_ids = not_payed_lines.create_account_payments()
        return payment_ids.move_id._post()

    def action_open(self):
        """
        This method is used by the open action button and it's a cash manager access level.
        This method change the state of validated ticket to 'partially_paid' and give the user the ability to update
        the ticket.
        """
        if self.filtered(lambda t: t.state != 'validated'):
            raise UserError(
                _("Only validated ticket can be opened.")
            )
        rounding = self.env.user.company_id.currency_id.rounding
        if self.filtered(
                lambda t: float_is_zero(t.amount_residual, precision_rounding=t.currency_id.rounding or rounding)
        ):
            raise UserError(
                _("Only ticket with a residual amount can be opened.")
            )
        return self.write({'state': 'partially_paid'})

    def action_cancel(self):
        """
        This method is used by the cancel action button.
        This method create an canceling ticket (cash.ticket.cancel record)
        :return action to open cash.ticket.cancel form view on create mode.
        """
        self.ensure_one()
        action = self.env.ref('smartest_payment_cash.cash_ticket_cancel_action')
        result = action.read()[0]
        # override the context to get rid of the default filtering
        result['context'] = {
            'default_cash_ticket_id': self.id
        }
        res = self.env.ref('smartest_payment_cash.cash_ticket_cancel_view_form', False)
        form_view = [(res and res.id or False, 'form')]
        if 'views' in result:
            result['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
        else:
            result['views'] = form_view
        return result

    def action_view_sales(self):
        """
        This method is an action called by the Sales Smart Button on the cash.ticket form View.
        This method show a form view or a tree view according to the number of the record related sales.
        :return: Action Dict
        """
        sales = self.mapped('sale_order_ides')
        if not sales:
            raise UserError(
                _('There is no sale to view.')
            )
        tree_view = self.env.ref('sale.view_order_tree')
        form_view = self.env.ref('sale.view_order_form')
        action = {
            'name': _('Sale(s)'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
        }
        if len(sales) == 1:
            action['views'] = [(form_view.id, 'form')]
            action['res_id'] = sales.id
            action['view_mode'] = 'form'
        else:
            action['views'] = [(tree_view.id, 'tree'), (form_view.id, 'form')]
            action['domain'] = [('id', 'in', sales.ids)]
        return action

    def action_view_invoices(self):
        """
        This method is an action called by the Invoice Smart Button on the cash.ticket form View.
        This method show a form view or a tree view according to the number of the record related invoices.
        :return: Action Dict
        """
        invoices = self.mapped('invoice_ids')
        if not invoices:
            raise UserError(
                _('There is no invoice to view.')
            )
        tree_view = self.env.ref('account.view_invoice_tree')
        form_view = self.env.ref('account.view_move_form')
        action = {
            'name': _('Invoice(s)'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
        }
        if len(invoices) == 1:
            action['views'] = [(form_view.id, 'form')]
            action['res_id'] = invoices.id
            action['view_mode'] = 'form'
        else:
            action['views'] = [(tree_view.id, 'tree'), (form_view.id, 'form')]
            action['domain'] = [('id', 'in', invoices.ids)]
        return action

    @api.model_create_multi
    def create(self, vals_list):
        """
        Overriding the create method to setup automatically the ticket name by getting sequence and also to update the
        user current cash_desk_id according to the ticket used cash_desk_id
        :param vals_list: List of dicts of the aimed created tickets
        :return: List of cash.ticket records
        """
        sequence_id = self.env.ref('smartest_payment_cash.cash_ticket_sequence')
        user = self.env.user
        for vals in vals_list:
            vals['name'] = sequence_id.next_by_id()
            if vals.get('cash_desk_id'):
                user.write({'cash_desk_id': vals['cash_desk_id']})
        return super(CashTicket, self).create(vals_list)

    def write(self, vals):
        """
        Overriding the write method to update the user current cash desk according to the ticket used cash_desk_id
        :param vals: Dict of the aimed edited fields
        """
        if vals.get('cash_desk_id'):
            self.env.user.write({'cash_desk_id': vals['cash_desk_id']})
        return super(CashTicket, self).write(vals)

    def unlink(self):
        """
        Overriding unlink method to disallow unlink no draft tickets
        """
        if self.filtered(lambda t: t.state != 'draft'):
            raise UserError(
                _('Only draft tickets can be deleted')
            )
        return super(CashTicket, self).unlink()

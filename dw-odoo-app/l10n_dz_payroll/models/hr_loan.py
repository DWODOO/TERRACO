# -*- encoding: utf-8 -*-
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError, UserError


class HrLoan(models.Model):
    _name = "hr.loan"
    _description = "Employee loan"
    _inherit = ['mail.thread']

    name = fields.Char(
        'Name',
        default="/",
        required=True,
        readonly=True,
        store=True
    )
    sequence = fields.Integer(
        'Sequence',
        help="Gives the sequence order when displaying a list of sales order lines."
    )
    amount_loan = fields.Monetary(
        'Loan/Advance amount',
        # digits='Payroll',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        currency_field="company_currency_id"
    )
    employee_id = fields.Many2one(
        'hr.employee',
        'Employee',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    refund_months = fields.Integer(
        'Refund month number',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=1
    )
    date_loan = fields.Date(
        'Loan/Advance Date',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    date_refund = fields.Date(
        'Refund date',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    refund_amount = fields.Monetary(
        'Refund amount',
        # digits=dp.get_precision('Payroll'),
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        currency_field="company_currency_id"
    )
    amount_refunded = fields.Monetary(
        'Amount refunded',
        # digits=dp.get_precision('Payroll'),
        compute='_compute_total',
        currency_field="company_currency_id"
    )
    amount_refund_remaining = fields.Monetary(
        'Remaining refund amount',
        # digits=dp.get_precision('Payroll'),
        compute='_compute_total',
        currency_field="company_currency_id"
    )
    notes = fields.Text(
        'Notes'
    )
    company_id = fields.Many2one(
        'res.company',
        'Company',
        required=True,
        index=True,
        default=lambda self: self.env.user.company_id,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    company_currency_id = fields.Many2one('res.currency',
        string='Currency',
        related='company_id.currency_id',
        readonly=True,
    )

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('paid', 'Paid'),
            ('cancelled', 'Canceled')
        ],
        'State',
        default="draft",
        store=True,
    )
    loan_line_ids = fields.One2many(
        'hr.loan.refund.line',
        'loan_id',
        'Loan Lines',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )

    type = fields.Selection(
        [
            ('advance', 'advance'),
            ('loan', 'Loan')
        ],
        "Type",
        default='advance',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )


    def update_state(self):
        for loan in self:
            if not loan.loan_line_ids.filtered(lambda l: l.payment_state != 'paid'):
                loan.state = 'paid'
            elif not loan.loan_line_ids.filtered(lambda l: l.payment_state != 'canceled'):
                loan.state = 'canceled'

    @api.depends('amount_loan', 'loan_line_ids', 'loan_line_ids.payment_state')
    def _compute_total(self):
        for loan in self:
            refunded = 0.0
            for line in loan.loan_line_ids:
                if line.payment_state not in ('waiting', 'postponed'):
                    refunded += line.refund_amount
            remaining = round(loan.amount_loan - refunded, 2)
            if remaining < 0:
                raise ValidationError(
                    _('It is not possible to refund more than the loaned amount.')
                )
            loan.amount_refunded = refunded
            loan.amount_refund_remaining = remaining


    def action_compute_refund_board(self):
        lines = []
        loans = self.filtered(lambda l: l.amount_loan > 0)
        loans.mapped('loan_line_ids').unlink()
        for loan in loans:
            deduction_date = datetime(loan.date_refund.year, loan.date_refund.month, 1)

            day = deduction_date.day
            month = deduction_date.month
            year = deduction_date.year

            amount = loan.refund_amount
            quotient = loan.amount_loan // amount
            remainder = loan.amount_loan % amount
            sequence = 1
            for x in range(len(loan.loan_line_ids), int(quotient)):
                sequence = x + 1
                lines.append({
                    'refund_amount': amount,
                    'loan_id': loan.id,
                    'date': deduction_date.strftime('%Y-%m-%d'),
                    'sequence': sequence,
                })
                deduction_date = (datetime(year, month, day) + relativedelta(months=+loan.refund_months))
                day = deduction_date.day
                month = deduction_date.month
                year = deduction_date.year

            if remainder > 0:
                lines.append({
                    'refund_amount': remainder,
                    'loan_id': loan.id,
                    'date': deduction_date.strftime('%Y-%m-%d'),
                    'sequence': sequence,
                })
        self.env['hr.loan.refund.line'].create(lines)
        return True


    def action_confirm(self):
        for loan in self.filtered(lambda l: l.name in (False, _('/'))):
            if loan.type == 'advance':
                loan.name = '%s%s' % (_('ADVANCE'), self.env['ir.sequence'].next_by_code('hr.loan') or '')
            else:
                loan.name = '%s%s' % (_('LOAN'), self.env['ir.sequence'].next_by_code('hr.advance') or '')
        self.write({'state': 'confirmed'})
        return True


    def action_draft(self):
        self.write({'state': 'draft'})
        return True


    def unlink(self):
        if self.filtered(lambda loan: loan.state != 'draft'):
            raise UserError(
                _("You can not remove confirmed or paid loans !")
            )
        return super(HrLoan, self).unlink()


class HrLoanLine(models.Model):
    _name = 'hr.loan.refund.line'
    _description = 'Loan Refund Line'
    _order = 'sequence'

    loan_id = fields.Many2one(
        'hr.loan',
        string='Loan',
        required=True,
        ondelete='cascade'
    )
    payslip_id = fields.Many2one(
        'hr.payslip',
        string='Payslip',
    )
    company_currency_id = fields.Many2one('res.currency',
        string='Currency',
        related='loan_id.company_currency_id',
        readonly=True,
    )
    employee_id = fields.Many2one(
        related='loan_id.employee_id',
        string='Employee',
        index=True
    )
    sequence = fields.Integer(
        'Sequence'
    )
    payment_state = fields.Selection(
        [
            ('waiting', 'Waiting'),
            ('paid', 'Paid'),
            ('postponed', 'Postponed'),
            ('canceled', 'Canceled')
        ],
        string='Payment Status',
        default="waiting"
    )
    date_refund = fields.Date(
        string='Payslip refund date',
        readonly=True,
        index=True
    )
    refund_amount = fields.Monetary(
        string='Refund amount',
        currency_field="company_currency_id",
        digits=dp.get_precision('Payroll')
    )
    date = fields.Date(
        string='Refund date',
        required=True
    )
    state = fields.Selection(
        [
            ('draft', 'draft'),
            ('confirmed', 'Confirmed'),
            ('paid', 'Paid'),
            ('cancelled', 'Canceled')
        ],
        'State',
        related='loan_id.state'
    )


    def unlink(self):
        context = self._context or {}
        if not (context.get('force', False)):
            if self.filtered(lambda l: l.date_refund):
                raise ValidationError(
                    _('It is not possible to delete refunded loan.')
                )
        super(HrLoanLine, self).unlink()


    def action_postpone(self):
        self.ensure_one()
        return {
            'name': _('Refund Postpone '),
            'type': 'ir.actions.act_window',
            'res_model': "hr.loan.postpone.wizard",
            'views': [(self.env.ref('l10n_dz_payroll.loan_postpone_form').id, 'form')],
            'target': 'new',
            'context': {
                'default_loan_line_id': self.id,
                'default_date': self.date,
                'default_amount': self.refund_amount,
            }
        }


    def action_make_paid(self):
        self.write({
            'payment_state': 'paid'
        })
        self.mapped('loan_id').update_state()
        return True

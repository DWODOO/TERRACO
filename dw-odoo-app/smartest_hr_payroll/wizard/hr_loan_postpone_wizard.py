# -*- encoding: utf-8 -*-

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class LoanPostponeWizard(models.TransientModel):
    _name = "hr.loan.postpone.wizard"
    _description = "Loan refund postpone"

    loan_line_id = fields.Many2one(
        'hr.loan.refund.line',
        'Loan line',
        store=True
    )
    date = fields.Date(
        'Date',
        readonly=True,
        required=True,
        store=True
    )
    amount = fields.Float(
        'Amount',
        readonly=True,
        store=True
    )
    new_date = fields.Date(
        'Postpone Date'
    )
    nbr = fields.Integer(
        'Slices',
        Help='Divide the amount into several slices',
        required=True,
        default=1
    )

    @api.constrains('date', 'new_date')
    def check_dates(self):
        if self.filtered(lambda postpone: postpone.new_date < postpone.date):
            raise UserError(
                _('The postpone date must be greater than actual refund date.')
            )


    def action_confirm(self):
        self.ensure_one()
        self.loan_line_id.write({
            'payment_state': 'postponed'
        })

        deduction_date = datetime(self.new_date.year, self.new_date.month, 1)
        day = deduction_date.day
        month = deduction_date.month
        year = deduction_date.year

        cr = self.env.cr
        cr.execute('SELECT MAX(p.sequence) FROM hr_loan_refund_line p WHERE loan_id=%s' % self.loan_line_id.loan_id.id)
        i = cr.fetchone()[0]

        amount = self.amount / self.nbr
        number = self.nbr + 1

        lines = []
        for x in range(1, number):
            i += 1
            lines.append({
                'refund_amount': amount,
                'loan_id': self.loan_line_id.loan_id.id,
                'date': deduction_date.strftime('%Y-%m-%d'),
                'sequence': i,
            })
            deduction_date = (datetime(year, month, day) + relativedelta(months=+1))
            day = deduction_date.day
            month = deduction_date.month
            year = deduction_date.year

        self.env['hr.loan.refund.line'].create(lines)
        return {
            'type': 'ir.actions.act_window_close'
        }

# -*- coding:utf-8 -*-
import datetime

from odoo import fields, models, _, api


class HrEmployeePrintingLog(models.Model):
    _name = 'hr.employee.printing.log'

    name = fields.Char(
        'Number',
        index=True,
        default=lambda self: _('New')
    )
    document = fields.Char(
        'Document'
    )
    date = fields.Datetime(
        'Date',
        default=datetime.datetime.now()
    )
    user_id = fields.Many2one(
        'res.users',
        'User',
        default=lambda self: self.env.user
    )
    state = fields.Selection(
        [
        ('done', 'Done'),
        ('canceled', 'Canceled')
    ],
        default="done"
    )
    cancel_user_id = fields.Many2one(
        'res.users',
        'Cancel User',
    )
    cancel_date = fields.Datetime(
        'Cancellation Date',
    )
    source_employee = fields.Boolean(
        "Source Employee",
        default=False,
    )

    def button_cancel(self):
        self.state = "canceled"
        self.cancel_user_id = self.env.user
        self.cancel_date = datetime.datetime.now()

    @api.model
    def create(self, values):
        if not values.get('source_employee'):
            if not values.get('name') or values.get('name') == 'new':
                sequence = self.env.ref('l10n_dz_hr.sequence_hr_employee_documents')
                values['name'] = sequence.next_by_id()
            values['source_employee'] = False
        return super(HrEmployeePrintingLog, self).create(values)

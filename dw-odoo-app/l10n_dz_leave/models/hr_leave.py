# -*- coding:utf-8 -*-

from odoo import models, api, fields


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    def default_get_remaining_leaves(self):
        default_employee = self.env.context.get('default_employee_id') or self.env.user.employee_id
        default_remaining_days = default_employee.remaining_leaves
        return default_remaining_days

    sequence = fields.Char(
        'Sequence'
    )
    remaining_leaves = fields.Float(
        'Remaining Leaves',
        default=default_get_remaining_leaves
    )
    interim_id = fields.Many2one(
        "hr.employee",
        "Interim"
    )

    @api.onchange('date_from', 'date_to', 'employee_id')
    def _onchange_leave_dates(self):
        if self.date_from and self.date_to:
            self.number_of_days = abs((self.date_to - self.date_from).days) + 1
        else:
            self.number_of_days = 0

    @api.model
    def create(self, values):
        if not values.get('name', False):
            sequence = self.env.ref('l10n_dz_hr.sequence_hr_employee_documents')
            values['sequence'] = sequence.next_by_id()
        return super(HrLeave, self).create(values)

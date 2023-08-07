# -*- coding:utf-8 -*-

from odoo import fields, models


class HrPayrollStructureType(models.Model):
    _inherit = 'hr.payroll.structure.type'

    default_absence_work_entry_type_id = fields.Many2one(
        'hr.work.entry.type',
        "Default Work Entry For Absences",
        help="Work entry type for absences.",
        default=lambda self: self.env.ref('l10n_dz_payroll.hr_absence_work_entry', raise_if_not_found=False)
    )

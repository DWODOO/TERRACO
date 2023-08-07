# -*- coding: utf-8 -*-
# Part of SMARTEST ALGERIA

# Import Odoo libs
from odoo import _, fields, models
from odoo.exceptions import ValidationError

entry_type_list = ['ABS_HOURS', 'ABS_DAYS', 'H75', 'H50', 'ABS_HOURS', 'H100', 'H150']


class SmartestHrWorkEntryType(models.Model):
    _inherit = "hr.work.entry.type"

    smartest_paid_in_addition = fields.Boolean(
        "Paid In Addition",
        copy=True)
    smartest_paid_in_calendar = fields.Boolean(
        "Paid In Calendar",
        copy=True)
    smartest_paid_in_sub = fields.Boolean(
        "Payé en moins",
        copy=True)
    smartest_hourly_paid = fields.Boolean(
        "Hourly Paid",
        copy=True)
    smartest_weekend_days = fields.Boolean(
        "Weekend Days",
        help=_('When checked it means that this work entry is the weekend days'),
        copy=True)

    smartest_get_weekend_days = fields.Boolean(
        "Get Weekend Days",
        help=_('When checked it sets the weekend work entry'),
        copy=True)
    smartest_payslip_irg_type_applied = fields.Selection([
        ('bareme', 'IRG Barème'),
        ('abs', 'IRG Régle de Trois'),
    ], string='IRG Type',
        default='bareme'
    )

    def unlink(self):
        if any(record.code in entry_type_list for record in self):
            raise ValidationError(
                _(
                    "You are not allowed to delete this record. If it doesn't make sens to you, "
                    "please contact your administrator."
                )
            )
        return super(SmartestHrWorkEntryType, self).unlink()

# -*- coding: utf-8 -*-
# Part of SMARTEST ALGERIA

# Import Odoo libs
from odoo import api, fields, models

MONTH_PER_YEAR = 12
WEEK_PER_YEAR = 52
DEFAULT_HOURS_PER_MONTH = 173.33
DEFAULT_DAYS_PER_MONTH = 0
DAYS_PER_WEEK = 7
DAYS_PER_MONTH = 30
WEEKS_PER_MONTH = 4


class SmartestHrContract(models.Model):
    _inherit = 'hr.contract'

    hours_per_month = fields.Float(
        string='Hours/month',
        default=173.33,
        readonly=True,
        states={'draft': [('readonly', False)]},
        tracking=True)
    days_per_month = fields.Integer(
        string='Working days',
        default=22,
        readonly=True,
        states={'draft': [('readonly', False)]})

    pre_wage = fields.Float(
        string='Pre salary',
        tracking=True
    )
    smartest_paid_in_calendar = fields.Boolean(
        "Work entries Paid In Calendar",
        copy=True, tracking=True)
    smartest_work_entry_type_ids = fields.Many2many(
        'hr.work.entry.type',
        string='Work entries Calendar',
        tracking=True
    )
    # ------------------------------------- Payroll rules fields ---------------------------------------------------
    company_currency = fields.Many2one(
        'res.currency',
        string='Currency',
        related='company_id.currency_id',
        readonly=True,
        tracking=True
    )

    allowance_meal_dependencies = fields.Selection(
        [
            ('non_abs_non_leave', 'Ne dépend pas des abs'),
            ('abs_leave', 'Dépend des abs'),
        ],
        'Meal allowance Dependency',
        default='abs_leave',
        tracking=True
    )

    allowance_transportation_dependencies = fields.Selection(
        [
            ('non_abs_non_leave', 'Non(Abs &Leave)'),
            ('abs_leave', 'Abs & Leave'),
        ],
        'Transportation allowance Dependency',
        default='abs_leave',
        tracking=True
    )
    allowance_in_iep_in_addition = fields.Float(
        'P.E.A (In company In Addition)',
        help='Professional Experience Allowance in the company in addition',
        tracking=True
    )

    @api.onchange('resource_calendar_id')
    def _on_calendar_change(self):
        calendar = self.resource_calendar_id
        if calendar.hours_per_day:
            days_per_week = len(list(dict.fromkeys(calendar.mapped('attendance_ids.dayofweek'))))
            days_off_per_week = DAYS_PER_WEEK - days_per_week
            self.hours_per_month = (calendar.hours_per_day * days_per_week * WEEK_PER_YEAR) / MONTH_PER_YEAR
            self.days_per_month = DAYS_PER_MONTH - WEEKS_PER_MONTH * days_off_per_week

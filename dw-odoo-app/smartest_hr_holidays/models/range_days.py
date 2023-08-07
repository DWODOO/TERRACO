# -*- coding:utf-8 -*-
from odoo import models,fields,api,_
from odoo.exceptions import ValidationError

from datetime import date,datetime


class RangeDays(models.Model):
    _name = 'range.days'
    _description = "Range days for holidays"

    smartest_days_worked = fields.Integer(
        required=True,
        string="Worked days"
    )
    smartest_number_of_days_allocated = fields.Float(
        required=True,
        string="Number of days to be allocated"
    )
    smartest_area = fields.Selection([
        ('north','North'),
        ('south', 'South'),
    ], string="Area",default="north",required=True)

    @api.constrains('smartest_days_worked')
    def important_constrains(self):
        date_planified_action = self.env.ref('hr_holidays.hr_leave_allocation_cron_accrual').nextcall
        year_month = date_planified_action.strftime('%Y-%m')
        date_string = str(year_month) +'-1'
        start = datetime.strptime(date_string, '%Y-%m-%d').date()
        off = (date_planified_action.date() - start).days +1

        for record in self:
            if record.smartest_days_worked < 1:
                raise ValidationError(
                    _('Min number of days worked must be greater than 0 .'))
            if record.smartest_days_worked > off:
                raise ValidationError(
                _('Max number of days worked must be less than %s ,To rectify this! it is necessary to change the date located in planned action')% off)


    @api.model
    def create(self, vals):
        worked_days= int(list(vals.values())[1])
        area = list(vals.values())[0]
        range = self.env['range.days'].search([('smartest_days_worked','=',worked_days),('smartest_area','=',area)])
        res = super(RangeDays, self).create(vals)
        if range:
            raise ValidationError(
                _('These values are already created.'))
        else:
            return res
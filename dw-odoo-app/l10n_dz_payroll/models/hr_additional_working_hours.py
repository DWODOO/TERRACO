# -*- encoding: utf-8 -*-
import time, calendar
from datetime import datetime

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError


class HrAdditionalWorkingHours(models.Model):
    _name = "hr.additional.working.hours"
    _description = "Employee additional working Hours"
    _order = 'date_from'
    _inherit = ['mail.thread']

    name = fields.Char(
        'Name',
        readonly=True,
        store=True,
        default='/'
    )
    limit = fields.Float(
        'Additional working hours limit',
        default=32,
        readonly=True,
        states={'draft': [('readonly', False)]},
        store=True
    )
    department_id = fields.Many2one(
        'hr.department',
        'Department',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    date_from = fields.Date(
        string='From',
        required=True,
        store=True,
        default=fields.Date.today,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    date_to = fields.Date(
        string='To',
        required=True,
        store=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('cancelled', 'Canceled')
        ],
        'State',
        default='draft'
    )
    additional_hours_line_ids = fields.One2many(
        'hr.additional.working.hours.line',
        'additional_hours_id',
        string='Additional hours Lines',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    company_id = fields.Many2one(
        'res.company',
        'Company',
        required=True,
        index=True,
        default=lambda self: self.env.user.company_id,
        readonly=True
    )

    @api.onchange('date_from')
    def on_change_date_from(self):
        if self.date_from:
            self.date_to = self.date_from.replace(
                day=calendar.monthrange(self.date_from.year, self.date_from.month)[1],
                month=self.date_from.month
            )


    def action_confirm(self):
        self.write({
            'state': 'confirmed'
        })
        return True


    def action_draft(self):
        self.write({
            'state': 'draft'
        })
        return True


    def action_cancel(self):
        self.write({
            'state': 'cancelled'
        })
        return True

    @api.model
    def create(self, vals):
        if vals.get('name', _('/')) == _('/'):
            date = datetime.fromtimestamp(time.mktime(time.strptime(vals['date_from'], "%Y-%m-%d")))
            vals['name'] = tools.ustr(date.strftime('%B-%Y')).upper()
        if not vals.get('company_id', False):
            vals['company_id'] = self.env.user.company_id.id
        return super(HrAdditionalWorkingHours, self).create(vals)


    def unlink(self):
        if 'confirmed' in self.mapped('state'):
            raise ValidationError(
                _('Confirmed additional working hours can not be deleted')
            )
        return super(HrAdditionalWorkingHours, self).unlink()


class HrAdditionalWorkingHoursLine(models.Model):
    _name = 'hr.additional.working.hours.line'
    _description = 'Additional Working Hours Lines'
    _order = 'employee_id'

    additional_hours_id = fields.Many2one(
        'hr.additional.working.hours',
        string='Additional hours',
        required=True,
        ondelete='cascade'
    )
    employee_id = fields.Many2one(
        'hr.employee',
        required=True,
        string='Employee',
        index=True
    )
    company_id = fields.Many2one(
        'res.company',
        'Company',
        required=True,
        index=True,
        store=True,
        related="additional_hours_id.company_id",
        readonly=True
    )
    total = fields.Float(
        string='Total Hours',
        compute='_compute_total',
        store=True
    )
    h50 = fields.Float(
        string='H50%'
    )
    h75 = fields.Float(
        string='H75%'
    )
    h100 = fields.Float(
        string='H100%'
    )
    date_from = fields.Date(
        related='additional_hours_id.date_from',
        store=True,
        index=True
    )
    date_to = fields.Date(
        related='additional_hours_id.date_to',
        store=True, index=True
    )
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('cancelled', 'Canceled')
        ],
        'State',
        related='additional_hours_id.state',
        store=True,
        index=True
    )

    @api.depends('h50', 'h75', 'h100')
    def _compute_total(self):
        for line in self:
            total = line.h50 + line.h75 + line.h100
            if total > line.additional_hours_id.limit:
                raise UserError(
                    _("You can not have total hours great than %s.\nTotal hours: %s") % (
                        line.additional_hours_id.limit,
                        total
                    )
                )
            line.total = total

    @api.model
    def create(self, vals):
        if not vals.get('company_id', False):
            vals['company_id'] = self.env.user.company_id.id
        return super(HrAdditionalWorkingHoursLine, self).create(vals)

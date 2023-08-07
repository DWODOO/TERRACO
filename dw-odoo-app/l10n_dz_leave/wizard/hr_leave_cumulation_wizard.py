# -*- coding:utf-8 -*-
import pdb
from datetime import datetime

from odoo import fields, models, api, _


class LeaveCumulationWizard(models.TransientModel):
    _name = 'hr.leave.cumulation.wizard'

    @api.model
    def get_year_references(self):
        year = datetime.today().year
        year -= 30
        return [(str(year + i), str(year + i)) for i in range(300)]

    date_from = fields.Date(
        string='From',
        required=True,
        default=fields.Date.today().replace(day=1, month=7, year=fields.Date.today().year-1),
    )
    date_to = fields.Date(
        string='To',
        required=True,
    )
    leave_type_id = fields.Many2one(
        'hr.leave.type',
        'Leave type',
        store=True,
        compute='_compute_leave_type',
    )
    company_id = fields.Many2one(
        'res.company',
        'Company',
        required=True,
        index=True,
        default=lambda self: self.env.user.company_id,
        readonly=True
    )
    employee_ids = fields.Many2many(
        'hr.employee',
        string='Employees'
    )
    payslip_ids = fields.Many2many(
        'hr.payslip',
        string='Payslips',
        domain="[('is_leave_cumulated', '=', False), ('state', '=', 'done')]"
    )
    year_reference = fields.Selection(
        selection='get_year_references',
        default=str(datetime.today().year-1)
    )

    @api.onchange('year_reference')
    def onchange_year_reference(self):
        self.date_from = self.date_from.replace(year=int(self.year_reference))

    @api.model
    def _select_payslips(self, date_from, date_to, employee_ids=None):
        domain = [
            ('date_from', '>=', date_from),
            ('date_to', '<=', date_to),
            ('state', '=', 'done'),
            ('is_leave_cumulated', '=', False)
        ]
        if employee_ids:
            domain.append(
                ('employee_id', 'in', employee_ids.ids)
            )
        return self.env['hr.payslip'].search(domain)

    @api.onchange('date_from', 'date_to', 'employee_ids')
    def update_payslips(self):
        if self.date_from and self.date_to:
            self.payslip_ids = False
            self.payslip_ids = [
                (4, payslip.id)
                for payslip in self._select_payslips(
                    self.date_from,
                    self.date_to,
                    self.employee_ids
                )
            ]

    @api.onchange('date_from')
    def on_change_date_from(self):
        if self.date_from:
            self.date_to = self.date_from.replace(
                day=30,
                month=6,
                year=self.date_from.year+1
            )

    @api.depends('date_from', 'date_to')
    def _compute_leave_type(self):
        if self.date_from and self.date_to:
            domain = [
                # False,
                # False,
                ('leave_situation', '=', 'annual_leave'),
                ('unpaid', '=', False),
                ('time_type', '=', 'leave'),
                ('request_unit', '=', 'day'),
            ]
            leave_type_obj = self.env['hr.leave.type']
            for cumulation in self:
                # domain[0] = ('date_from', '<=', cumulation.date_from.replace(year=cumulation.date_from.year+1))
                # domain[1] = ('date_to', '>=', cumulation.date_to.replace(year=cumulation.date_to.year+1))
                leave_type_id = leave_type_obj.search(
                    domain,
                    limit=1,
                    order="id"
                )
                if not leave_type_id:
                    leave_type_id = leave_type_obj.create({
                        'name': _('Annual Leave %s') % (cumulation.date_from.year + 1),
                        'allocation_type': 'accrual',
                        # 'date_from': cumulation.date_to.replace(month=7, day=1),
                        'requires_allocation': "yes",
                        'leave_situation': 'annual_leave'
                    })
                cumulation.leave_type_id = leave_type_id

    def action_cumulation(self):
        self.ensure_one()
        payslips = self.payslip_ids.filtered(lambda p: p.state == 'done')
        allocation_obj = self.env['hr.leave.allocation']
        allocations = []
        for employee in self.mapped('payslip_ids.employee_id'):
            employee_payslips = payslips.filtered(lambda p: p.employee_id == employee)
            leaves = sum(employee_payslips.mapped('leave_days_count'))
            allowance = sum(employee_payslips.mapped('leave_allowance'))
            if leaves > 0:
                allocations.append({
                    "employee_id": employee.id,
                    "holiday_status_id": self.leave_type_id.id,
                    "holiday_type": "employee",
                    "name": _("Leaves cumulation of the period: %s - %s") % (self.date_from, self.date_to),
                    "state": "draft",
                    "number_of_days": leaves,
                    "leave_allowance": allowance,
                    "year_reference": int(self.year_reference),
                })

        if allocations:
            context = dict(self._context or {})
            allocation_ids = allocation_obj.with_context(
                context,
                pass_holiday_status_constraint=True
            ).create(allocations)
            allocation_ids.sudo().action_confirm()
            allocation_ids.sudo().filtered(lambda alloc: alloc.state == 'confirm').action_approve()
            allocation_ids.sudo().filtered(lambda alloc: alloc.state == 'validate1').action_validate()
        payslips.write({
            'is_leave_cumulated': True
        })
        return True

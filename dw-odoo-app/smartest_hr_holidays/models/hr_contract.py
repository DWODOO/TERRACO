# -*- coding:utf-8 -*-
from odoo import models, fields, api, _



class HrContract(models.Model):
    _inherit = 'hr.contract'

    @api.model
    def create(self, vals):
        contract = super(HrContract, self).create(vals)
        if contract.state == 'open':
            values = contract._prepare_allocation_values()
            allocations = self.env['hr.leave.allocation'].create(values)
            allocations.action_validate()
        return contract

    def write(self, values):
        if values.get('state') == 'open':
            vals_list = []
            for contract in self.filtered(lambda c: c.state == 'draft'):
                vals_list += contract._prepare_allocation_values()
            if vals_list:
                allocation = self.env['hr.leave.allocation'].create(vals_list)
                allocation.action_validate()
        return super(HrContract, self).write(values)

    def _prepare_allocation_values(self):
        self.ensure_one()
        date_from = self.date_start or fields.Date.today()
        allocation = self.env['hr.leave.allocation']._get_employee_allocation(self.employee_id, date_from)

        if not allocation:
            return []

        allocation_values = allocation._prepare_holiday_values(self.employee_id)
        #
        # if len(allocation_values):
        #     allocation[0]['date_from'] = date_from

        return allocation_values

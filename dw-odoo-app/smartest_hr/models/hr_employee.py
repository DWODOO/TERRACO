# -*- coding:utf-8 -*-
import pdb

from odoo import api, fields, models, _


class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    last_name = fields.Char(
        'Last name',
    )
    first_name = fields.Char(
        'First name',
    )
    name = fields.Char(
        'Complete Name',
    )


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    last_name = fields.Char(
        'Last name',
    )
    first_name = fields.Char(
        'First name',
    )
    name = fields.Char(
        'Complete Name',
    )

    @api.model
    def create(self, values):
        if not values.get('name'):
            values['name'] = '%s %s' % (values.get('first_name') or '', values.get('last_name') or '')
        return super(HrEmployee, self).create(values)

    def write(self, values):
        if values.get('first_name', False) or values.get('last_name', False):
            for employee in self:
                values['name'] = '%s %s' % (
                    values.get('first_name', False) or employee.first_name or '',
                    values.get('last_name', False) or employee.last_name or '',
                )
                super(HrEmployee, employee).write(values)
        else:
            super(HrEmployee, self).write(values)

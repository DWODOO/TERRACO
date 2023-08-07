# -*- coding: utf-8 -*-

# Import Odoo libs
from odoo import fields, models


class SmartestHrEmployeePublic(models.AbstractModel):
    _inherit = 'hr.employee.base'

    objective_ids = fields.Many2many(
        'hr.appraisal.objective',
        'objective_employee_rel',
        'employee_id',
        'objective_id',
    )
    appraisal_validator_id = fields.Many2one(
        'hr.employee',
        'Appraisal Validator'
    )


class SmartestHrEmployee(models.Model):
    _inherit = 'hr.employee'

    objective_ids = fields.Many2many(
        'hr.appraisal.objective',
        'objective_employee_rel',
        'employee_id',
        'objective_id',
    )
    appraisal_validator_id = fields.Many2one(
        'hr.employee',
        'Appraisal Validator'
    )

    def _read(self, fields):
        try:
            return super(SmartestHrEmployee, self)._read(fields)
        except Exception as e:
            context = self.env.context
            if context.get('smartest_bypass'):
                return super(SmartestHrEmployee, self.sudo())._read(fields)
            raise e

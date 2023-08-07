# -*- coding: utf-8 -*-

# Import Odoo libs
from odoo import api, fields, models


class SmartestProjectAttendance(models.Model):
    _name = 'project.attendance'
    _description = 'Project Attendance'

    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string="Employee"
    )
    working_days = fields.Integer(
        string='Working Days'
    )
    from_date = fields.Date(
        string='Debut Date'
    )
    to_date = fields.Date(
        string='End Date'
    )
    sick_days = fields.Integer(
        string='Sick Days'
    )
    vacation_days = fields.Integer(
        string='Vacation Days'
    )
    training_days = fields.Integer(
        string='Training'
    )
    recovery_days = fields.Integer(
        string='Recovery'
    )
    holiday = fields.Integer(
        string='holidays'
    )
    aviability = fields.Integer(
        string='Aviability',
        compute="_compute_aviability",
        store=True
    )
    aviability_percentage = fields.Float(
        string='Aviability percentage'
    )

    @api.depends('working_days', 'sick_days', 'vacation_days', 'training_days', 'recovery_days', 'holiday')
    def _compute_aviability(self):
        for employee in self:
            if employee.working_days:
                employee.aviability = employee.working_days - (
                        employee.sick_days + employee.vacation_days + employee.training_days + employee.recovery_days + employee.holiday)
                employee.aviability_percentage = employee.aviability / employee.working_days * 100

    def name_get(self):
        result = []
        for rec in self:
            name = rec.employee_id.name
            if rec.to_date:
                name = '#%s: %s' % (rec.to_date, name)
            result.append((rec.id, name))
        return result

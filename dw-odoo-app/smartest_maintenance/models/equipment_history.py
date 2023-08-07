# -*- coding: utf-8 -*-

# Import Odoo libs
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SmartestEquipment(models.Model):
    _name = "maintenance.equipment.history"
    _description = "Equipment History"
    _order = "id desc"

    old_employee_id = fields.Many2one(
        'hr.employee',
        'From'
    )
    new_employee_id = fields.Many2one(
        'hr.employee',
        'To'
    )
    new_department_id = fields.Many2one(
        'hr.department',
        'To'
    )
    old_department_id = fields.Many2one(
        'hr.department',
        'From'
    )
    date_assignment = fields.Date(
        string="Assignment Date",
        help="Date when the equipment was assigned to the new employee.",
        default=fields.Date.context_today,
        # track_visibility="onchange",
    )
    equipment_id = fields.Many2one(
        'maintenance.equipment',
        'Equipment',
        # track_visibility="onchange",
        required=True,
    )

    assign_equipment_to = fields.Selection(
        [('department', 'Department'), ('employee', 'Employee'), ('other', 'Other')],
        string='Used By',
        required=True,
        default='employee')

    def button_equipment_assign(self):
        date = self._context.get('default_date_assignment')
        if date:
            if self.assign_equipment_to == 'employee':
                self.equipment_id.write({
                    "equipment_assign_to": "employee",
                    "employee_id": self.new_employee_id.id,
                    "assign_date": self.date_assignment
                })
            if self.assign_equipment_to == 'department':
                self.equipment_id.write({
                    "equipment_assign_to": "department",
                    "department_id": self.new_department_id.id,
                    "assign_date": self.date_assignment
                })

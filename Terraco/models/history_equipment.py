
from odoo import _, api, fields, models

class SmartestHistoryEquipment(models.Model):

    _name= 'history.equipment'

    sequence = fields.Integer()
    equipment_id = fields.Many2one(
        'maintenance.equipment',
    )
    employee_id = fields.Many2one(
        'hr.employee',
    )
    department_id = fields.Many2one(
        'hr.department',
    )
    lieux = fields.Char(
    )

    date_return = fields.Date(
    )
    motif= fields.Char(
    )
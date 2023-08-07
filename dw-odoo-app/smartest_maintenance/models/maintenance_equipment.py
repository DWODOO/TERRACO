# -*- coding: utf-8 -*-

# Import Odoo libs
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SmartestEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    history_ids = fields.One2many('maintenance.equipment.history','equipment_id','History of assignation')
    first_maintenance_request = fields.Date(string="First Maintenance Date", compute="compute_first_maintenance_date")


    def compute_first_maintenance_date(self):
        for equipement in self:
            first_maintenance_request = self.env['maintenance.request'].search([('equipment_id','=',equipement.id)], order='request_date desc',limit=1)
            equipement.first_maintenance_request = False if not first_maintenance_request else first_maintenance_request[0].request_date

    def button_assign(self):
        ''' Create new assignation of equipment'''

        return {
            'name': _('New Equipment Assignation'),
            'res_model': 'maintenance.equipment.history',
            'view_mode': 'form',
            'context': {
                'form_view_initial_mode': 'edit',
                'default_date_assignment': fields.date.today(),
                'default_equipment_id': self.id,
                'default_old_employee_id': self.employee_id.id,
                'default_old_department_id': self.department_id.id,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
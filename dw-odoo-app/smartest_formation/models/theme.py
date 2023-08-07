# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SmartestFormationCourse(models.Model):
    _name = 'theme'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Theme General'
    
    
    smartest_company_id = fields.Many2one('res.company', string='Company', required=True, index=True, default=lambda self: self.env.company)
    smartest_course_id = fields.Char(string="Course ID",readonly=True,index=True)
    smartest_name = fields.Char("Theme")
    smartest_institute_ids = fields.Many2many("res.partner",string="Institute",domain=[('smartest_is_institute','=',True)])
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    #smartest_department_ids = fields.One2many('hr.department','smartest_formation',string='Department',required=True)
    smartest_course_details = fields.One2many('formation.details','smartest_formation')



    @api.model
    def create(self, values):
        if values.get('smartest_course_id',_('New') == _('New')) :
                values['smartest_course_id'] = self.env['ir.sequence'].next_by_code('smartest.formation.seq') or _('New')
        result = super(SmartestFormationCourse, self).create(values)
        return result

    def name_get(self):
        return [(record.id,record.smartest_name) for record in self]


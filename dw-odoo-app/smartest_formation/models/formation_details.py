# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, timedelta 
from odoo.exceptions import ValidationError


class SmartestFormationDetails(models.Model):
    _name = 'formation.details'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Formation Details'

    
    smartest_course_id = fields.Char(string="Formation ID",readonly=True,index=True)
    today = datetime.now().strftime("%Y-%m-%d")
    smartest_name = fields.Char("Formation", required="1")
    smartest_duration = fields.Integer('Durée Total(h)')
    smartest_trainer = fields.Char("Formateur")
    smartest_course_price = fields.Float(string='Prix de Formation')
    smartest_agrement_course = fields.Boolean("Formation Agréées",default=False)
    smartest_institute_id = fields.Many2one("res.partner",string="Institute",domain=[('smartest_is_institute','=',True)], required="1")
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    smartest_formation = fields.Many2one('theme',string='Theme', required="1")
    smartest_company_id = fields.Many2one('res.company', required=True, index=True, default=lambda self: self.env.company)


    def name_get(self):
        return [(record.id,record.smartest_name) for record in self]

    @api.constrains('smartest_course_price')
    def _formation_price(self):
        for rec in self:
            if rec.smartest_course_price == 0:
                raise ValidationError(_('Price must be bigger than 0.'))







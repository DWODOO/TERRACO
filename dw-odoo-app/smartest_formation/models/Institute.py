# -*- coding: utf-8 -*-

from odoo import models, fields


class SmartestFormationInstitute(models.Model):
    _inherit = 'res.partner'
    _description = 'Institute'
    
    
    
    smartest_is_institute = fields.Boolean('Is Institute')
    smartest_is_licensed = fields.Boolean('Is licensed')
    smartest_theme = fields.Many2many('theme',readonly=True)


    # def is_supplier(self):
    #     self.is_supplier = True



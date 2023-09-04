
from odoo import _, api, fields, models

class SmartestEtatEquipment(models.Model):
    _name= 'etat.equipment'

    name = fields.Char()
    sequence = fields.Integer()
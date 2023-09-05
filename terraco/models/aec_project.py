
from odoo import _, api, fields, models

class AecProject(models.Model):

    _name= 'aec.project'

    name = fields.Char()

# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SmartestResGroups(models.Model):
    _inherit = 'res.groups'

    smartest_parent_group = fields.Many2one('res.groups')

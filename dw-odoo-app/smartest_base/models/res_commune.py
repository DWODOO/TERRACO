# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ResCommune(models.Model):
    _name = 'res.commune'
    _description = 'Commune'
    _order = 'name,id'

    code = fields.Char(
        string='Code Commune', size=2,
        help=u'Le code de la commune sur deux positions',
        required=True
    )
    state_id = fields.Many2one(
        'res.country.state',
        string='Wilaya',
        required=True
    )
    name = fields.Char(
        string='Commune',
        required=True,
        translate=True
    )


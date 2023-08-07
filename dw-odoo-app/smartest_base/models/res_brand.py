# -*- coding: utf-8 -*-
import base64
import os

from odoo import models, tools, fields, api, _
from odoo.exceptions import UserError


class SmartestSabieResBrand(models.Model):
    _name = "res.brand"
    _description = 'Brand'
    _order = 'sequence, name'

    def copy(self, default=None):
        raise UserError(_('Duplicating a company is not allowed. Please create a new company instead.'))

    def _get_logo(self):
        return base64.b64encode(
            open(os.path.join(
                tools.config['root_path'], 'addons', 'base', 'static', 'img', 'res_company_logo.png'),
                'rb'
            ).read()
        )

    name = fields.Char(
        string='Brand Name',
        related='partner_id.name',
        required=True,
        store=True,
        readonly=False
    )
    sequence = fields.Integer(
        string="Sequence",
        help='Used to order Brands in the company switcher',
        default=10
    )
    logo = fields.Binary(
        related='partner_id.image_1920',
        default=_get_logo,
        string="Company Logo",
        readonly=False
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        required=True
    )

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The brand name must be unique !'),
    ]

    @api.model
    def create(self, vals):
        if not vals.get('name') or vals.get('partner_id'):
            self.clear_caches()
            return super(SmartestSabieResBrand, self).create(vals)
        partner = self.env['res.partner'].create({
            'name': vals['name'],
            'is_company': True,
            'image_1920': vals.get('logo')
        })
        vals['partner_id'] = partner.id
        self.clear_caches()
        brand = super(SmartestSabieResBrand, self).create(vals)
        return brand

# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SmartestProductProduct(models.Model):
    _inherit = 'product.product'


    invisible_on_sale = fields.Boolean(default=False)
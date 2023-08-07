# -*- coding:utf-8 -*-

from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = 'purchase.product.request'

    origin = fields.Char('Source Document', copy=False,
                         help="Reference of the document that generated this purchase rquest "
                              "request (e.g. a mrp production)")

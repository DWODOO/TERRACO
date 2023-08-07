# -*- coding:utf-8 -*-

from odoo import fields, models


class MaintenanceRequest(models.Model):
    _inherit = "maintenance.request"
    _check_company_auto = True

    production_id = fields.Many2one(
        'mrp.production', string='Manufacturing Order', check_company=True)

    production_company_id = fields.Many2one(string='Production Company', related='production_id.company_id')
    company_id = fields.Many2one(domain="[('id', '=?', production_company_id)]")

# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta

from odoo import models, fields, api, _, exceptions
from odoo.exceptions import ValidationError, UserError


class ImportFile(models.Model):
    _inherit = 'comex.import.file'


    import_folder_id = fields.Many2one('purchase.import.folder', string="Folder")

    def action_view_import_folder(self):
        action = self.env['ir.actions.actions']._for_xml_id('smartest_stock_landed_costs.action_purchase_import_folder')
        action['domain'] = [('id','in',self.import_folder_id.id)]
        return action


class ImportFileOpeningRequest(models.Model):
    _inherit = 'comex.opening.request'


    import_folder_id = fields.Many2one('purchase.import.folder', string="Folder")
    comex_import_file_ids = fields.One2many('comex.import.file', 'opening_request_id', string="Comex Import File(s)")



    def create_comex_import_file(self):
        file_ids = []
        for request in self:
            import_file = self.comex_import_file_ids.create({
                'import_file_type': request.import_file_type,
                'import_folder_id': request.import_folder_id.id,
                'product_type_id': request.product_type.id,
                'supplier_id': request.proforma_bill_id.partner_id.id,
                'subsidiary_id': self.env.company.id,
                'opening_request_id': request.id,
                'proforma_bill': request.proforma_bill_id.name,
                'currency_id': request.proforma_bill_id.currency_id.id,
                'proforma_amount_total': request.proforma_bill_id.amount_total,
                'fiscal_year_use': str(request.date.year),
            })
            file_ids.append(import_file.id)
        action = self.env['ir.actions.actions']._for_xml_id(
                'foreign_trade.all_import_file_pdr_no_create')
        action['domain'] = [('id', 'in', file_ids)]
        return action


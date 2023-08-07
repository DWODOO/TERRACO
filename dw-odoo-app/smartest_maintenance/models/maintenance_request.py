# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, timedelta


class SmartestMaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    repair_id = fields.Many2one('repair.order', string="Ordre de Reparation")
    preventive_id = fields.Many2one('maintenance.preventive.dates',string="Preventive Date")
    stage_id_done = fields.Boolean(related="stage_id.done")
    is_replacement = fields.Boolean('Remplacement')
    is_diagnostic = fields.Boolean('Diagnostique')
    is_amelioration = fields.Boolean('Amelioration')
    is_control = fields.Boolean('Controle')
    normale_defaillance = fields.Boolean('Usure Normale')
    user_defaillance = fields.Boolean('Usure Utilisateur')
    product_defaillance = fields.Boolean('Defaut Produit')
    autre = fields.Boolean('Autres')
    is_mecanique = fields.Boolean('Mecanique')
    is_electric = fields.Boolean('Electrique')
    is_instrumentation = fields.Boolean('Instrumentation')
    is_automatisme = fields.Boolean('Automatisme')

    def prepare_repair_order_vals(self):
        for this in self:
             vals={
                'repair_equipement':True,
                'location_id':self.env['stock.location'].search([('usage','=','internal')],limit=1).id,
                'equipement_id':this.equipment_id.id,
                'maintenance_request_id':this.id,
             }
        return vals

    def prepare_repair_order_lines_vals(self):
        for this in self:
             repair_pdr_lines = []
             repair_operation_lines = []
             pdr_lines = this.preventive_id.pdr_line_ids
             operation_lines = this.preventive_id.operation_line_ids
             for line in pdr_lines:
                 repair_line ={
                     'product_id':line.product_id.id,
                     'name':line.product_id.name,
                     'repair_id':this.repair_id.id,
                     'product_uom_qty':line.product_qty,
                     'product_uom':line.product_uom.id,
                     'price_unit':line.product_id.standard_price,
                     'location_id':line.location_id.id,
                     'location_dest_id':self.env.ref('stock.stock_location_locations_partner').id,
                 }
                 repair_pdr_lines.append(repair_line)

             for line in operation_lines:
                 repair_line ={
                     'product_id':line.product_id.id,
                     'product_uom':line.product_uom.id,
                     'repair_id':this.repair_id.id,
                     'name':line.operation_name if line.operation_name else line.product_id.name,
                     'product_uom_qty':1,
                     'price_unit':line.product_id.standard_price,
                 }
                 repair_operation_lines.append(repair_line)

        return repair_pdr_lines,repair_operation_lines

    def proceed_reparation(self):
        # create repair order and change state
        for this in self:
            if not this.repair_id:
                vals  = this.prepare_repair_order_vals()
                this.repair_id = self.env['repair.order'].create(vals)
                repair_pdr_lines,repair_operation_lines  = this.prepare_repair_order_lines_vals()
                this.repair_id.operations.create(repair_pdr_lines)
                this.repair_id.fees_lines.create(repair_operation_lines)
                this.stage_id = self.env['maintenance.stage'].search([('sequence','=',this.stage_id.sequence+1)])
            return this.open_repair_order()

    def open_repair_order(self):
        for maintenance in self:
            view = {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'views': [(self.env.ref('repair.view_repair_order_form').id, 'form')],
                'name': _('Repair Order'),
                'res_model': 'repair.order',
                'res_id': maintenance.repair_id.id,
            }
            return view

    def open_preventive_dates(self):
        for maintenance in self:
            preventive_view = {
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,form',
                'name': _('Preventive'),
                'res_model': 'maintenance.preventive.dates',
                "domain": [["id", "=", maintenance.preventive_id.id]],
                'res_id': maintenance.preventive_id.id,
            }
            return preventive_view

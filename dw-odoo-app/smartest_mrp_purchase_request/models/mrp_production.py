# -*- coding:utf-8 -*-

from odoo import _, api,fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def _prepare_request_values(self):
        self.ensure_one()
        not_available_move_raw_ids = self.move_raw_ids.filtered(lambda raw_id: raw_id.forecast_availability < raw_id.product_uom_qty)
        line_ids = []
        for line in not_available_move_raw_ids:
            line_ids.append((0, 0, {
                'product_id': line.product_id.id,
                'name': line.product_id.name,
                'product_uom_id': line.product_id.uom_id.id,
                'product_qty': line.product_uom_qty - line.reserved_availability - line.should_consume_qty,
            }))
        return line_ids

    def action_create_purchase_request(self):
        ''' Create the Purchase Request associated to the Fabrication'''
        return {
            'name': _('Créer Demande de Besoin'),
            'res_model': 'purchase.product.request',
            'view_mode': 'form',
            'context': {
                'active_model': 'mrp.production',
                'active_ids': self.ids,
                'form_view_initial_mode': 'edit',
                'default_date_start': fields.Date.today(),
                'default_request_by': self.user_id.id,
                'default_line_ids': self._prepare_request_values(),
                'default_origin':  self.name
            },
            'target': 'current',
            'type': 'ir.actions.act_window',
        }

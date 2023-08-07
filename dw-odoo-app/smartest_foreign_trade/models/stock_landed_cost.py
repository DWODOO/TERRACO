from odoo import _, api, fields, models


class SmartestStockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    purchase_folder_import_id = fields.Many2one('smartest.import.folder', string="Import Folder")

    purchase_order_ids = fields.Many2many(
        'purchase.order',
        string='Orders',
        copy=False,
        store=True,
        states={'done': [('readonly', True)]})
    purchase_order_picking_ids = fields.Many2many('stock.picking', 'purchase_picking_rel',
                                                  column1="purchase_order_id",
                                                  column2="picking_ids",
                                                  compute="compute_purchase_order_ids_picking_ids", store=True)

    # @api.onchange('purchase_folder_import_id')
    # def _onchange_on_purchase_folder_import_id(self):
    #     if self.purchase_folder_import_id:
    #         self.purchase_order_ids = False

    @api.depends('purchase_order_ids')
    def compute_purchase_order_ids_picking_ids(self):
        for record in self:
            purchase_picking_ids = []
            record.write({'purchase_order_picking_ids': False})
            purchase_order_ids = record.purchase_order_ids
            for purchase_order in purchase_order_ids:
                for picking in purchase_order.picking_ids:
                    purchase_picking_ids.append(picking.id)
            record.write({'purchase_order_picking_ids': [(4, picking) for picking in purchase_picking_ids]})


class SmartestStockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'

    @api.model
    def action_landed_costs_valorisation_analysis(self):
        landed_valuation_domain = []
        purchase_folder_import_id = self.env.context.get('active_ids')

        if purchase_folder_import_id:
            purchase_folder_import_id = self.env["smartest.import.folder"].browse(purchase_folder_import_id[-1])
            landed_valuation_domain = [('cost_id.purchase_folder_import_id', '=', purchase_folder_import_id.id)]

        return {
            'name': _("Valorisation Analysis"),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.valuation.adjustment.lines',
            'view_mode': 'tree,form',
            'search_view_id': self.env.ref(
                'smartest_foreign_trade.view_stock_valuation_adjustment_lines_tree').id,
            'domain': landed_valuation_domain,
        }
from odoo import _, api, fields, models


class SmartestPurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    purchase_folder_import_id = fields.Many2one('smartest.import.folder', string="Import Folder")

    @api.model
    def action_purchase_order_analysis(self):
        domain = []
        purchase_folder_import_id = self.env.context.get('active_ids')
        if purchase_folder_import_id:
            domain = [('purchase_folder_import_id', 'in', self.env.context.get('active_ids', []))]
            purchase_folder_import_id = self.env["smartest.import.folder"].browse(purchase_folder_import_id[-1])
        return {
            'name': _('Purchase Order Analysis'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'tree,form',
            'search_view_id': self.env.ref(
                'purchase.view_purchase_order_filter').id,
            'domain': domain,
            'context': {
                'default_purchase_folder_import_id': purchase_folder_import_id.id
            }
        }

    def _prepare_invoice(self):
        """override the _prepare_invoice super method to add the import folder chosen  to the dict .
        """
        self.ensure_one()
        invoice_vals = super(SmartestPurchaseOrder, self)._prepare_invoice()
        if self.purchase_folder_import_id:
            invoice_vals["purchase_folder_import_id"] = self.purchase_folder_import_id.id
            invoice_vals["smartest_purchase_id"] = self.id
        return invoice_vals

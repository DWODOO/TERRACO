from odoo import fields, models, api


class SmartestPurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    purchase_folder_import_id = fields.Many2one('purchase.import.folder', string="Import Folder",
                                                domain=[('state', '=', 'ongoing')])
    opening_request_count = fields.Integer(compute="compute_import_opening_request")

    def compute_import_opening_request(self):
        opening_requests = self.env['comex.opening.request'].search([('proforma_bill_id', '=', self.id)])
        if opening_requests:
            self.opening_request_count = len(opening_requests.ids)
        else:
            self.opening_request_count = 0

    def compute_opening_request_vals(self):
        vals = []
        for line in self.order_line:
            product_type_in_vals = [this.get('product_type') for this in vals if 'product_type' in vals]
            if line.product_id.import_product_type_id.id not in product_type_in_vals:
                val = {
                    'import_folder_id': self.purchase_folder_import_id.id,
                    'proforma_bill_id': self.id,
                    'date': self.date_planned,
                    'product_type': line.product_id.import_product_type_id.id,
                }
                vals.append(val)
        return vals

    def compute_comex_opening_request_activity_vals(self, opening_request_ids):
        opening_request_vals = []
        for opening in opening_request_ids:
            val = {
                'summary': 'create Import File',
                'activity_type_id': 4,
                'date_deadline': self.date_planned,
                'user_id': self.env.uid,
                'res_model_id': self.env['ir.model'].search([('model', '=', 'comex.opening.request')]).id,
                'res_id': opening,
            }
            opening_request_vals.append(val)
        return opening_request_vals

    def create_import_file(self):
        comex_opening_request = self.env['comex.opening.request']
        comex_opening_request_activity = self.env['mail.activity']
        vals = self.compute_opening_request_vals()
        opening_request_ids = comex_opening_request.create(vals)
        comex_opening_request_activity_vals = self.compute_comex_opening_request_activity_vals(opening_request_ids.ids)
        comex_opening_request_activity.create(comex_opening_request_activity_vals)
        action = self.env['ir.actions.actions']._for_xml_id('foreign_trade.opening_request_action_form')
        action['domain'] = [('id', 'in', opening_request_ids.ids)]
        return action

    def open_import_opening_request(self):
        opening_requests = self.env['comex.opening.request'].search([('proforma_bill_id', '=', self.id)])
        action = self.env['ir.actions.actions']._for_xml_id('foreign_trade.opening_request_action_form')
        action['domain'] = [('id', 'in', opening_requests.ids)]
        return action

    def _prepare_invoice(self):
        """Prepare the dict of values to create the new invoice for a purchase order.
        """
        self.ensure_one()
        res = super()._prepare_invoice()
        res['purchase_folder_import_id'] = self.purchase_folder_import_id.id
        return res


class SmartestAccountMove(models.Model):
    _inherit = 'account.move'

    purchase_folder_import_id = fields.Many2one('purchase.import.folder', string="Import Folder",
                                                domain=[('state', '=', 'ongoing')])

    def write(self, vals):
        if vals.get('purchase_folder_import_id'):
            folder_id = self.env['purchase.import.folder'].browse(vals.get('purchase_folder_import_id'))
            purchase_line = self.invoice_line_ids.filtered(lambda x: x.purchase_line_id)
            purchase = purchase_line[0].purchase_line_id if purchase_line else False
            folder_id.vendor_line_ids.create({
                'folder_id': folder_id.id,
                'invoice_id': self.id,
                'purchase_order_id': purchase.order_id.id if purchase else False,
                'vendor_invoice': True if purchase else False,
            })
        return super(SmartestAccountMove, self).write(vals)

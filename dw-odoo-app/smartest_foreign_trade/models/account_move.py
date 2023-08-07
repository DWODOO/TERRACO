from odoo import _, api, fields, models


class SmartestAccountMove(models.Model):
    _inherit = 'account.move'

    purchase_folder_import_id = fields.Many2one('smartest.import.folder', string="Import Folder")
    sale_folder_export_id = fields.Many2one('export.folder', string="Export Folder")
    smartest_purchase_id = fields.Many2one('purchase.order', string="Purchase Order")
    supplier_invoice_type = fields.Selection([
        ('supplier_invoice', 'Supplier Invoice'), ('landed_costs_invoices', 'Landed Costs Invoice'),
    ], string="Supplier Inoices Type", default="supplier_invoice",
        readonly=True,
        store=True,
        states={'draft': [('readonly', False), ('required', True)]},
        tracking=True)

    @api.model
    def action_supplier_invoices_analysis(self):
        domain = [('move_type', '=', 'in_invoice'), ('supplier_invoice_type', '=', 'supplier_invoice')]
        purchase_folder_import_id = self.env.context.get('active_ids')
        if purchase_folder_import_id:
            domain += [('purchase_folder_import_id', 'in', self.env.context.get('active_ids', []))]
        purchase_folder_import_id = self.env["smartest.import.folder"].browse(purchase_folder_import_id[-1])
        return {
            'name': _("Supplier Invoices Analysis"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'search_view_id': self.env.ref(
                'account.view_account_invoice_filter').id,
            'domain': domain,
            'context': {'default_move_type': 'in_invoice',
                        'default_purchase_folder_import_id': purchase_folder_import_id.id,
                        'default_supplier_invoice_type': 'supplier_invoice'}
        }


    @api.model
    def action_landed_costs_invoices_analysis(self):
        domain = [('move_type', '=', 'in_invoice'), ('supplier_invoice_type', '=', 'landed_costs_invoices')]
        purchase_folder_import_id = self.env.context.get('active_ids')
        if purchase_folder_import_id:
            domain += [('purchase_folder_import_id', 'in', self.env.context.get('active_ids', []))]
        purchase_folder_import_id = self.env["smartest.import.folder"].browse(purchase_folder_import_id[-1])
        return {
            'name': _("Supplier Invoices Analysis"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'search_view_id': self.env.ref(
                'account.view_account_invoice_filter').id,
            'domain': domain,
            'context': {'default_move_type': 'in_invoice',
                        'default_purchase_folder_import_id': purchase_folder_import_id.id,
                        'default_supplier_invoice_type': 'landed_costs_invoices'}
        }

    def action_view_landed_costs(self):
        """
        override the action_view_landed_costs super method to add the import folder chosen in the invoice to the landed cost dict .

        """
        self.ensure_one()
        res = super().action_view_landed_costs()
        if self.purchase_folder_import_id:
            res["context"]["default_purchase_folder_import_id"] = self.purchase_folder_import_id.id

            res["context"]["default_purchase_order_ids"] = [(4, purchase.id) for purchase in
                                                            self.purchase_folder_import_id.purchase_order_ids]

            res["context"]["default_picking_ids"] = [(4, picking.id) for picking in
                                                     self.purchase_folder_import_id.purchase_picking_ids]
            smartest_product_lines = self.invoice_line_ids.filtered(
                lambda line: not line.is_landed_costs_line and line.product_id)
            res["context"]["default_smartest_product_ids"] = [(4, line.product_id.id) for line in
                                                              smartest_product_lines]

        return res

    def button_create_landed_costs(self):
        """Create a `stock.landed.cost` record associated to the account move of `self`, each
        `stock.landed.costs` lines mirroring the current `account.move.line` of self.
        """
        self.ensure_one()
        landed_costs_lines = self.line_ids.filtered(lambda line: line.is_landed_costs_line)
        smartest_product_lines = self.invoice_line_ids.filtered(
            lambda line: not line.is_landed_costs_line and line.product_id)
        landed_costs = self.env['stock.landed.cost'].create({
            'vendor_bill_id': self.id,
            'purchase_folder_import_id': self.purchase_folder_import_id.id if self.purchase_folder_import_id else False,
            'purchase_order_ids': [(4, purchase.id) for purchase in
                                   self.purchase_folder_import_id.purchase_order_ids] if (
                    self.purchase_folder_import_id and self.purchase_folder_import_id.purchase_order_ids) else False,
            'picking_ids': [(4, picking.id) for picking in
                            self.purchase_folder_import_id.purchase_picking_ids] if (
                    self.purchase_folder_import_id and self.purchase_folder_import_id.purchase_picking_ids) else False,
            'cost_lines': [(0, 0, {
                'product_id': l.product_id.id,
                'name': l.product_id.name,
                'account_id': l.product_id.product_tmpl_id.get_product_accounts()['stock_input'].id,
                'price_unit': l.currency_id._convert(l.price_subtotal, l.company_currency_id, l.company_id,
                                                     l.move_id.date,
                                                     rate=l.purchase_line_id.order_id.currency_rate_import_purchase),
                'split_method': l.product_id.split_method_landed_cost or 'equal',
            }) for l in landed_costs_lines],
            'smartest_product_ids': [(4, line.product_id.id) for line in smartest_product_lines],
        })
        landed_costs._onchange_picking_ids()
        action = self.env["ir.actions.actions"]._for_xml_id("stock_landed_costs.action_stock_landed_cost")
        return dict(action, view_mode='form', res_id=landed_costs.id, views=[(False, 'form')])


class Currency(models.Model):
    _inherit = "res.currency"

    def _convert(self, from_amount, to_currency, company, date, round=True, rate=None):
        """"""
        # obverride super methode to use smartest_currency_rate
        """"""
        self, to_currency = self or to_currency, to_currency or self
        assert self, "convert amount from unknown currency"
        assert to_currency, "convert amount to unknown currency"
        assert company, "convert amount from unknown company"
        assert date, "convert amount from unknown date"
        # apply conversion rate
        if rate:
            to_amount = from_amount * rate
            return to_currency.round(to_amount) if round else to_amount
        return super()._convert(from_amount, to_currency, company, date)

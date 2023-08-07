from odoo import fields, models, api, _


class SmartestImportFolder(models.Model):
    _name = 'purchase.import.folder'
    _description = "Purchase Import Folder"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"


    name = fields.Char('Number')
    description = fields.Char('Description')
    date = fields.Date('Date', required=True, default=fields.Date.context_today)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    vendor_line_ids = fields.One2many('purchase.import.folder.line', 'folder_id', string='Vendor Inv', domain=[('vendor_invoice','=',True)], readonly=1, states={'ongoing': [('readonly', False)]})
    fees_line_ids = fields.One2many('purchase.import.folder.line', 'folder_id', string='Fees Inv', domain=[('vendor_invoice','=',False)], readonly=1, states={'ongoing': [('readonly', False)]})
    purchase_order_ids = fields.One2many('purchase.order', 'purchase_folder_import_id', string='Purchase Order', readonly=1, states={'ongoing': [('readonly', False)]})
    purchase_picking_ids = fields.Many2many('stock.picking' ,compute="compute_purchase_order_ids_picking_ids" , string='Purchase Picking', readonly=1)
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("ongoing", "On going"),
            ("done", "Done"),
            ("cancel", "Cancel"),
        ],
        default="draft",ondelete='cascade',
    )
    comex_import_file_ids = fields.One2many("comex.import.file",'import_folder_id' , string="Import File")

    def action_view_import_file(self):
        tree_view = self.env.ref('foreign_trade.import_file_view_tree')
        form_view = self.env.ref('foreign_trade.comex_import_file_form_view')
        action = {
            'name': _('Import File'),
            'type': 'ir.actions.act_window',
            'res_model': 'comex.import.file',
            'views': [(form_view.id, 'form'),(tree_view.id, 'tree')],
            'context': {'default_import_folder_id': self.id}
        }
        if self.comex_import_file_ids.ids:
            action['views'] = [(tree_view.id, 'tree'),(form_view.id, 'form')]
            action['view_mode'] = 'tree'
            action['domain'] = [('import_folder_id', '=', self.id)]
        else:
            action['views'] = [(form_view.id, 'form')]
            action['view_mode'] = 'form'
            action['context'] = {'default_import_folder_id': self.id}
        return action

    def compute_purchase_order_ids_picking_ids(self):
        self.purchase_picking_ids = False
        for pick in self.purchase_order_ids.picking_ids:
            self.purchase_picking_ids += pick


    @api.model
    def _get_default_name(self):
        return self.env["ir.sequence"].next_by_code("purchase.import.folder")

    @api.model
    def create(self, vals):
        if not vals.get('name') :
            vals['name'] = self._get_default_name()
        folder = super(SmartestImportFolder, self).create(vals)
        return folder

    def button_done(self):
        for folder in self:
            if folder.state == 'draft' :
                folder.state = 'ongoing'
            elif folder.state == 'ongoing' :
                folder.state = 'done'

    def button_draft(self):
        for folder in self:
            if folder.state == 'ongoing' :
                folder.state = 'draft'

    def action_create_purchase_order(self):
        for folder in self :
            return


class SmartestImportFolderLines(models.Model):
    _name = 'purchase.import.folder.line'
    _description = "Purchase Import Folder Lines"


    folder_id = fields.Many2one('purchase.import.folder', string="Folder")
    invoice_id = fields.Many2one('account.move', string="Invoice", domain="[('move_type','=','in_invoice')]")
    purchase_order_id = fields.Many2one('purchase.order', string="Purchase")
    vendor_invoice = fields.Boolean(compute="_compute_invoice_vendor", store=True)
    invoice_state = fields.Selection(string="Invoice State", related="invoice_id.state")
    payment_state = fields.Selection(string="Payment State", related="invoice_id.payment_state")
    landed_cost_visible = fields.Boolean(related="invoice_id.landed_costs_visible")
    landed_costs_ids = fields.One2many(related="invoice_id.landed_costs_ids")
    amount_total = fields.Monetary(string="Total", related="invoice_id.amount_total", currency_field="invoice_currency")
    invoice_currency = fields.Many2one("res.currency", string='Currency', related="invoice_id.currency_id", readonly=True)


    @api.depends('invoice_id')
    def _compute_invoice_vendor(self):
        for line in self:
            if line.invoice_id:
                line.vendor_invoice = False
                if any(this.order_id for this in line.invoice_id.invoice_line_ids.purchase_line_id):
                   line.vendor_invoice = True


    def button_create_landed_cost(self):
        for line in self:
            return line.button_create_landed_costs()

    def button_create_landed_costs(self):
        """Create a `stock.landed.cost` record associated to the account move of `self`, each
        `stock.landed.costs` lines mirroring the current `account.move.line` of self.
        """
        self.ensure_one()
        landed_costs_lines = self.invoice_id.line_ids.filtered(lambda line: line.is_landed_costs_line)

        landed_costs = self.env['stock.landed.cost'].create({
            'vendor_bill_id': self.invoice_id.id,
            'picking_ids': self.folder_id.purchase_picking_ids.ids,
            'cost_lines': [(0, 0, {
                'product_id': l.product_id.id,
                'name': l.product_id.name,
                'account_id': l.product_id.product_tmpl_id.get_product_accounts()['stock_input'].id,
                'price_unit': l.currency_id._convert(l.price_subtotal, l.company_currency_id, l.company_id, l.move_id.date),
                'split_method': l.product_id.split_method_landed_cost or 'equal',
            }) for l in landed_costs_lines],
        })
        landed_costs._onchange_picking_ids()
        action = self.env["ir.actions.actions"]._for_xml_id("stock_landed_costs.action_stock_landed_cost")
        return dict(action, view_mode='form', res_id=landed_costs.id, views=[(False, 'form')])

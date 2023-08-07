from odoo.exceptions import ValidationError

from odoo import _, fields, models, api


class SmartestImportFolder(models.Model):
    _name = 'smartest.import.folder'
    _description = "Import Folder"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    name = fields.Char('Number')
    description = fields.Char('Description')
    date = fields.Date('Date', required=True, default=fields.Date.context_today)
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)

    purchase_order_ids = fields.One2many('purchase.order', 'purchase_folder_import_id', string='Purchase Order',
                                         readonly=1, states={'ongoing': [('readonly', False)]})
    supplier_invoices_ids = fields.One2many('account.move', 'purchase_folder_import_id', string='Supplier Invoices',
                                            readonly=1, states={'ongoing': [('readonly', False)]})
    landed_costs_valorisations_ids = fields.One2many('stock.landed.cost', 'purchase_folder_import_id',
                                                     string='Landed Costs Valorisations',
                                                     readonly=1, states={'ongoing': [('readonly', False)]})
    purchase_picking_ids = fields.Many2many('stock.picking', compute="compute_purchase_order_ids_picking_ids",
                                            string='Purchase Picking', readonly=1)
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("ongoing", "On going"),
            ("done", "Done"),
            ("cancel", "Cancel"),
        ],
        compute="_compute_state", force_save=1, store=1
    )
    state_folder = fields.Selection(
        selection=[
            ("supplier_offer", "Supplier Offer/Domiciliation"),
            ("expedition", "Expedition"),
            ("dedouanement", "Dédouanement"),
            ("payment_reception", "Payment/Reception"),
            ("cancel", "Cancel"),
        ],
        copy=False, default="supplier_offer", force_save=1,
        group_expand='_group_expand_states', store=1
    )
    active = fields.Boolean(default=True)

    import_file_ids = fields.One2many("smartest.import.file", 'import_folder_id', string="Import File")
    import_file_count = fields.Integer('Number of Credit Commitment',
                                       compute='_compute_import_file_count')
    valorisation_count = fields.Integer('Number of Landed Costs Valorisations',
                                        compute='_compute_valorisation_count')
    order_count = fields.Integer('Number of Orders',
                                 compute='_compute_purchase_order_count')

    order_total = fields.Float('Amount Total of Orders',
                               compute='_compute_purchase_order_count')
    supplier_invoices_count = fields.Integer('Number of Invoices',
                                             compute='_compute_supplier_invoices_count')

    supplier_invoices_total = fields.Float('Amount Total of Invoices',
                                           compute='_compute_supplier_invoices_count')
    landed_costs_invoices_count = fields.Integer('Number of Landed Costs Invoices',
                                                 compute='_compute_supplier_invoices_count')

    landed_costs_invoices_total = fields.Float('Amount Total of Landed Costs Invoices',
                                               compute='_compute_supplier_invoices_count')


    def _group_expand_states(self, states, domain, order):
        return [key for key, val in type(self).state_folder.selection]

    @api.depends("purchase_order_ids")
    def _compute_purchase_order_count(self):
        folder_without_orders = self.filtered(lambda import_folder: not import_folder.purchase_order_ids)
        folder_without_orders.write({
            'order_count': 0,
            'order_total': 0,
        })
        folder_with_orders = self.filtered(lambda import_folder: import_folder.purchase_order_ids)
        for folder in folder_with_orders:
            purchase_order_ids = folder.purchase_order_ids
            folder.order_count = len(purchase_order_ids)
            folder.order_total = sum(purchase_order_ids.mapped("amount_total"))

    @api.depends("import_file_ids")
    def _compute_import_file_count(self):
        folder_without_import_file_ids = self.filtered(
            lambda import_folder: not import_folder.import_file_ids)
        folder_without_import_file_ids.write({
            'import_file_count': 0,
        })
        import_file_ids = self.filtered(lambda import_folder: import_folder.import_file_ids)
        for folder in import_file_ids:
            import_file_ids = folder.import_file_ids
            folder.import_file_count = len(import_file_ids)

    @api.depends("landed_costs_valorisations_ids", "supplier_invoices_ids")
    def _compute_valorisation_count(self):

        for folder in self:
            purchase_folder_import_id = folder

            landed_valuation_domain = [('cost_id.purchase_folder_import_id', '=', purchase_folder_import_id.id)]
            stock_valuation_layer_ids = self.env['stock.valuation.adjustment.lines'].search(landed_valuation_domain)
            folder.valorisation_count = len(stock_valuation_layer_ids)

    @api.depends("supplier_invoices_ids")
    def _compute_supplier_invoices_count(self):
        folder_without_invoices = self.filtered(lambda import_folder: not import_folder.supplier_invoices_ids)
        folder_without_invoices.write({
            'supplier_invoices_count': 0,
            'supplier_invoices_total': 0,
            'landed_costs_invoices_count': 0,
            'landed_costs_invoices_total': 0,
        })
        folder_with_invoices = self.filtered(lambda import_folder: import_folder.supplier_invoices_ids)
        for folder in folder_with_invoices:
            supplier_invoices_count = supplier_invoices_total = 0
            landed_costs_invoices_count = landed_costs_invoices_total = 0
            supplier_invoices_ids = folder.supplier_invoices_ids.filtered(
                lambda
                    invoice: invoice.supplier_invoice_type == "supplier_invoice" and invoice.move_type == "in_invoice")
            supplier_landed_costs_ids = folder.supplier_invoices_ids.filtered(
                lambda
                    invoice: invoice.supplier_invoice_type != "supplier_invoice" and invoice.move_type == "in_invoice")
            if supplier_invoices_ids:
                supplier_invoices_count = len(supplier_invoices_ids)
                supplier_invoices_total = sum(supplier_invoices_ids.mapped("amount_total"))
            if supplier_landed_costs_ids:
                landed_costs_invoices_count = len(supplier_landed_costs_ids)
                landed_costs_invoices_total = sum(supplier_landed_costs_ids.mapped("amount_total"))
            folder.supplier_invoices_count = supplier_invoices_count
            folder.supplier_invoices_total = supplier_invoices_total
            folder.landed_costs_invoices_count = landed_costs_invoices_count
            folder.landed_costs_invoices_total = landed_costs_invoices_total

    @api.depends("state_folder")
    def _compute_state(self):
        for record in self:
            if record.state_folder == "supplier_offer":
                state = "draft"
            elif record.state_folder == "payment_reception":
                state = "done"
            elif record.state_folder == "cancel":
                state = "cancel"
            else:
                state = "ongoing"
            record.state = state

    def compute_purchase_order_ids_picking_ids(self):
        self.purchase_picking_ids = False
        for pick in self.purchase_order_ids.picking_ids:
            self.purchase_picking_ids += pick

    @api.model
    def _get_default_name(self):
        return self.env.ref('smartest_foreign_trade.import_folder_sequence').next_by_id()

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = self._get_default_name()
        folder = super(SmartestImportFolder, self).create(vals)
        return folder

    def button_validate(self):
        folder_can_t_be_validated = self.filtered(
            lambda import_folder: import_folder.state_folder in ["payment_reception", "cancel"])
        if folder_can_t_be_validated:
            raise ValidationError(
                _("You can't validate a Done/canceled Folder")
            )

        for folder in self:
            if folder.state_folder == 'supplier_offer':
                folder.state_folder = 'expedition'
            elif folder.state_folder == 'expedition':
                folder.state_folder = 'dedouanement'
            elif folder.state_folder == 'dedouanement':
                folder.state_folder = 'payment_reception'

    def button_draft(self):
        folder_can_t_be_set_as_draft = self.filtered(
            lambda import_folder: import_folder.state_folder in ["payment_reception"])
        if folder_can_t_be_set_as_draft:
            raise ValidationError(
                _("You can't Set as Draft a Done Folder,\nYou should set it as canceled.")
            )
        for folder in self:
            if folder.state_folder != 'payment_reception':
                folder.state_folder = 'supplier_offer'

    def button_cancel(self):
        folder_can_t_be_set_as_cancel = self.filtered(
            lambda import_folder: import_folder.state_folder in ["supplier_offer"])
        if folder_can_t_be_set_as_cancel:
            raise ValidationError(
                _("You can't Set as Cancel a Draft Folder that doesn't even begin.")
            )
        for folder in self:
            if folder.state_folder != 'supplier_offer':
                folder.state_folder = 'cancel'

from odoo.exceptions import ValidationError

from odoo import _, fields, models, api


class ExportFolder(models.Model):
    _name = 'export.folder'
    _description = "Export Folder"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    name = fields.Char('Number')
    description = fields.Char('Description')
    date = fields.Date('Date', required=True, default=fields.Date.context_today)
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)

    sale_ids = fields.One2many('sale.order', 'sale_folder_export_id', string='Sale Order',
                               readonly=1, states={'ongoing': [('readonly', False)]})
    invoices_ids = fields.One2many('account.move', 'sale_folder_export_id', string='Invoices',
                                   readonly=1, states={'ongoing': [('readonly', False)]})

    sale_picking_ids = fields.Many2many('stock.picking', compute="compute_sale_order_ids_picking_ids",
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
            ("offer", "Offer/Domiciliation"),
            ("expedition", "Expedition"),
            ("dedouanement", "Dédouanement"),
            ("payment_reception", "Payment/Reception"),
            ("cancel", "Cancel"),
        ],
        copy=False, default="offer", force_save=1,
        group_expand='_group_expand_states', store=1
    )
    active = fields.Boolean(default=True)

    export_file_ids = fields.One2many("smartest.import.file", 'export_folder_id', string="Export File")
    export_file_count = fields.Integer('Number of Credit Commitment',
                                       compute='_compute_export_file_count')
    order_count = fields.Integer('Number of Orders',
                                 compute='_compute_sale_order_count')

    order_total = fields.Float('Amount Total of Orders',
                               compute='_compute_sale_order_count')
    invoices_count = fields.Integer('Number of Invoices',
                                    compute='_compute_invoices_count')

    invoices_total = fields.Float('Amount Total of Invoices',
                                  compute='_compute_invoices_count')

    def _group_expand_states(self, states, domain, order):
        return [key for key, val in type(self).state_folder.selection]

    @api.depends("sale_ids")
    def _compute_sale_order_count(self):
        folder_without_orders = self.filtered(lambda import_folder: not import_folder.sale_ids)
        folder_without_orders.write({
            'order_count': 0,
            'order_total': 0,
        })
        folder_with_orders = self.filtered(lambda import_folder: import_folder.sale_ids)
        for folder in folder_with_orders:
            order_ids = folder.sale_ids
            folder.order_count = len(order_ids)
            folder.order_total = sum(order_ids.mapped("amount_total"))

    @api.depends("export_file_ids")
    def _compute_export_file_count(self):
        folder_without_export_file_ids = self.filtered(
            lambda import_folder: not import_folder.export_file_ids)
        folder_without_export_file_ids.write({
            'export_file_count': 0,
        })
        export_file_ids = self.filtered(lambda import_folder: import_folder.export_file_ids)
        for folder in export_file_ids:
            export_file_ids = folder.export_file_ids
            folder.export_file_count = len(export_file_ids)

    @api.depends("invoices_ids")
    def _compute_invoices_count(self):
        folder_without_invoices = self.filtered(lambda import_folder: not import_folder.invoices_ids)
        folder_without_invoices.write({
            'invoices_count': 0,
            'invoices_total': 0,
        })
        folder_with_invoices = self.filtered(lambda import_folder: import_folder.invoices_ids)
        for folder in folder_with_invoices:
            invoices_count = invoices_total = 0
            invoices_ids = folder.invoices_ids.filtered(
                lambda
                    invoice: invoice.move_type == "out_invoice")

            if invoices_ids:
                invoices_count = len(invoices_ids)
                invoices_total = sum(invoices_ids.mapped("amount_total"))

            folder.invoices_count = invoices_count
            folder.invoices_total = invoices_total

    @api.depends("state_folder")
    def _compute_state(self):
        for record in self:
            if record.state_folder == "offer":
                state = "draft"
            elif record.state_folder == "payment_reception":
                state = "done"
            elif record.state_folder == "cancel":
                state = "cancel"
            else:
                state = "ongoing"
            record.state = state

    def compute_sale_order_ids_picking_ids(self):
        self.sale_picking_ids = False
        for pick in self.sale_ids.picking_ids:
            self.sale_picking_ids += pick

    @api.model
    def _get_default_name(self):
        return self.env.ref('smartest_foreign_trade.export_folder_sequence').next_by_id()

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = self._get_default_name()
        folder = super(ExportFolder, self).create(vals)
        return folder

    def button_validate(self):
        folder_can_t_be_validated = self.filtered(
            lambda import_folder: import_folder.state_folder in ["payment_reception", "cancel"])
        if folder_can_t_be_validated:
            raise ValidationError(
                _("You can't validate a Done/canceled Folder")
            )

        for folder in self:
            if folder.state_folder == 'offer':
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
                folder.state_folder = 'offer'

    def button_cancel(self):
        folder_can_t_be_set_as_cancel = self.filtered(
            lambda import_folder: import_folder.state_folder in ["offer"])
        if folder_can_t_be_set_as_cancel:
            raise ValidationError(
                _("You can't Set as Cancel a Draft Folder that doesn't even begin.")
            )
        for folder in self:
            if folder.state_folder != 'offer':
                folder.state_folder = 'cancel'

    def action_open_sales(self):
        export_id = self.id
        domain = [('sale_folder_export_id', '=', export_id)]
        return {
            'name': _('Sale Order(s)'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'domain': domain,
            'context': {
                'default_sale_folder_export_id': export_id,
            }
        }

    def action_open_invoices(self):
        export_folder_id = self.id
        domain = [('move_type', '=', 'out_invoice'), ('sale_folder_export_id', '=', export_folder_id)]
        return {
            'name': _("Invoices"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': domain,
            'context': {'default_move_type': 'out_invoice',
                        'default_sale_folder_export_id': export_folder_id, }
        }


class SmartestSaleOrder(models.Model):
    _inherit = 'sale.order'

    sale_folder_export_id = fields.Many2one('export.folder', string="Export Folder")

    def _prepare_invoice(self):
        """override the _prepare_invoice super method to add the Export folder chosen  to the dict .
        """
        self.ensure_one()
        invoice_vals = super(SmartestSaleOrder, self)._prepare_invoice()
        if self.sale_folder_export_id:
            invoice_vals["sale_folder_export_id"] = self.sale_folder_export_id.id
        return invoice_vals

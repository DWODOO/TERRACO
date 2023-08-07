from odoo import _, api, fields, models
from odoo.exceptions import UserError

_STATES = [
    ("draft", "Draft"),
    ("to_approve", "To be approved"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
    ("done", "Done"),
]


class PurchaseRequestLine(models.Model):
    _name = "purchase.request.line"
    _description = "Purchase Request Line"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    name = fields.Char(string="Description",)
    product_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Product Unit of Measure",
        # track_visibility="onchange",
    )
    product_qty = fields.Float(
        string="Quantity", digits="Product Unit of Measure"
    )
    request_id = fields.Many2one(
        comodel_name="purchase.request",
        string="Purchase Request",
        ondelete="cascade",
        readonly=True,
        index=True,
        auto_join=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        related="request_id.company_id",
        string="Company",
        store=True,
    )
    requested_by = fields.Many2one(
        comodel_name="res.users",
        related="request_id.requested_by",
        string="Requested by",
        store=True,
    )
    assigned_to = fields.Many2one(
        comodel_name="res.users",
        related="request_id.assigned_to",
        string="Assigned to",
        store=True,
    )
    date_start = fields.Date(related="request_id.date_start", store=True)
    description = fields.Text(
        # related="request_id.description",
        string="PR Description",
        store=True,
        readonly=False,
    )
    date_required = fields.Date(
        string="Request Date",
        required=True,
        # track_visibility="onchange",
        default=fields.Date.context_today,
    )
    is_editable = fields.Boolean(
        string="Is editable", compute="_compute_is_editable", readonly=True
    )
    justification = fields.Text(string="Justification")
    request_state = fields.Selection(
        string="Request state",
        related="request_id.state",
        selection=_STATES,
        store=True,
    )
    cancelled = fields.Boolean(
        string="Cancelled", readonly=True, default=False, copy=False
    )

    estimated_cost = fields.Monetary(
        string="Estimated Cost",
        currency_field="currency_id",
        default=0.0,
        help="Estimated cost of Purchase Request Line, not propagated to PO.",
    )
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)

    purchase_line_ids = fields.Many2many(
        "purchase.order.line",
        column1="purchase_request_line_ids",
        string="Purchase Order Lines",
        readonly=True,
        copy=False,
    )

    @api.depends(
        "name",
        "product_uom_id",
        "product_qty",
        "date_required",
    )
    def _compute_is_editable(self):
        for rec in self:
            if rec.request_id.state in ("to_approve", "approved", "rejected", "done"):
                rec.is_editable = False
            else:
                rec.is_editable = True
        # for rec in self.filtered(lambda p: p.purchase_lines):
        #     rec.is_editable = False

    def do_cancel(self):
        """Actions to perform when cancelling a purchase request line."""
        self.write({"cancelled": True})

    def do_uncancel(self):
        """Actions to perform when uncancelling a purchase request line."""
        self.write({"cancelled": False})

    def write(self, vals):
        res = super(PurchaseRequestLine, self).write(vals)
        if vals.get("cancelled"):
            requests = self.mapped("request_id")
            requests.check_auto_reject()
        return res

    # @api.depends("purchase_lines.state", "purchase_lines.order_id.state")
    # def _compute_purchase_state(self):
    #     for rec in self:
    #         temp_purchase_state = False
    #         if rec.purchase_lines:
    #             if any([po_line.state == "done" for po_line in rec.purchase_lines]):
    #                 temp_purchase_state = "done"
    #             elif all([po_line.state == "cancel" for po_line in rec.purchase_lines]):
    #                 temp_purchase_state = "cancel"
    #             elif any(
    #                 [po_line.state == "purchase" for po_line in rec.purchase_lines]
    #             ):
    #                 temp_purchase_state = "purchase"
    #             elif any(
    #                 [po_line.state == "to approve" for po_line in rec.purchase_lines]
    #             ):
    #                 temp_purchase_state = "to approve"
    #             elif any([po_line.state == "sent" for po_line in rec.purchase_lines]):
    #                 temp_purchase_state = "sent"
    #             elif all(
    #                 [
    #                     po_line.state in ("draft", "cancel")
    #                     for po_line in rec.purchase_lines
    #                 ]
    #             ):
    #                 temp_purchase_state = "draft"
    #         rec.purchase_state = temp_purchase_state

    def _can_be_deleted(self):
        self.ensure_one()
        return self.request_state == "draft"

    def unlink(self):
        # if self.mapped("purchase_lines"):
        #     raise UserError(
        #         _("You cannot delete a record that refers to purchase lines!")
        #     )
        for line in self:
            if not line._can_be_deleted():
                raise UserError(
                    _(
                        "You can only delete a purchase request line "
                        "if the purchase request is in draft state."
                    )
                )
        return super(PurchaseRequestLine, self).unlink()

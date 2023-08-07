from odoo.exceptions import UserError

from odoo import _, api, fields, models

_STATES = [
    ("draft", "demande de Besoin"),
    ("ongoing", "En cours"),
    ("done", "Demande d'achat"),
]


class PurchaseProductRequest(models.Model):
    _name = "purchase.product.request"
    _description = "Purchase Product Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    @api.model
    def _company_get(self):
        return self.env["res.company"].browse(self.env.company.id)

    @api.model
    def _get_default_requested_by(self):
        return self.env["res.users"].browse(self.env.uid)

    @api.model
    def _get_default_name(self):
        return self.env["ir.sequence"].next_by_code("purchase.product.request")

    @api.depends("state")
    def _compute_is_editable(self):
        for rec in self:
            if rec.state in ("done"):
                rec.is_editable = False
            else:
                rec.is_editable = True

    name = fields.Char(
        string="Request Reference",
        required=True,
        default="New",
        # track_visibility="onchange",
        readonly=True,
    )
    date_start = fields.Date(
        string="Request date",
        help="Date when the user initiated the request.",
        default=fields.Date.context_today,
        # track_visibility="onchange",
    )
    desired_date = fields.Date(
        string="Desired reception date",
        help="Date when the user desire to receive the request.",
        default=fields.Date.context_today,
        # track_visibility="onchange",
    )
    latest_date = fields.Date(
        string="Latest reception date",
        help="Date when the user desire to receive the request at latest.",
        default=fields.Date.context_today,
        # track_visibility="onchange",
    )
    project = fields.Char('Project(s)')
    requested_by = fields.Many2one(
        "res.users",
        string="Requested by",
        required=True,
        copy=False,
        # track_visibility="onchange",
        default=_get_default_requested_by,
        index=True,
    )
    assigned_to = fields.Many2one(
        "res.users",
        string="Assigned to",
        related="create_uid",
        index=True,
        store=True,
    )
    description = fields.Text(string="Description")
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=_company_get,
    )
    line_ids = fields.One2many(
        comodel_name="purchase.product.request.line",
        inverse_name="request_id",
        string="Products to Purchase",
        readonly=False,
        copy=True,
    )
    state = fields.Selection(
        selection=_STATES,
        string="Status",
        index=True,
        required=True,
        copy=False,
        default="draft",
    )
    is_editable = fields.Boolean(
        string="Is editable", compute="_compute_is_editable", readonly=True
    )
    to_approve_allowed = fields.Boolean(compute="_compute_to_approve_allowed")

    line_count = fields.Integer(
        string="Purchase Request Line count",
        compute="_compute_line_count",
        readonly=True,
    )

    purchase_order_ids = fields.One2many(
        'purchase.order',
        'purchase_request_id',
        string="Related Purchase Orders",
        readonly=True,
        copy=False,
    )

    purchase_order_count = fields.Integer(
        compute="_compute_purchase_order_count"
    )
    purchase_team_members_id = fields.Many2one('res.users', string='Purchase team members')
    financial_validator = fields.Many2one('res.users', string='Financial Validator')
    po_date_approve = fields.Date()
    url = fields.Char()
    # validation_comment = fields.Char(related="review_ids.comment",store=True)
    validation_state = fields.Selection([
        ('to_approuve', 'A approuvé'),
        ('rejected', 'Rejeté'),
        ('validated', 'Validé')
    ], string='Etat de Validation', compute="_compute_validation_state", store=True)
    request_status = fields.Selection([('available', 'Available'), ('not_available', 'Not Available')],
                                      default="not_available")

    @api.depends("review_ids", "state", "review_ids.status")
    def _compute_validation_state(self):
        for order in self:
            if not order.review_ids:
                order.validation_state = 'to_approuve'
            elif any(review.status == 'rejected' for review in order.review_ids):
                order.validation_state = 'rejected'
            elif all(review.status == 'approved' for review in order.review_ids):
                order.validation_state = 'validated'
            else:
                order.validation_state = 'to_approuve'

    @api.depends("purchase_order_ids")
    def _compute_purchase_order_count(self):
        for request in self:
            request.purchase_order_count = len(request.mapped("purchase_order_ids"))

    def action_view_purchase_orders(self):
        """
        This method is used by the Purchase Orders smart button. It opens a form view or a tree view
        :return: Action Dict
        """

        orders = self.mapped('purchase_order_ids')
        if not orders:
            raise UserError(
                _('There is no PO to view.')
            )
        tree_view = self.env.ref('purchase.purchase_order_tree')
        form_view = self.env.ref('purchase.purchase_order_form')
        action = {
            'name': _('Purchase Order(s)'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'context': {'default_purchase_order_ids': [(4, self.id)]}
        }
        if len(orders) == 1:
            action['views'] = [(form_view.id, 'form')]
            action['res_id'] = orders.id
            action['view_mode'] = 'form'
        else:
            action['views'] = [(tree_view.id, 'tree'), (form_view.id, 'form')]
            action['domain'] = [('id', 'in', orders.ids)]
        return action

    def action_create_purchase_order(self):
        ''' Create the RFQ/PO associated to the PR'''
        return {
            'name': _('Crée Demande d\'Achat'),
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'context': {
                'active_model': 'purchase.product.request',
                'active_ids': self.ids,
                'form_view_initial_mode': 'edit',
                'default_date_order': self.date_start,
                'default_purchase_request_create_id': self.assigned_to.id,
                'default_order_line': [(0, 0, {
                    'name': line.name if line.name or not line.product_id else line.product_id.name,
                    'product_qty': line.product_qty, 'product_id': line.product_id.id if line.product_id else False,
                    'product_uom': line.product_id.uom_id.id if line.product_id else False})
                                       for line in
                                       self.line_ids],
                'default_purchase_request_id': self.id
            },
            'target': 'current',
            'type': 'ir.actions.act_window',
        }

    @api.depends("line_ids")
    def _compute_line_count(self):
        for rec in self:
            rec.line_count = len(rec.mapped("line_ids"))

    @api.depends("state", "line_ids.product_qty", "line_ids.cancelled")
    def _compute_to_approve_allowed(self):
        for rec in self:
            rec.to_approve_allowed = rec.state == "draft" and any(
                [not line.cancelled and line.product_qty for line in rec.line_ids]
            )

    def copy(self, default=None):
        default = dict(default or {})
        self.ensure_one()
        default.update({"state": "draft", "name": self._get_default_name()})
        return super(PurchaseProductRequest, self).copy(default)

    @api.model
    def _get_partner_id(self, request):
        user_id = request.assigned_to or self.env.user
        return user_id.partner_id.id

    @api.model
    def create(self, vals):
        if not vals.get('name') == _('New'):
            vals['name'] = self.env["ir.sequence"].next_by_code("product.request") or _('/')
        request = super(PurchaseProductRequest, self).create(vals)
        if vals.get("assigned_to"):
            partner_id = self._get_partner_id(request)
            request.message_subscribe(partner_ids=[partner_id])
        return request

    def _can_be_deleted(self):
        self.ensure_one()
        return self.state == "draft"

    def unlink(self):
        for request in self:
            if not request._can_be_deleted():
                raise UserError(
                    _("You cannot delete a purchase request which is not draft.")
                )
        return super(PurchaseProductRequest, self).unlink()

    def button_draft(self):
        self.mapped("line_ids").do_uncancel()
        return self.write({"state": "draft"})

    def button_done(self):
        for rec in self:
            if rec.state == 'draft':
                rec.state = 'ongoing'
            elif rec.state == 'ongoing':
                val = {
                    'res_id': rec.id,
                    'res_model_id': self.env['ir.model']._get_id('purchase.product.request'),
                    'activity_type_id': 4,
                    'date_deadline': fields.Date.today(),
                    'automated': True,
                    'summary': f"demande de Besoin {rec.name} Approuvé",
                    'note': f"Cher {rec.create_uid.name} : Votre demande de Besoin a été Approuvé, vous pouvez continuer la procedure en cliquant sur cree une demande de prix !",
                    'user_id': rec.create_uid.id
                }
                self.env['mail.activity'].with_context(mail_activity_quick_update=True).create(val)
                # base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                # base_url += '/web?db=%s#id=%d&view_type=form&model=%s' % (self._cr.dbname,self.id, self._name)
                # rec.url = base_url
                # main_purchase_team = self.env.ref('purchase.group_purchase_manager')
                # ir_model_data = self.env['ir.model.data']
                # template_id = ir_model_data._xmlid_lookup('purchase_tier_validation.mail_template_product_request_RFQ')[2]
                # template = self.env['mail.template'].browse(template_id)
                # for group in main_purchase_team:
                #     for user in group.users:
                #         rec.purchase_team_members_id = user
                #         template.send_mail(rec.id, force_send=True)
                return self.write({"state": "done"})

    def check_auto_reject(self):
        """When all lines are cancelled the purchase request should be
        auto-rejected."""
        for pr in self:
            if not pr.line_ids.filtered(lambda l: l.cancelled is False):
                pr.write({"state": "rejected"})


class PurchaseProductRequestinherited(models.Model):
    _name = "purchase.product.request"
    _inherit = ["purchase.product.request", "tier.validation"]
    _state_from = ["ongoing"]
    _state_to = ["done"]

    _tier_validation_manual_config = False

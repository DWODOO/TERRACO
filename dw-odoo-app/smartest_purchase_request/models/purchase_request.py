from odoo import _, api, fields, models
from odoo.exceptions import UserError

_STATES = [
    ("draft", "Draft"),
    ("done", "Done"),
]


class PurchaseRequest(models.Model):
    _name = "purchase.request"
    _description = "Purchase Request"
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
        return self.env["ir.sequence"].next_by_code("purchase.request")

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
    # department_id = fields.Many2one(
    #     "organization.department",
    #     string="Beneficiary Structure",
    #     required=True,
    #     track_visibility="onchange",
    # )
    project = fields.Char('Project(s)')
    requested_by = fields.Many2one(
        comodel_name="res.users",
        string="Requested by",
        required=True,
        copy=False,
        # track_visibility="onchange",
        default=_get_default_requested_by,
        index=True,
    )
    assigned_to = fields.Many2one(
        comodel_name="res.users",
        string="Assigned to",
        # track_visibility="onchange",
        related="create_uid",
        # domain=lambda self: [
        #     (
        #         "groups_id",
        #         "in",
        #         self.env.ref("smartest_purchase_request.group_purchase_request_manager").id,
        #     )
        # ],
        index=True,
    )
    description = fields.Text(string="Description")
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=_company_get,
        # track_visibility="onchange",
    )
    line_ids = fields.One2many(
        comodel_name="purchase.request.line",
        inverse_name="request_id",
        string="Products to Purchase",
        readonly=False,
        copy=True,
        # track_visibility="onchange",
    )
    state = fields.Selection(
        selection=_STATES,
        string="Status",
        index=True,
        # track_visibility="onchange",
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

    purchase_order_ids = fields.Many2many(
        'purchase.order',
        'purchase_request_purchase_order_rel',
        column1="purchase_request_id",
        column2="purchase_order_id",
        string="Related Purchase Orders",
        readonly=True,
        copy=False,
    )

    purchase_order_count = fields.Integer(
        compute="_compute_purchase_order_count"
    )
    purchase_team_members_id = fields.Many2many('res.users', string='Purchase team members')
    site = fields.Selection([('dune', 'Les Dunes'), ('hm', 'HM')],string='Site')
    financial_validator = fields.Many2one('res.users', string='Financial Validator')
    po_date_approve = fields.Date()
    url = fields.Char()

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
            'name': _('Create RFQ'),
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'context': {
                'active_model': 'purchase.request',
                'active_ids': self.ids,
                'form_view_initial_mode': 'edit',
                'default_date_order': self.date_start,
                'default_purchase_request_create_id': self.assigned_to.id,
                'default_order_line': [(0, 0, {'name': line.name, 'product_qty': line.product_qty}) for line in
                                       self.line_ids],
                'default_purchase_request_ids': [(4, self.id)]
            },
            'target': 'current',
            'type': 'ir.actions.act_window',
        }

    # def action_view_purchase_order(self):
    #     action = self.env.ref("purchase.purchase_rfq").read()[0]
    #     lines = self.mapped("line_ids.purchase_lines.order_id")
    #     if len(lines) > 1:
    #         action["domain"] = [("id", "in", lines.ids)]
    #     elif lines:
    #         action["views"] = [
    #             (self.env.ref("purchase.purchase_order_form").id, "form")
    #         ]
    #         action["res_id"] = lines.id
    #     return action

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
        return super(PurchaseRequest, self).copy(default)

    @api.model
    def _get_partner_id(self, request):
        user_id = request.assigned_to or self.env.user
        return user_id.partner_id.id

    @api.model
    def create(self, vals):
        if not vals.get('name') == _('New'):
            vals['name'] = self.env["ir.sequence"].next_by_code("purchase.request") or _('/')
        request = super(PurchaseRequest, self).create(vals)
        if vals.get("assigned_to"):
            partner_id = self._get_partner_id(request)
            # request.message_subscribe(partner_ids=[partner_id])
        return request

    def write(self, vals):
        res = super(PurchaseRequest, self).write(vals)
        for request in self:
            if vals.get("assigned_to"):
                partner_id = self._get_partner_id(request)
                request.message_subscribe(partner_ids=[partner_id])
        return res

    def _can_be_deleted(self):
        self.ensure_one()
        return self.state == "draft"

    def unlink(self):
        for request in self:
            if not request._can_be_deleted():
                raise UserError(
                    _("You cannot delete a purchase request which is not draft.")
                )
        return super(PurchaseRequest, self).unlink()

    def button_draft(self):
        self.mapped("line_ids").do_uncancel()
        return self.write({"state": "draft"})

    def button_done(self):
        for rec in self:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            base_url = '/web?db=%s#id=%d&view_type=form&model=%s' % (self._cr.dbname,self.id, self._name)
            rec.url = base_url
            main_purchase_team = self.env.ref('smartest_purchase_request.group_purchase_team')
            purchase_groups = self.env['res.groups'].search([('smartest_parent_group','=', main_purchase_team.id)])
            ir_model_data = self.env['ir.model.data']
            template_id = ir_model_data._xmlid_lookup('smartest_purchase_request.mail_template_request_RFQ')[2]
            template = self.env['mail.template'].browse(template_id)
            for group in purchase_groups:
                for user in group.users:
                    rec.purchase_team_members_id = user
                    template.send_mail(rec.id, force_send=True)
            return self.write({"state": "done"})

    def check_auto_reject(self):
        """When all lines are cancelled the purchase request should be
        auto-rejected."""
        for pr in self:
            if not pr.line_ids.filtered(lambda l: l.cancelled is False):
                pr.write({"state": "rejected"})

    # def to_approve_allowed_check(self):
    #     for rec in self:
    #         if not rec.to_approve_allowed:
    #             raise UserError(
    #                 _(
    #                     "You can't request an approval for a purchase request "
    #                     "which is empty. (%s)"
    #                 )
    #                 % rec.name
    #             )

    # def sale_team_notification(self):
    #     print('none')
        # '''
        # This function opens a window to compose an email, with the edi purchase template message loaded by default
        # '''
        # self.ensure_one()
        # ir_model_data = self.env['ir.model.data']
        # try:
        #     template_id = ir_model_data.get_object_reference('smartest_purchase_request', 'mail_template_request_RFQ')[1]
        #
        # except ValueError:
        #     template_id = False
        # try:
        #     compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        # except ValueError:
        #     compose_form_id = False
        # ctx = dict(self.env.context or {})
        # ctx.update({
        #     'default_model': 'purchase.request',
        #     'active_model': 'purchase.request',
        #     'active_id': self.ids[0],
        #     'default_res_id': self.ids[0],
        #     'default_use_template': bool(template_id),
        #     'default_template_id': template_id,
        #     'default_composition_mode': 'comment',
        #     'custom_layout': "mail.mail_notification_paynow",
        #     'force_email': True,
        #     'mark_rfq_as_sent': True,
        # })
        #
        # # In the case of a RFQ or a PO, we want the "View..." button in line with the state of the
        # # object. Therefore, we pass the model description in the context, in the language in which
        # # the template is rendered.
        # lang = self.env.context.get('lang')
        # if {'default_template_id', 'default_model', 'default_res_id'} <= ctx.keys():
        #     template = self.env['mail.template'].browse(ctx['default_template_id'])
        #     if template and template.lang:
        #         lang = template._render_template(template.lang, ctx['default_model'], ctx['default_res_id'])
        #
        # self = self.with_context(lang=lang)
        # if self.state :
        #     ctx['model_description'] = _('Purchase Request Notification')
        #
        # return {
        #     'name': _('Compose Email'),
        #     'type': 'ir.actions.act_window',
        #     'view_mode': 'form',
        #     'res_model': 'mail.compose.message',
        #     'views': [(compose_form_id, 'form')],
        #     'view_id': compose_form_id,
        #     'target': 'new',
        #     'context': ctx,
        # }

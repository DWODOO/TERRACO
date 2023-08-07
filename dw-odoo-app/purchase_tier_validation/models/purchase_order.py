from odoo.exceptions import UserError

from odoo import _, api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    purchase_request_id = fields.Many2one(
        'purchase.product.request',
        string="Origin Requests",
        readonly=True,
        copy=False,
    )

    purchase_request_count = fields.Integer(
        compute="_compute_line_count"
    )

    validation_state = fields.Selection([
        ('to_approuve', 'A approuvé'),
        ('rejected', 'Rejeté'),
        ('validated', 'Validé')
    ], string='Etat de Validation', compute="_compute_validation_state", store=True)

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

    @api.depends("purchase_request_id")
    def _compute_line_count(self):
        for order in self:
            order.purchase_request_count = len(order.mapped("purchase_request_id"))

    def action_view_purchase_request(self):
        """
        This method is used by the Purchase Request smart button. It opens a form view or a tree view
        :return: Action Dict
        """

        requests = self.mapped('purchase_request_id')
        if not requests:
            raise UserError(
                _('There is no Request to view.')
            )
        tree_view = self.env.ref('smartest_purchase_request.view_purchase_request_tree')
        form_view = self.env.ref('smartest_purchase_request.view_purchase_request_form')
        action = {
            'name': _('Purchase Request(s)'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.request',
            'context': {'default_purchase_order_ids': [(4, self.id)]}
        }
        if len(requests) == 1:
            action['views'] = [(form_view.id, 'form')]
            action['res_id'] = requests.id
            action['view_mode'] = 'form'
        else:
            action['views'] = [(tree_view.id, 'tree'), (form_view.id, 'form')]
            action['domain'] = [('id', 'in', requests.ids)]
        return action


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    purchase_request_line_id = fields.Many2one(
        "purchase.request.line",
        string="Purchase Request Lines",
        readonly=True,
        copy=False,
    )

    @api.onchange('product_id')
    def onchange_product_id(self):
        initial_quantity = self.product_qty
        initial_name = self.name
        super(PurchaseOrderLine, self).onchange_product_id()
        if initial_quantity:
            self.product_qty = initial_quantity
        if initial_name:
            self.name = initial_name

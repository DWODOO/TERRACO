# -*- coding:utf-8 -*-

from odoo import _, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    department_id = fields.Many2one("hr.department", string="Department", related="purchase_request_id.department_id",
                                    store=1)
    activity_user_id = fields.Many2one("res.users", store=1, related="purchase_request_id.requested_by.employee_parent_id.user_id")


class ProductPurchaseRequest(models.Model):
    _inherit = 'purchase.product.request'

    def _get_department_domain(self):
        department_ids = self.env.user.department_ids
        return [('id', 'in', department_ids.ids)]

    department_id = fields.Many2one("hr.department", string="Département concerné", domain=_get_department_domain)
    activity_user_id = fields.Many2one("res.users", store=1, related="requested_by.employee_parent_id.user_id")


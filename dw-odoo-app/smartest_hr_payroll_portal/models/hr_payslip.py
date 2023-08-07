# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SmartestHrPayslip(models.Model):
    _name = 'hr.payslip'
    _inherit = ['hr.payslip', 'portal.mixin']

    def _compute_access_url(self):
        super(SmartestHrPayslip, self)._compute_access_url()
        for payslip in self:
            payslip.access_url = '/my/payslips/%s' % payslip.id

    def _get_report_base_filename(self):
        self.ensure_one()
        return '%s - %s' % (self.employee_id.name, self.number)

    @api.constrains ('order_line')
    def _check_exist_product_in_line(self):
        for order in self:
            products_in_lines = order.mapped('order_line.product_id')
            for product in products_in_lines:
                lines_count = len(order.order_line.filtered(lambda line: line.product_id == product))
                if lines_count > 1:
                    raise ValidationError(_('Product already added.'))
        return True

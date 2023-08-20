from odoo import models,fields,api,_
from odoo.exceptions import ValidationError

class AccountPayment(models.Model):

    _inherit = 'account.payment'








    # def action_view_source_sale_orders(self):
    #     self.ensure_one()
    #     source_orders = self.line_ids.sale_line_ids.order_id
    #     result = self.env['ir.actions.act_window']._for_xml_id('sale.action_orders')
    #     if len(source_orders) > 1:
    #         result['domain'] = [('id', 'in', source_orders.ids)]
    #     elif len(source_orders) == 1:
    #         result['views'] = [(self.env.ref('sale.view_order_form', False).id, 'form')]
    #         result['res_id'] = source_orders.id
    #     else:
    #         result = {'type': 'ir.actions.act_window_close'}
    #     return result
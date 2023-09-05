from datetime import datetime

from odoo import models,fields,api,_,Command


class ResPartner(models.Model):

    _inherit = 'res.partner'

    def price_restourne(self,date_from,date_to):
        cash_id = self.env.ref('account.account_payment_term_immediate').id
        total = sum(self.env['account.move'].search([('partner_id','=',self.id),('move_type','=','out_invoice'),('invoice_date','<',date_to),('invoice_date','>',date_from)]).mapped('amount_total_signed'))
        range_restourne = self.env['sale.restourne']
        if total and self.property_payment_term_id.id != cash_id:
            for range in range_restourne.search([], order='amount_min asc').filtered(
                    lambda p: p.payment_type == "aterm"):
                if total <= range.amount_max:
                    return total * (range.percentage /100)


    @api.model
    def _action_open_wizard_restourne(self):
        """Allow to keep the wizard modal open after executing the action."""
        return {
            'name': _('Data Restourne'),
            'type': 'ir.actions.act_window',
            'res_model': 'restourne.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }









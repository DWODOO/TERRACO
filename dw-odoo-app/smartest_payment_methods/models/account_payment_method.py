from odoo import api, fields, models, _


class AccountPaymentMethod(models.Model):
    _inherit = "account.payment.method"

    @api.model
    def _get_payment_method_information(self):
        res = super(AccountPaymentMethod, self)._get_payment_method_information()
        res['cash.ticket.cash'] = {}
        res['cash.ticket.check'] = {}
        res['cash.ticket.transfer'] = {}
        res['cash.ticket.cash']['mode'] = 'multi'
        res['cash.ticket.check']['mode'] = 'multi'
        res['cash.ticket.transfer']['mode'] = 'multi'
        res['cash.ticket.cash']['domain'] = [('type', 'in', ('bank', 'cash'))]
        res['cash.ticket.check']['domain'] = [('type', 'in', ('bank', 'cash'))]
        res['cash.ticket.transfer']['domain'] = [('type', 'in', ('bank', 'cash'))]
        res['cash.ticket.cash.out'] = res['cash.ticket.check.out']=res['out.cash.ticket.transfer']= {}
        res['cash.ticket.cash.out']['mode'] = res['cash.ticket.check.out']['mode'] =res['out.cash.ticket.transfer']['mode'] = 'multi'
        res['cash.ticket.cash.out']['domain'] = res['cash.ticket.check.out']['domain']= res['out.cash.ticket.transfer']['mode']=[('type', 'in', ('bank', 'cash'))]
        return res

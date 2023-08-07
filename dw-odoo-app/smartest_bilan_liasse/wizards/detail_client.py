from odoo import models,fields,api,_
from datetime import datetime

cnt=10
list1=[]
for i in range(2010,datetime.today().year+1):
         list1.append((str(cnt),str(i)))
         cnt=cnt+1
print(list1)

class printDetailleClient (models.TransientModel):
    _name='detaill.client.wizard'


    # date_id = fields.Date(
    #     'Date'
    # )
    date_year_id = fields.Selection(list1,
                                    required=True, store=True, string="Exercice", tracking=True)

    # date = fields.Datetime()
    # ('move_type', '=', 'out_invoice'),('state', '=', 'posted'),,('invoice_date','=','date')
    @api.model
    def _get_amount_total_invoice(self,partner_id,date_year_id):
        invoice = sum(self.env['account.move'].search(
            [('partner_id', '=', partner_id.id),('move_type', '=', 'out_invoice'),('state', '=', 'posted'),
             ('invoice_date', 'like', date_year_id)
              ]).mapped("amount_untaxed_signed"))
        print(partner_id)
        print(invoice)

        return invoice


    @api.model
    def _get_taxs_total_invoice(self, partner_id,date_year_id):
        invoice = sum(self.env['account.move'].search(
            [('partner_id', '=', partner_id.id), ('move_type', '=', 'out_invoice'), ('state', '=', 'posted'),
             ('invoice_date', 'like',date_year_id)
             ]).mapped("amount_total_signed"))
        taxs = sum(self.env['account.move'].search(
            [('partner_id', '=', partner_id.id), ('move_type', '=', 'out_invoice'), ('state', '=', 'posted'),
             ('invoice_date', 'like', date_year_id)
             ]).mapped("amount_untaxed_signed"))

        total_taxs = round(invoice - taxs,2)

        return total_taxs


    # company_id = fields.Many2one('res.company')
    # print(company_id.name)
    # name_company = fields.Char()
    #
    # def _def_res_company(self):
    #     test_sum = self.env['res.company'].search(
    #         [], limit=1).name
    #
    #     print(test_sum)

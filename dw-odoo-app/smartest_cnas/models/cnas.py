
from odoo import models, fields, api


class SmartestCnas(models.Model):
    _name = 'smartest.cnas'

    name = fields.Char('', required=True)
    # journal_id = fields.Many2one('account.journal', string='Journal Bank', default=lambda self:self.env['account.journal'].search([('name','=','AGB BANQUE')]))
    # journal_id = fields.Many2one('account.journal', string='Journal Bank')
    journal_id = fields.Many2one('account.journal',domain="[('type','=','bank')]", required=True)
    payslips_batches = fields.Many2one('hr.payslip.run', required=True)
    amount = fields.Monetary(currency_field='currency_id',readonly=True)
    # amount = fields.Float('Amount')
    date = fields.Date('Date', required=True, index=True, default=fields.Date.context_today)
    currency_id = fields.Many2one('res.currency', string='Journal Currency')
    # anouar = fields.Char('AnOUAR')

    # bank_account = fields.Many2one('account.account',  default=lambda self:self.env['account.account'].search([('name','=','AGB BANQUE')]))
    bank_account = fields.Many2one('account.account', required=True,domain="[('user_type_id.id','=',3)]")

    status = fields.Selection([
        ('Draft', 'Draft'),
        ('Posted', 'Posted'),
        ('Paid', 'Paid'),
    ], string="Status", default="Draft")



    def validate(self):
        print("hello !!:!!!")
        print("hello !!:!!! -->",self.bank_account)
        self.status = 'Paid'
        xx_account = self.env['account.account'].search([('code', '=', '431000')])

        self.env['account.move'].create({
            'ref': self.name,
            'date': self.date,
            # 'journal_id': self.journal_id,
            'line_ids': [
                (0, 0,
                 {
                    'account_id': xx_account.id,
                    'credit': self.amount,

                }),
                (0, 0,
                 {
                     'account_id': self.bank_account.id,
                     'debit': self.amount,

                 })

            ]        })

    def calculate(self):
        print("hello !!:!!!")
        print("hello !!:!!! -->",self.journal_id)
        self.status = 'Posted'
        xamount = self.amount
        print('user type id ',self.bank_account.user_type_id.id)
        xx = self.env['account.move'].search([('id', '=', self.payslips_batches.move_id.id)])
        # print(" this is account move", xx.line_ids.account_id.code)
        i = 0
        for rec in xx.line_ids:
            if rec.account_id.code == '431020' or rec.account_id.code == '441020':
                print(" this is account move", rec.name, (rec.credit))
                i += rec.credit
                print(" i is ", self.id)
        record_to_update = self.env['smartest.cnas'].browse(self.id)
        if record_to_update.exists():
            record_to_update.write({'amount': i})

        print("this is the amount",xamount)



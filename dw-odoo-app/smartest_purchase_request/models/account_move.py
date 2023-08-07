from datetime import timedelta
from num2words import num2words
import datetime
import time
from odoo import _, api, exceptions, fields, models
from odoo.exceptions import UserError, ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    has_purchase_request = fields.Boolean(string='Purchase Request')
    has_purchase_order = fields.Boolean(string='Purchase Order')
    has_delivery_order = fields.Boolean(string='Delivery Order')
    has_service_fait = fields.Boolean(string='Service Fait')
    has_account_move = fields.Boolean(string='Invoice')
    amount_total_words = fields.Char(compute="_compute_amount_to_words")
    invoice_supplier = fields.Char('Facture Fournisseur')
    convention = fields.Char('Convention')
    convention_start_date = fields.Date('Du')
    convention_end_date = fields.Date('Au')
    payment_mode = fields.Selection([('cheque', 'Cheque'), ('versement', 'Versement'), ('virement', 'Virement')],
                                    string='Mode De Paiement')
    payment_mode_number = fields.Char(string='N°')
    observation = fields.Text('Observation')
    supplier_bank_account = fields.Many2one('res.partner.bank', string='Compte bancaire du fournisseur', domain="[('partner_id','=',partner_id)]")

    @api.depends('amount_total')
    def _compute_amount_to_words(self):
        for rec in self:
            # Initialize variables
            amount_total_words = ''

            if rec:
                # Convert to Float
                flo = float(rec.amount_total)

                # Compute entire
                entire_num = int((str(flo).split('.'))[0])

                # Compute decimals
                decimal_num = int((str(flo).split('.'))[1])
                if decimal_num < 10:
                    decimal_num = decimal_num * 10

                # Build Total text
                amount_total_words = num2words(entire_num, lang='fr')
                amount_total_words += ' Dinars Algériens '
                if decimal_num != 0:
                    amount_total_words += ' et %s %s' % (num2words(decimal_num, lang='fr'), ' Centimes')

            # Populate field
            rec.amount_total_words = amount_total_words.upper()

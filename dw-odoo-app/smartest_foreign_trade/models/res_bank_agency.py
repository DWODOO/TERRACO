# -*- coding: utf-8 -*-
from odoo import models, fields


class BankAgency(models.Model):
    _name = 'res.bank.agency'
    _description = "Bank Agency"
    _order = 'name'

    name = fields.Char(
        'Name',
        required=True,
    )

    bank_id = fields.Many2one(
        'res.bank',
        'Bank',
        required=True, )

    code = fields.Char('Code')
    street = fields.Char()
    street2 = fields.Char()
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')

    email = fields.Char()
    website = fields.Char()
    phone = fields.Char(unaccent=False)
    fax = fields.Char(unaccent=False)

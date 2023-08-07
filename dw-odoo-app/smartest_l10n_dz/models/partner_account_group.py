# -*- coding: utf-8 -*-
from odoo import models, fields


class AccountGroup(models.Model):
    _name = 'partner.account.group'
    _description = "Accounting group for partners"
    _order = 'name'
    _rec_name = 'name'

    name = fields.Char(
        'Name',
    )
    customer_account_id = fields.Many2one(
        'account.account',
        'Customer Account',
    )
    supplier_account_id = fields.Many2one(
        'account.account',
        'Supplier Account',
    )
    affected_partner = fields.Selection(
        [
            ('customer', 'To Customers'),
            ('supplier', 'To Suppliers'),
            ('both', 'To Customers and Suppliers'),
        ],
        # default='customer',
    )

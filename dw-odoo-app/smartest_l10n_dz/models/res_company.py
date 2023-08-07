# -*- coding: utf-8 -*-
from odoo import models, fields


class Company(models.Model):
    _inherit = 'res.company'

    commercial_register = fields.Char(
        'N° Commercial Register'
    )  # This field represents compnay's commercial register number

    fiscal_identification = fields.Char(
        'N° Fiscal Identification'
    )  # This field represents company's fiscal identification number

    taxation = fields.Char(
        'N° Taxation Article'
    )  # This field represents company's taxation article number

    nis = fields.Char(
        'NIS'
    )  # This field represents company's NIS
    use_stamp_tax = fields.Boolean(
        'Use Stamp Duty Tax?'
    )
    stamp_tax_account_id = fields.Many2one(
        'account.account',
        'Account',
    )
    invoice_amount_min = fields.Monetary(
        'Amount Max.',
        currency_field='currency_id',
        default=20,
    )
    stamp_tax_max = fields.Monetary(
        'Tax Amount Max.',
        currency_field='currency_id',
        default=2500,
    )
    stamp_tax_min = fields.Monetary(
        'Tax Amount Min.',
        currency_field='currency_id',
        default=5,
    )
    slice = fields.Monetary(
        'Slice',
        currency_field='currency_id',
        default=100,
    )
    slice_amount = fields.Monetary(
        'Slice Amount',
        currency_field='currency_id',
        default=1,
    )
    company_cnas_ids = fields.One2many(
        'res.company.cnas',
        'company_id',
        'Company CNAS'
    )


class CompanyCnas(models.Model):
    _name = 'res.company.cnas'

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, rec.employer_number))
        return result

    employer_number = fields.Char(
        "Employer Number"
    )
    payer_center = fields.Char(
        'Payer center'
    )
    commercial_register = fields.Char(
        "N° Commercial Register"
    )
    company_id = fields.Many2one(
        'res.company',
        'Company',
        store=True
    )

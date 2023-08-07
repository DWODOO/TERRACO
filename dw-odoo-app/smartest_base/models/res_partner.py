# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _rec_name = 'display_name'

    partner_code = fields.Char(
        'Partner code',
        readonly=False,
        store=True,
        index=True
    )  # This field represent the partner code and it's automatically generated on partner creation according
    # to the partner type (supplier/customer).
    is_supplier = fields.Boolean(
        'Supplier',
    )  # This field is used to indicate if this partner is a supplier instead of using default odoo mechanism
    is_customer = fields.Boolean(
        'Customer',
    )  # This field is used to indicate if this partner is a customer instead of using default odoo mechanism
    commercial_register = fields.Char(
        'N° Commercial Register'
    )  # This field represents partner's commercial register number
    fiscal_identification = fields.Char(
        'N° Fiscal Identification'
    )  # This field represents partner's fiscal identification number
    taxation = fields.Char(
        'N° Taxation Article'
    )  # This field represents partner's taxation article number
    nis = fields.Char(
        'NIS'
    )  # This field represents partner's NIS
    commune_id = fields.Many2one(
        'res.commune',
        string='Commune'
    )
    budget = fields.Float(
        'Budget'
    )
    turnover = fields.Float(
        'Turnover'
    )
    business_capital = fields.Float(
        'Capital'
    )
    start_date = fields.Date(
        'Start Date'
    )
    birthday = fields.Date(
        'Birthday'
    )

    @api.onchange('commune_id')
    def commune_id_change(self):
        for partner in self:
            partner.state_id = partner.commune_id.state_id.id
            partner.city = partner.commune_id.name
            partner.country_id = partner.commune_id.state_id.country_id.id

    @api.depends('partner_code', 'name')
    def _compute_display_name(self):
        for partner in self:
            partner.display_name = partner.partner_code and '[%s] %s' % (partner.partner_code, partner.name) or partner.name

    def name_get(self):
        """
        We override this method in order to display the name of a res.partner record as [CODE] NAME if the record
        has a code value
        :return: list((id, display_name))
        """
        result = []
        partners_names = super(ResPartner, self).name_get()
        for res in partners_names:
            partner_id = self.browse(res[0])
            code = partner_id.partner_code
            name = '[%s] %s' % (code, res[1]) if code else res[1]
            result.append((res[0], name))
        return result

    @api.model
    def create(self, vals):
        """
        Override the create method in order to automatically generate the partner code according to
        it's type (Customer/Supplier).
        :param vals: Dict values of the aimed created partners.
        :return: List of res.partner records.
        """
        use_partner_code = self.env.user.has_group('smartest_base.group_res_partner_code')
        if use_partner_code and not vals.get('partner_code'):
            if vals.get('is_supplier'):
                vals['partner_code'] = self.env.ref('smartest_base.supplier_sequence').next_by_id()
            elif vals.get('is_customer'):
                vals['partner_code'] = self.env.ref('smartest_base.customer_sequence').next_by_id()
        return super(ResPartner, self).create(vals)

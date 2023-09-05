# -*- coding:utf-8 -*-
import pdb
from datetime import datetime

from odoo import fields, models, api, _, Command


class RestourneWizard(models.TransientModel):
    _name = 'restourne.wizard'


    date_from = fields.Date(
        string='From',
        required=True,
    )

    date_to = fields.Date(
        string='To',
        required=True,
    )

    invoice_date = fields.Date(
        string='date of restourne',
        required=True,
        default=fields.datetime.now(),
    )

    def _default_partner_ids(self):
        partner_ids = self.env.context.get('default_partner_ids', []) or self.env.context.get('active_ids', [])
        contact_ids = set()
        for partner in self.env['res.partner'].sudo().browse(partner_ids):
            contact_partners = partner.child_ids.filtered(lambda p: p.type in ('contact', 'other')) | partner
            contact_ids |= set(contact_partners.ids)

        return [Command.link(contact_id) for contact_id in contact_ids]

    partner_ids = fields.Many2many('res.partner', string='Partners', default=_default_partner_ids)

    def create_restourne(self):
        product = self.env.ref('terraco.product_template_restourne')
        restourne_ids = []
        for rec in self.partner_ids:
            order_lines = []
            order_lines.append((0, 0, {
                'product_id': product.id,
                'quantity': 1,
                'product_uom_id': product.uom_id.id,
                'price_unit': rec.price_restourne(self.date_from,self.date_to),
                'account_id': product.categ_id.property_account_income_categ_id.id,
                'tax_ids': False,
            }))
            move_ids = self.env['account.move'].with_context(check_move_validity=False).create({
                'partner_id': rec.id,
                'restourne': True,
                'invoice_date': self.invoice_date,
                'move_type': 'out_refund',
                'journal_id': self.env['account.journal'].search([('type','=','sale')],limit=1).id,
                'invoice_line_ids': order_lines,
            })
            restourne_ids.append(move_ids.id)
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            'name': _('Restournes'),
            "views": [[False, "tree"], [False, "form"]],
            "domain": [["id", "in", restourne_ids]],
        }



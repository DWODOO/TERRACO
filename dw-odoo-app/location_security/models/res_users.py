# -*- coding:utf-8 -*-
from odoo import models, fields, api
from odoo.models import NewId


class ResUsers(models.Model):
    _inherit = 'res.users'

    stock_location_ids = fields.Many2many(
        'stock.location',
        'user_location_rel',
        'user_id',
        'location_id',
        'Locations',
    )  # This field represent the authorized locations per user.
    stock_warehouse_ids = fields.Many2many(
        'stock.warehouse',
        'user_warehouse_rel',
        'user_id',
        'warehouse_id',
        'Warehouses',
    )  # This field represent the authorized warehouses per user.

    restricted_by_warehouse_location_ids = fields.Many2many(
        'stock.location',
        'user_location_restricted_rel',
        'user_id',
        'location_id',
        'Restricted Locations',
        compute="_compute_restricted_by_warehouse_location_ids"
    )  # This field represent the restricted locations caused by the warehouse restriction.

    authorized_location_ids = fields.Many2many(
        'stock.location',
        'user_location_authorized_rel',
        'user_id',
        'location_id',
        'Authorized Locations',
        compute="_compute_authorized_location_ids"
    )  # This field represent the authorized locations. The difference between this field and stock_location_ids field
    # is the stock_location_ids field represent only the authorized locations selected by the user and this field
    # represent an union between stock_location_ids and others authorized location (like view location,
    # customer and vendor locations...)

    def _get_restricted_by_warehouse_locations(self):
        """
        This function retrieve and return all the child locations under the not authorized warehouses
        (warehouse not in stock_warehouse_ids)
        :return: stock.location list
        """
        self.ensure_one()
        restricted_warehouse = self.env['stock.warehouse'].sudo().search([('company_id', 'in', self.env.company.ids)]) - self.sudo().stock_warehouse_ids
        return self.env['stock.location'].sudo().search([]).filtered(
            lambda loc: loc.warehouse_id in restricted_warehouse
        )

    @api.depends('stock_warehouse_ids')
    def _compute_restricted_by_warehouse_location_ids(self):
        """
        Some locations will be restricted by the restriction of their parent warehouse, this method compute those
        locations.
        """
        for user in self:
            if user.has_group('location_security.stock_restriction_group'):
                user.restricted_by_warehouse_location_ids = user._get_restricted_by_warehouse_locations()
            else:
                user.restricted_by_warehouse_location_ids = False

    @api.depends('stock_location_ids', 'stock_warehouse_ids')
    def _compute_authorized_location_ids(self):
        """
        The root user can select the authorized locations for each stock_restriction_group group user. But others
        locations can be also authorized for the user regardless the selected locations by the root user like vendor and
        customer virtual locations.
        """
        for user in self:
            if user.has_group('location_security.stock_restriction_group') and user.id:
                uid = user if not isinstance(user.id, NewId) else self.env['res.users'].browse(user.id.origin)
                user.authorized_location_ids = self.env['stock.location'].with_user(uid).search([('company_id', 'in', self.env.company.ids)])
            else:
                user.authorized_location_ids = self.env['stock.location'].sudo().search([('company_id', 'in', self.env.company.ids)])

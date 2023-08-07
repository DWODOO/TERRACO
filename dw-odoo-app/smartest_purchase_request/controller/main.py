# -*- coding: utf-8 -*-
from odoo import _, fields, http
from odoo.http import request
from odoo.exceptions import AccessError, MissingError
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
import odoo.addons.web.controllers.main


class UserPoValidationPortal(http.Controller):
    # @http.route(["/my/validation/<int:purchase_id>"],type='http', auth="public", website=True)
    # def portal_my_appraisals(self,purchase_id, **kw):
    #     po = request.env['purchase.order'].sudo().search([],order="id")
    #     return request.render('smartest_purchase_request.portal_template_test',{'po':po[purchase_id]})

    @http.route(["/my/validation/<string:purchase_name>"],type='http', auth="user", website=True)
    def portal_my_appraisals(self,purchase_name, **kw):
        if request.httprequest.method == 'GET':
            po = request.env['purchase.order'].sudo().search([('name', '=', purchase_name),('state', 'like', 'technical_validation')], order="id")
            if po:
                return request.render('smartest_purchase_request.portal_template_test',{'po':po})
            else:
                     return request.redirect('/my')

    @http.route(["/validate"], type='http', auth="user", website=True)
    def validate(self, **kw):
        if request.httprequest.method == 'POST':
            id = kw.get('purchase_id')
            # purchase = request.env['purchase.order'].sudo().browse(id).exists()
            # purchase.button_approval()
            # purchase.state = 'quantity_validation'
            po = request.env['purchase.order'].sudo().search([('id', '=', id)], order="id")
            po.button_approval()
            return request.render('smartest_purchase_request.portal_template_thank', {})

    @http.route(["/reject"], type='http', auth="user", website=True)
    def reject(self, **kw):
        if request.httprequest.method == 'POST':
            id = kw.get('purchase_id')
            po = request.env['purchase.order'].sudo().search([('id', '=', id)], order="id")

            # purchase = request.env['purchase.order'].sudo().browse(id).exists()
            # purchase.state = 'cancel'
            po.state = 'cancel'
            return request.render('smartest_purchase_request.portal_template_thank', {})


# -*- coding: utf-8 -*-
# from odoo import http


# class SmartestStock(http.Controller):
#     @http.route('/smartest_stock/smartest_stock/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/smartest_stock/smartest_stock/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('smartest_stock.listing', {
#             'root': '/smartest_stock/smartest_stock',
#             'objects': http.request.env['smartest_stock.smartest_stock'].search([]),
#         })

#     @http.route('/smartest_stock/smartest_stock/objects/<model("smartest_stock.smartest_stock"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('smartest_stock.object', {
#             'object': obj
#         })

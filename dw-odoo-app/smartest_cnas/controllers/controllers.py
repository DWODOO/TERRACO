# -*- coding: utf-8 -*-
# from odoo import http


# class SmartestCnas(http.Controller):
#     @http.route('/smartest_cnas/smartest_cnas/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/smartest_cnas/smartest_cnas/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('smartest_cnas.listing', {
#             'root': '/smartest_cnas/smartest_cnas',
#             'objects': http.request.env['smartest_cnas.smartest_cnas'].search([]),
#         })

#     @http.route('/smartest_cnas/smartest_cnas/objects/<model("smartest_cnas.smartest_cnas"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('smartest_cnas.object', {
#             'object': obj
#         })

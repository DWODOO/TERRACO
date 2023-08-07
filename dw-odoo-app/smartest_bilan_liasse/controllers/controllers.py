# -*- coding: utf-8 -*-
# from odoo import http


# class SmartestCompteResultat(http.Controller):
#     @http.route('/smartest_compte_resultat/smartest_compte_resultat/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/smartest_compte_resultat/smartest_compte_resultat/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('smartest_compte_resultat.listing', {
#             'root': '/smartest_compte_resultat/smartest_compte_resultat',
#             'objects': http.request.env['smartest_compte_resultat.smartest_compte_resultat'].search([]),
#         })

#     @http.route('/smartest_compte_resultat/smartest_compte_resultat/objects/<model("smartest_compte_resultat.smartest_compte_resultat"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('smartest_compte_resultat.object', {
#             'object': obj
#         })

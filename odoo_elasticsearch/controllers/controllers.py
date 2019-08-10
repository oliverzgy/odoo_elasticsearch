# -*- coding: utf-8 -*-
from odoo import http

# class AutosoftSearch(http.Controller):
#     @http.route('/autosoft_search/autosoft_search/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/autosoft_search/autosoft_search/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('autosoft_search.listing', {
#             'root': '/autosoft_search/autosoft_search',
#             'objects': http.request.env['autosoft_search.autosoft_search'].search([]),
#         })

#     @http.route('/autosoft_search/autosoft_search/objects/<model("autosoft_search.autosoft_search"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('autosoft_search.object', {
#             'object': obj
#         })
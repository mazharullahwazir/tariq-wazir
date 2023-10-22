# -*- coding: utf-8 -*-
# from odoo import http


# class WbPosRestrict(http.Controller):
#     @http.route('/wb_pos_restrict/wb_pos_restrict', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/wb_pos_restrict/wb_pos_restrict/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('wb_pos_restrict.listing', {
#             'root': '/wb_pos_restrict/wb_pos_restrict',
#             'objects': http.request.env['wb_pos_restrict.wb_pos_restrict'].search([]),
#         })

#     @http.route('/wb_pos_restrict/wb_pos_restrict/objects/<model("wb_pos_restrict.wb_pos_restrict"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('wb_pos_restrict.object', {
#             'object': obj
#         })

# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from odoo import models, api, _
from reportlab.graphics.barcode import createBarcodeDrawing
from base64 import b64encode
from odoo.exceptions import Warning


class product_label_report_template(models.AbstractModel):
    _name = 'report.dynamic_product_small_label.prod_small_lbl_rpt'
    _description = 'Product Small Label Template'

    def print_product_attributes(self, product, product_dict_value, data):
        field_value = ''
        if list(product_dict_value.values()):
            if list(product_dict_value.values())[0].attribute_ids:
                for attribute in list(product_dict_value.values())[0].attribute_ids:
                    field_value += attribute.attribute_id.name + ': ' + attribute.name + ', '

            elif list(product_dict_value.values())[0].prod_small_wiz_id.attribute_ids:
                for attribute in list(product_dict_value.values())[0].prod_small_wiz_id.attribute_ids:
                    if attribute.id in [attribute.id for attribute in product.product_template_attribute_value_ids]:
                        field_value += attribute.attribute_id.name + ': ' + attribute.name + ', '

            else:
                for attribute in product.product_template_attribute_value_ids:
                    field_value += attribute.attribute_id.name + ': ' + attribute.name + ', '
        return field_value

    def _get_style(self, data):
        return 'height:' + str(data['form']['display_height']) + 'px;width:' + str(data['form']['display_width']) + 'px;'

    def _get_barcode_string(self, product, field_name, type, data):
        encoded_string = ''
        value = product.mapped(field_name)[0]
        if data['form']['with_barcode'] and value and type:
            try:
                encoded_string = createBarcodeDrawing(type, value=value, format='png', width=int(data['form']['barcode_height']),
                                                             height=int(data['form']['barcode_width']),
                                                             humanReadable=data['form']['humanReadable'])
            except Exception:
                return False
            encoded_string = b64encode(encoded_string.asString('png'))
        return encoded_string

    def _get_barcode_data(self, data):
        product_list = []
        model = ''
        if self._context.get('active_model') == 'sale.order':
            model = 'sale.order.line'
        elif self._context.get('active_model') == 'purchase.order':
            model = 'purchase.order.line'
        elif self._context.get('active_model') == 'stock.picking':
            model = 'stock.move'
        elif self._context.get('active_model') == 'account.invoice':
            model = 'account.invoice.line'
        elif self._context.get('active_model') == 'stock.production.lot':
            model = 'stock.production.lot'
        product_ids = self.env['product.small.label.qty'].search([('id', 'in', data['form']['product_ids'])])
        skip_products = []
        for product_line in product_ids:
            if product_line.line_id:
                line_brw = self.env[model].browse(product_line.line_id)
                for qty in range(product_line.qty):
                    product_list.append({line_brw : product_line})
            else:
                for qty in range(product_line.qty):
                    product_list.append({product_line.product_id: product_line})
        return product_list

    def _get_price(self, product, pricelist_id=None):
        price = 0
        if product:
            price = product.list_price
            if pricelist_id:
                price = pricelist_id.price_get(product.id, 1.0)
                if price and isinstance(price, dict):
                    price = price.get(pricelist_id.id)
        return price

    @api.model
    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name('dynamic_product_small_label.prod_small_lbl_rpt')
        return {
            'doc_ids': self.env["wizard.product.small.label.report"].browse(data["ids"]),
            'doc_model': "wizard.product.small.label.report",
            'docs': self,
            'get_barcode_data': self._get_barcode_data,
            'get_barcode_string': self._get_barcode_string,
            'get_price': self._get_price,
            'get_style' : self._get_style,
            'print_product_attributes': self.print_product_attributes,
            'data': data
        }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

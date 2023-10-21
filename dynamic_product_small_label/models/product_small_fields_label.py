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

from base64 import b64encode
from reportlab.graphics import barcode

from odoo import api, models
from odoo.exceptions import Warning


class product_small_fields_label(models.AbstractModel):
    _name = 'report.dynamic_product_small_label.product_small_fields_label'
    _description = 'Dynamic Product Fields Label Template Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name(
            'dynamic_product_small_label.product_small_fields_label')
        return {
            'doc_ids': self.env["wizard.product.small.label.report"].browse(data["ids"]),
            'doc_model': report.model,
            'docs': self,
            'get_label_data': self._get_label_data,
            'draw_style': self._draw_style,
            'get_barcode_string': self._get_barcode_string,
            'get_record_set': self.get_record_set,
            'get_style': self._get_style,
            'get_span_style': self.get_span_style,
            'get_align': self.get_align,
            'get_logo_style': self._get_logo_style,
            'get_price': self._get_price,
            'data': data
        }

    def _get_logo_style(self, form):
        logo_style = ''
        if form['logo_width']:
            logo_style += 'max-width:' + str(form['logo_width']) + "px;"
        if form['logo_height']:
            logo_style += 'max-height:' + str(form['logo_height']) + "px;"
        return logo_style

    def _get_label_data(self, form):
        line_ids = []
        for product in self.env['product.small.label.qty'].browse(form['product_ids']):
            for no in range(0, product.qty):
                line_ids.append(product.id)
        return line_ids

    def get_record_set(self, fields):
        field_line_obj = self.env['aces.product.field.line'].browse(fields)
        return field_line_obj

    def _get_style(self, data):
        return 'height:' + str(data['form']['display_height']) + 'px;width:' + str(
            data['form']['display_width']) + 'px;'

    def get_align(self, field_line):
        return str(field_line.field_align)

    def _get_barcode_string(self, ean13, data):
        barcode_str = ''
        if data['form']['with_barcode'] and ean13 and type:
            try:
                barcode_str = barcode.createBarcodeDrawing(
                    data['form']['barcode_type'], value=ean13, format='png',
                    width=data['form']['barcode_width'],
                    height=data['form']['barcode_height'],
                    humanReadable=data['form']['humanReadable'])
                barcode_str = b64encode(barcode_str.asString('png'))
                return barcode_str
            except Exception as e:
                return barcode_str or ''

    def get_span_style(self, field_line):
        style = ''
        if field_line.font_size:
            style += 'font-size:%s !important;' % (str(field_line.font_size) + 'px')
        if field_line.font_color:
            style += 'color:%s !important;' % (str(field_line.font_color))
        if field_line.field_width:
            style += 'width:%s !important;' % (str(field_line.field_width) + '%')
        if field_line.field_border:
            style += 'border:%s !important;' % (str(field_line.field_border) + 'px' + ' solid' + ' black')
        if field_line.font_weight:
            style += 'font-weight:%s !important;' % (str(field_line.font_weight))
        if field_line.margin_value:
            margin_value = field_line.margin_value.split(',')
            style += '''margin-top:%s !important;margin-right:%s !important;margin-bottom:%s !important;margin-left:%s !important;''' % \
                     ((margin_value[0] + '%' or str(0) + '%'), (margin_value[1] + '%' or str(0) + '%'),
                      (margin_value[2] + '%' or str(0) + '%'), (margin_value[3] + '%' or str(0) + '%'))
        return style

    def _draw_style(self, field_line, product_id, data):
        currency_symbol = ''
        if data['form']['currency_id']:
            currency_symbol = self.env['res.currency'].browse(data['form']['currency_id'][0]).symbol

        field_value = ''
        if field_line.field_id.ttype not in ('many2many', 'one2many', 'many2one'):
            if data['form']['with_barcode']:
                if field_line.field_id.name != data['form']['barcode_field']:
                    field_value = product_id.product_id.mapped(field_line.field_id.name)[0]
                elif field_line.field_id.name == data['form']['barcode_field']:
                    if product_id.product_id.mapped(field_line.field_id.name)[0]:
                        field_value = self._get_barcode_string(
                            product_id.product_id.mapped(field_line.field_id.name)[0], data)
            else:
                field_value = product_id.product_id.mapped(field_line.field_id.name)[0]

        if field_line.field_id.name == 'product_template_attribute_value_ids':
            if product_id.attribute_ids:
                for attribute in product_id.attribute_ids:
                    field_value += attribute.attribute_id.name + ': ' + attribute.name + ', '
            elif product_id.prod_small_wiz_id.attribute_ids:
                for attribute in product_id.prod_small_wiz_id.attribute_ids:
                    if attribute.id in [attribute.id for attribute in
                                        product_id.product_id.product_template_attribute_value_ids]:
                        field_value += attribute.attribute_id.name + ': ' + attribute.name + ', '
            else:
                for attribute in product_id.product_id.product_template_attribute_value_ids:
                    field_value += attribute.attribute_id.name + ': ' + attribute.name + ', '

        if field_line.field_id.name == 'categ_id':
            if product_id.product_id.categ_id:
                field_value = product_id.product_id.categ_id.display_name

        if field_line.field_id.name == 'uom_id':
            if product_id.product_id.uom_id:
                field_value += 'UOM: ' + product_id.product_id.uom_id.name

        if field_line.with_currency:
            if data['form']['pricelist_id']:
                pricelist_id = self.env['product.pricelist'].browse([data['form']['pricelist_id'][0]])
                field_value = pricelist_id.price_get(product_id.product_id.id, 1.0)
                field_value = field_value.get(pricelist_id.id)
            if data['form']['currency_position'] == 'after':
                field_value = str(field_value) + ' ' + currency_symbol
            if data['form']['currency_position'] == 'before':
                field_value = currency_symbol + ' ' + str(field_value)
        return field_value

    def _get_price(self, product, pricelist_id=None):
        price = 0
        if product:
            price = product.list_price
            if pricelist_id:
                price = pricelist_id.price_get(product.id, 1.0)
                if price and isinstance(price, dict):
                    price = price.get(pricelist_id.id)
        return price

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

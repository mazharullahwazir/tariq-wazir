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

from odoo import fields, models, api, _
import base64
from odoo.exceptions import Warning, UserError
import logging

_logger = logging.getLogger(__name__)
try:
    from wand.image import Image as Img
except ImportError:
    _logger.error('Cannot `import wand`.')
import os, glob
import os.path
from base64 import b64encode
from reportlab.graphics import barcode


class product_small_label_design(models.Model):
    _name = 'product.small.label.design'
    _description = 'Product Small Label Design'

    def _get_currency(self):
        return self.env['res.users'].browse([self._uid]).company_id.currency_id

    @api.model
    def default_get(self, fields_list):
        res = super(product_small_label_design, self).default_get(fields_list)
        if self._context.get('wiz_id') and self._context.get('from_wizard'):
            for wiz in self.env['wizard.product.small.label.report'].browse(self._context.get('wiz_id')):
                prod_list = []
                for field_line in wiz.product_field_lines:
                    prod_list.append((0, 0, {
                        'font_size': field_line.font_size,
                        'font_color': field_line.font_color,
                        'field_align': field_line.field_align,
                        'field_border': field_line.field_border,
                        'font_weight': field_line.font_weight,
                        'sequence': field_line.sequence,
                        'field_id': field_line.field_id.id,
                        'field_width': field_line.field_width,
                        'margin_value': field_line.margin_value,
                        'with_currency': field_line.with_currency,
                    }))
                res.update({
                    'template_label_design': wiz.report_design,
                    'report_model': wiz.report_model,
                    'label_width': wiz.label_width,
                    'label_height': wiz.label_height,
                    'dpi': wiz.dpi,
                    'margin_top': wiz.margin_top,
                    'margin_left': wiz.margin_left,
                    'margin_bottom': wiz.margin_bottom,
                    'margin_right': wiz.margin_right,
                    'humanReadable': wiz.humanReadable,
                    'barcode_height': wiz.barcode_height,
                    'barcode_width': wiz.barcode_width,
                    'display_height': wiz.display_height,
                    'display_width': wiz.display_width,
                    'with_barcode': wiz.with_barcode,
                    'label_logo': wiz.label_logo,
                    'product_field_lines': prod_list,
                    'barcode_type': wiz.barcode_type,
                    'currency_id': wiz.currency_id and wiz.currency_id.id,
                    'currency_position': wiz.currency_position,
                    'design_using': wiz.design_using,
                    'logo_position': wiz.logo_position,
                    'logo_height': wiz.logo_height,
                    'logo_width': wiz.logo_width,
                    'barcode_field': wiz.barcode_field
                })
        return res

    name = fields.Char(string="Design Name")
    report_model = fields.Char(string='Model')
    template_label_design = fields.Text(string="Template Design")
    # label
    label_width = fields.Integer(string='Label Width (mm)', default=43, required=True)
    label_height = fields.Integer(string='Label Height (mm)', default=30, required=True)
    dpi = fields.Integer(string='DPI', default=80, help="The number of individual dots\
                                that can be placed in a line within the span of 1 inch (2.54 cm)")
    margin_top = fields.Integer(string='Margin Top (mm)', default=4)
    margin_left = fields.Integer(string='Margin Left (mm)', default=1)
    margin_bottom = fields.Integer(string='Margin Bottom (mm)', default=1)
    margin_right = fields.Integer(string='Margin Right (mm)', default=1)
    # barcode
    humanReadable = fields.Boolean(string="HumanReadable", help="User wants to print barcode number\
                                    with barcode label.")
    barcode_height = fields.Integer(string="Height", default=300, required=True, help="This height will\
                                    required for the clearity of the barcode.")
    barcode_width = fields.Integer(string="Width", default=1500, required=True, help="This width will \
                                    required for the clearity of the barcode.")
    display_height = fields.Integer(string="Display Height (px)", required=True, default=30,
                                    help="This height will required for display barcode in label.")
    display_width = fields.Integer(string="Display Width (px)", required=True, default=120,
                                   help="This width will required for display barcode in label.")
    with_barcode = fields.Boolean(string='Barcode', help="Click this check box if user want to print\
                                    barcode for Product Label.", default=True)
    active = fields.Boolean(string="Active", default=True)
    pricelist_id = fields.Many2one('product.pricelist', string="Pricelist")
    label_logo = fields.Binary(string="Label Logo")
    design_using = fields.Selection([('fields_selection', 'Fields Selection'),
                                     ('xml_design', 'XML Design')],
                                    default='xml_design')
    product_field_lines = fields.One2many('aces.design.field.line', 'design_id', string="Product Fields")
    barcode_type = fields.Selection([('Codabar', 'Codabar'), ('Code11', 'Code11'),
                                     ('Code128', 'Code128'), ('EAN13', 'EAN13'),
                                     ('Extended39', 'Extended39'), ('EAN8', 'EAN8'),
                                     ('Extended93', 'Extended93'), ('USPS_4State', 'USPS_4State'),
                                     ('I2of5', 'I2of5'), ('UPCA', 'UPCA'),
                                     ('QR', 'QR')], string="Barcode Type")
    currency_id = fields.Many2one('res.currency', string="Currency", default=_get_currency)
    currency_position = fields.Selection([('before', 'Before'),
                                          ('after', 'After')], string="Currency Position", default="before")
    logo_position = fields.Selection([('top', 'Top'), ('bottom', 'Bottom')], string="Logo Position")
    logo_height = fields.Integer(string="Logo Height(px)")
    logo_width = fields.Integer(string="Logo width(px)")
    barcode_field = fields.Selection([('barcode', 'Barcode'), ('default_code', 'Internal Reference')],
                                     string="Barcode Field", default="barcode")

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if self._context.get('from_wizard') and self._context.get('report_model'):
            args.append(('report_model', '=', self._context.get('report_model')))
        elif self._context.get('from_wizard') and not self._context.get('report_model'):
            args.append(('report_model', '=', False))
        return super(product_small_label_design, self).name_search(name, args=args, operator=operator, limit=limit)

    def close_wizard(self):
        self.write({'active': False})
        return {
            'name': _('Print Product Label'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'wizard.product.small.label.report',
            'target': 'new',
            'res_id': self._context.get('wiz_id'),
            'context': self.env.context
        }

    def go_to_label_wizard(self):
        if not self.name:
            raise Warning(_('Label Design Name is required.'))
        return {
            'name': _('Product Label'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'wizard.product.small.label.report',
            'target': 'new',
            'res_id': self._context.get('wiz_id'),
            'context': self.env.context
        }


class aces_design_field_line(models.Model):
    _name = 'aces.design.field.line'
    _description = 'Design Field Lines'

    font_size = fields.Integer(string="Font Size", default=10)
    font_color = fields.Selection([('black', 'Black'), ('blue', 'Blue'),
                                   ('cyan', 'Cyan'), ('gray', 'Gray'),
                                   ('green', 'Green'), ('lime', 'Lime'),
                                   ('maroon', 'Maroon'), ('pink', 'Pink'),
                                   ('purple', 'Purple'), ('red', 'Red'),
                                   ('yellow', 'Yellow')], string="Font Color", default='black')
    sequence = fields.Integer(string="Sequence")
    field_id = fields.Many2one('ir.model.fields', string="Fields Name")
    design_id = fields.Many2one('product.small.label.design', string="Barcode Label ID")
    field_width = fields.Float(string="Field Width(%)", default=100.00)
    margin_value = fields.Char(string="Field Margin(%)(T,R,B,L)", default='0,0,0,0',
                               help="Field Margin(%)T(Top),R(Right),B(Bottom),L(Left)")
    with_currency = fields.Boolean(string="With Currency")
    field_align = fields.Selection([('center', 'Center'), ('right', 'Right'), ('left', 'Left')],
                                   string="Align", default='center')
    font_weight = fields.Selection([('normal', 'Normal'), ('bold', 'Bold')],
                                   string="Font Weight", default='normal')
    field_border = fields.Integer(string="Border")


class wizard_product_small_label_report(models.TransientModel):
    _name = "wizard.product.small.label.report"
    _description = 'Wizard Product Small Label Report'

    @api.model
    def default_get(self, fields_list):
        prod_list = []
        product_list_dict = []
        res = super(wizard_product_small_label_report, self).default_get(fields_list)
        if self._context.get('active_ids') and self._context.get('active_model') == 'purchase.order':
            for line in self.env['purchase.order.line'].search([('order_id', 'in', self._context.get('active_ids'))]):
                if line.product_id and line.product_qty:
                    product_list_dict.append(
                        {'product_id': line.product_id.id, 'qty': line.product_qty, 'line_id': line.id})
        elif self._context.get('active_ids') and self._context.get('active_model') == 'sale.order':
            for line in self.env['sale.order.line'].search([('order_id', 'in', self._context.get('active_ids'))]):
                if line.product_id and line.product_uom_qty:
                    product_list_dict.append(
                        {'product_id': line.product_id.id, 'qty': line.product_uom_qty, 'line_id': line.id})
        elif self._context.get('active_ids') and self._context.get('active_model') == 'stock.picking':
            for line in self.env['stock.move'].search([('picking_id', 'in', self._context.get('active_ids'))]):
                if line.product_id and line.product_qty:
                    product_list_dict.append(
                        {'product_id': line.product_id.id, 'qty': line.product_qty, 'line_id': line.id})
        elif self._context.get('active_ids') and self._context.get('active_model') == 'account.invoice':
            for line in self.env['account.invoice.line'].search(
                    [('invoice_id', 'in', self._context.get('active_ids'))]):
                if line.product_id and line.quantity:
                    product_list_dict.append(
                        {'product_id': line.product_id.id, 'qty': line.quantity, 'line_id': line.id})
        elif self._context.get('active_ids') and self._context.get('active_model') == 'product.product':
            for each_product in self.env['product.product'].browse(self._context.get('active_ids')):
                product_list_dict.append({'product_id': each_product.id, 'qty': 1})
        elif self._context.get('active_ids') and self._context.get('active_model') == 'stock.production.lot':
            for each_lot in self.env['stock.production.lot'].browse(self._context.get('active_ids')):
                product_list_dict.append(
                    {'product_id': each_lot.product_id.id, 'qty': each_lot.product_qty, 'line_id': each_lot.id})
        for each_dict in product_list_dict:
            prod_list.append((0, 0, {'product_id': each_dict.get('product_id'),
                                     'qty': each_dict.get('qty'),
                                     'line_id': each_dict.get('line_id'),
                                     'attribute_ids': [(6, 0, [])]}))
        if self._context.get('active_model'):
            res['report_model'] = self._context.get('active_model')
            design_id = self.env['product.small.label.design'].search(
                [('report_model', '=', self._context.get('active_model'))], limit=1)
            if design_id:
                res['design_id'] = design_id.id
        else:
            res['report_model'] = 'wizard.product.small.label.report'
            design_id = self.env['product.small.label.design'].search(
                [('report_model', '=', 'wizard.product.small.label.report')], limit=1)
            if design_id:
                res['design_id'] = design_id.id
        res['product_ids'] = prod_list
        return res

    @api.model
    def _get_report_design(self):
        view_id = self.env['ir.ui.view'].search([('name', '=', 'prod_small_lbl_rpt')])
        if view_id.arch:
            return view_id.arch

    @api.model
    def _get_report_id(self):
        view_id = self.env['ir.ui.view'].search([('name', '=', 'prod_small_lbl_rpt')])
        if not view_id:
            raise Warning('Someone has deleted the reference view of report.\
                Please Update the module!')
        return view_id.id

    @api.model
    def _get_report_paperformat_id(self):
        xml_id = self.env['ir.actions.report'].search([('report_name', '=',
                                                        'dynamic_product_small_label.prod_small_lbl_rpt')])
        if not xml_id or not xml_id.paperformat_id:
            raise Warning('Someone has deleted the reference paperformat of report.Please Update the module!')
        return xml_id.paperformat_id.id

    def _get_currency(self):
        return self.env['res.users'].browse([self._uid]).company_id.currency_id

    report_model = fields.Char(string='Model')
    design_id = fields.Many2one('product.small.label.design', string="Template")
    product_ids = fields.One2many('product.small.label.qty', 'prod_small_wiz_id', string='Product List')
    label_width = fields.Integer(string='Label Width (mm)', default=43, required=True)
    label_height = fields.Integer(string='Label Height (mm)', default=30, required=True)
    dpi = fields.Integer(string='DPI', default=80, help="The number of individual dots \
                        that can be placed in a line within the span of 1 inch (2.54 cm)")
    margin_top = fields.Integer(string='Margin Top (mm)', default=4)
    margin_left = fields.Integer(string='Margin Left (mm)', default=1)
    margin_bottom = fields.Integer(string='Margin Bottom (mm)', default=1)
    margin_right = fields.Integer(string='Margin Right (mm)', default=1)
    # barcode input
    humanReadable = fields.Boolean(string="HumanReadable", help="User wants to print barcode number \
                                    with barcode label.")
    barcode_height = fields.Integer(string="Height", default=300, required=True,
                                    help="This height will required for the clearity of the barcode.")
    barcode_width = fields.Integer(string="Width", default=1500, required=True,
                                   help="This width will required for the clearity of the barcode.")
    display_height = fields.Integer(string="Display Height (px)", required=True, default=30,
                                    help="This height will required for display barcode in label.")
    display_width = fields.Integer(string="Display Width (px)", required=True, default=120,
                                   help="This width will required for display barcode in label.")
    # report design
    report_design = fields.Text(string="Report Design", default=_get_report_design, required=True)
    view_id = fields.Many2one('ir.ui.view', string='Report View', default=_get_report_id)
    paper_format_id = fields.Many2one('report.paperformat', string="Paper Format", default=_get_report_paperformat_id)
    with_barcode = fields.Boolean(string='Barcode', help="Click this check box if user want to\
                        print barcode for Product Label.", default=True)
    pricelist_id = fields.Many2one('product.pricelist', string="Pricelist")
    make_update_existing = fields.Boolean(string="Update Existing Template")
    label_logo = fields.Binary(string="Label Logo")
    design_using = fields.Selection([('fields_selection', 'Fields Selection'),
                                     ('xml_design', 'XML Design')],
                                    default='xml_design')
    product_field_lines = fields.One2many('aces.product.field.line', 'wizard_id', string="Product Fields")
    barcode_type = fields.Selection([('Codabar', 'Codabar'), ('Code11', 'Code11'),
                                     ('Code128', 'Code128'), ('EAN13', 'EAN13'),
                                     ('Extended39', 'Extended39'), ('EAN8', 'EAN8'),
                                     ('Extended93', 'Extended93'), ('USPS_4State', 'USPS_4State'),
                                     ('I2of5', 'I2of5'), ('UPCA', 'UPCA'),
                                     ('QR', 'QR')], string="Barcode Type")
    currency_id = fields.Many2one('res.currency', string="Currency", default=_get_currency)
    currency_position = fields.Selection([('before', 'Before'),
                                          ('after', 'After')], string="Currency Position", default="before")
    logo_position = fields.Selection([('top', 'Top'), ('bottom', 'Bottom')], string="Logo Position")
    logo_height = fields.Integer(string="Logo Height(px)")
    logo_width = fields.Integer(string="Logo width(px)")
    barcode_field = fields.Selection([('barcode', 'Barcode'), ('default_code', 'Internal Reference')],
                                     string="Barcode Field", default="barcode")
    attribute_ids = fields.Many2many('product.attribute.value', 'wizard_product_attribute_value_table',
                                     'wizard_product_id', 'attribute_id', string="Product Attributes")

    @api.onchange('design_id')
    def on_change_design_id(self):
        prod_list = []
        if self.design_id:
            for field_line in self.design_id.product_field_lines:
                prod_list.append((0, 0, {
                    'font_size': field_line.font_size,
                    'font_color': field_line.font_color,
                    'field_align': field_line.field_align,
                    'field_border': field_line.field_border,
                    'font_weight': field_line.font_weight,
                    'sequence': field_line.sequence,
                    'field_id': field_line.field_id.id,
                    'field_width': field_line.field_width,
                    'margin_value': field_line.margin_value,
                    'with_currency': field_line.with_currency
                }))

            self.report_design = self.design_id.template_label_design
            self.report_model = self.design_id.report_model
            # label format args
            self.label_width = self.design_id.label_width
            self.label_height = self.design_id.label_height
            self.dpi = self.design_id.dpi
            self.margin_top = self.design_id.margin_top
            self.margin_left = self.design_id.margin_left
            self.margin_bottom = self.design_id.margin_bottom
            self.margin_right = self.design_id.margin_right
            # barcode args
            self.with_barcode = self.design_id.with_barcode
            self.barcode_height = self.design_id.barcode_height
            self.barcode_width = self.design_id.barcode_width
            self.humanReadable = self.design_id.humanReadable
            self.display_height = self.design_id.display_height
            self.display_width = self.design_id.display_width
            self.label_logo = self.design_id.label_logo
            self.design_using = self.design_id.design_using
            self.product_field_lines = prod_list
            self.barcode_type = self.design_id.barcode_type
            self.currency_id = self.design_id.currency_id and self.design_id.currency_id.id
            self.currency_position = self.design_id.currency_position
            self.logo_position = self.design_id.logo_position
            self.logo_height = self.design_id.logo_height
            self.logo_width = self.design_id.logo_width
            self.barcode_field = self.design_id.barcode_field

    def save_design(self):
        if not self.make_update_existing:
            view_id = self.env['ir.model.data'].get_object_reference('dynamic_product_small_label',
                                                                     'wizard_product_small_label_design_form_view')[1]
            ctx = dict(self.env.context)
            ctx.update({'wiz_id': self.id})
            return {
                'name': _('Product Small Label Design'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'product.small.label.design',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'view_id': view_id,
                'context': ctx,
                'nodestroy': True
            }
        else:
            if self.design_id:
                prod_list = []
                for field_line in self.product_field_lines:
                    prod_list.append((0, 0, {
                        'font_size': field_line.font_size,
                        'font_color': field_line.font_color,
                        'field_align': field_line.field_align,
                        'field_border': field_line.field_border,
                        'font_weight': field_line.font_weight,
                        'sequence': field_line.sequence,
                        'field_id': field_line.field_id.id,
                        'field_width': field_line.field_width,
                        'margin_value': field_line.margin_value,
                        'with_currency': field_line.with_currency
                    }))
                self.design_id.product_field_lines = False
                self.design_id.write({
                    'template_label_design': self.report_design,
                    'report_model': self.report_model,
                    'label_width': self.label_width,
                    'label_height': self.label_height,
                    'dpi': self.dpi,
                    'margin_top': self.margin_top,
                    'margin_left': self.margin_left,
                    'margin_bottom': self.margin_bottom,
                    'margin_right': self.margin_right,
                    'humanReadable': self.humanReadable,
                    'barcode_height': self.barcode_height,
                    'barcode_width': self.barcode_width,
                    'display_height': self.display_height,
                    'display_width': self.display_width,
                    'with_barcode': self.with_barcode,
                    'label_logo': self.label_logo,
                    'design_using': self.design_using,
                    'product_field_lines': prod_list,
                    'barcode_type': self.barcode_type,
                    'currency_id': self.currency_id and self.currency_id.id,
                    'currency_position': self.currency_position,
                    'logo_position': self.logo_position,
                    'logo_width': self.logo_width,
                    'logo_height': self.logo_height,
                    'barcode_field': self.barcode_field
                })
                return {
                    'name': _('Product Label'),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'wizard.product.small.label.report',
                    'target': 'new',
                    'res_id': self.id,
                    'context': self.env.context
                }

    @api.onchange('dpi')
    def onchange_dpi(self):
        if self.dpi < 80:
            self.dpi = 80

    def _get_barcode_string(self, ean13, data):
        barcode_str = barcode.createBarcodeDrawing(
            data['form']['barcode_type'], value=ean13, format='png',
            width=data['form']['barcode_width'],
            height=data['form']['barcode_height'],
            humanReadable=data['form']['humanReadable'])
        barcode_str = b64encode(barcode_str.asString('png'))
        return barcode_str

    def action_print(self):
        if not self.product_ids:
            raise UserError('Select any product first.!')
        for product in self.product_ids:
            if product.qty <= 0:
                raise UserError('%s product label qty should be greater then 0.!'
                                % (product.product_id.name))
        if (self.label_height <= 0) or (self.label_width <= 0):
            raise UserError(_('You can not give label width and label height to less then zero(0).'))
        if (self.margin_top < 0) or (self.margin_left < 0) or \
                (self.margin_bottom < 0) or (self.margin_right < 0):
            raise UserError('Margin Value(s) for report can not be negative!')
        if self.with_barcode and (self.barcode_height <= 0 or self.barcode_width <= 0 or
                                  self.display_height <= 0 or self.display_width <= 0):
            raise UserError('Give proper barcode height and width value(s) for display')
        data = self.read()[0]
        data.update({'label_preview': False})
        datas = {
            'ids': self._ids,
            'model': 'wizard.product.small.label.report',
            'form': data
        }
        if self.view_id and self.report_design:
            self.view_id.sudo().write({'arch': self.report_design})
        self._set_paper_format_id()
        if self.design_using == 'xml_design':
            if self.with_barcode:
                skip_products = self.check_skip_products()
                if skip_products:
                    for p in skip_products:
                        datas['form']['product_ids'].remove(p.id)
                    if not datas['form']['product_ids']:
                        raise UserError(
                            _('Selected products does not contain proper barcode number which match with select barcode type.'))
            return self.env.ref('dynamic_product_small_label.dynamic_product_small_label_report').report_action(self,
                                                                                                                data=datas)

        if self.design_using == 'fields_selection':
            if not self.product_field_lines:
                raise UserError(_('Select Fields to print into label.'))
            sequence = False
            fields_list = []
            l = []
            count = len(self.product_field_lines)
            for field in sorted(self.product_field_lines, key=lambda v: v.sequence, reverse=False):
                if self.barcode_field == field.field_id.name:
                    if not self.barcode_type:
                        raise UserError(_("Select barcode type to print barcode from Barcode tab."))
                    if field.with_currency:
                        raise UserError(_("Barcode will not print with Currency."))

                if field.margin_value:
                    if len(field.margin_value.split(',')) != 4:
                        raise UserError(_('Please enter margin value with Top,Right,Bottom,Left margin parameters.'))

                if sequence and sequence == field.sequence:
                    raise UserError(_("Sequence cannot repeated."))
                    # l.append(field.id)
                if not sequence:
                    l.append(field.id)
                if sequence and sequence != field.sequence:
                    fields_list.append(l)
                    l = []
                    l.append(field.id)
                sequence = field.sequence
                if count == 1:
                    fields_list.append(l)
                count -= 1

            if self.label_logo and not self.logo_position:
                raise UserError(_('Define logo position properly into label tab.'))

            datas.update({'fields_list': fields_list})

            if self.with_barcode and not self.product_field_lines.filtered(
                    lambda f: f.field_id.name == self.barcode_field):
                if self.barcode_field == 'barcode':
                    field_name = 'Barcode'
                if self.barcode_field == 'default_code':
                    field_name = 'Internal Reference'
                raise UserError(
                    _('Field from product table %s is not selected which you are tring to print as barcode...!' % (
                        field_name)))

            if self.with_barcode and self.product_field_lines.filtered(lambda f: f.field_id.name == self.barcode_field):
                skip_products = self.check_skip_products()
                if skip_products:
                    for p in skip_products:
                        datas['form']['product_ids'].remove(p.id)
                    if not datas['form']['product_ids']:
                        raise UserError(
                            _('Selected products does not contain proper barcode number which match with select barcode type.'))
            return self.env.ref('dynamic_product_small_label.product_small_fields_label_report').report_action(self,
                                                                                                               data=datas)

    def _get_barcode_string(self, ean13):
        try:
            barcode_str = barcode.createBarcodeDrawing(
                self.barcode_type, value=ean13, format='png', width=self.barcode_width, height=self.barcode_height,
                humanReadable=self.humanReadable)
            barcode_str = b64encode(barcode_str.asString('png'))
            return barcode_str
        except Exception as e:
            pass

    def check_skip_products(self):
        skip_products = []
        field_line_id = False
        if self.with_barcode and self.barcode_type and self.barcode_field:
            for product_line in self.product_ids:
                if product_line.product_id.mapped(self.barcode_field)[0]:
                    result = self._get_barcode_string(product_line.product_id.mapped(self.barcode_field)[0])
                    if not result:
                        skip_products.append(product_line)
                else:
                    skip_products.append(product_line)
        if skip_products:
            group_id = self.env.ref('stock.group_stock_manager')
            if group_id and group_id.users:
                subtype_id = self.env.ref('mail.mt_note')
                body = """Hello, This is list of products which are skipped during product label printing."""
                body += """<table style="border:1px solid black;padding:5px;cell-spacing:5px;">
                                <tr>
                                    <td style="border:1px solid black;padding:5px;cell-spacing:5px;"><b>Product Name</b></td>
                                    <td style="border:1px solid black;padding:5px;cell-spacing:5px;"><b>Qty</b></td>
                                </tr>"""

                for prod in skip_products:
                    body += """<tr>
                                    <td style="border:1px solid black;padding:5px;cell-spacing:5px;">%s</td>
                                    <td style="border:1px solid black;padding:5px;cell-spacing:5px;">%s</td>
                                </tr>""" % (prod.product_id.name, prod.qty)
                body += """</table>"""
                values = {
                    'author_id': self.env.user.partner_id.id,
                    'body': body,
                    'subject': "Dynamic Small Label module",
                    'message_type': 'notification',
                    'subtype_id': subtype_id.id,
                    'partner_ids': [(4, user.partner_id.id) for user in group_id.users],
                    # 'needaction_partner_ids': [(4, user.partner_id.id) for user in group_id.users],
                    'model': '',
                }
                new_message = self.env['mail.message'].create(values)
                self.env['mail.thread']._message_post_after_hook(new_message, values)
                # self.env['mail.thread']._message_post_after_hook(new_message, values, model_description=self._name)
        return skip_products

    def _set_paper_format_id(self):
        if self.paper_format_id:
            result = self.paper_format_id.sudo().write({
                'format': 'custom',
                'page_width': self.label_width,
                'page_height': self.label_height,
                'margin_top': self.margin_top,
                'margin_left': self.margin_left,
                'margin_bottom': self.margin_bottom,
                'margin_right': self.margin_right,
                'dpi': self.dpi
            })


class product_label_qty(models.TransientModel):
    _name = 'product.small.label.qty'
    _description = 'Product Small Label Quantity'

    product_id = fields.Many2one('product.product', string='Product', required=True)
    qty = fields.Integer(string='Quantity', default=1)
    prod_small_wiz_id = fields.Many2one('wizard.product.small.label.report', string='Product Label Wizard ID')
    line_id = fields.Integer(string='Line ID')
    attribute_ids = fields.Many2many('product.attribute.value', 'wizard_attribute_value_table', 'product_line_id',
                                     'attribute_id', string="Attributes")


class aces_product_field_line(models.TransientModel):
    _name = 'aces.product.field.line'
    _description = 'Product Field Line Wizard'

    font_size = fields.Integer(string="Font Size", default=10)
    font_color = fields.Selection([('black', 'Black'), ('blue', 'Blue'),
                                   ('cyan', 'Cyan'), ('gray', 'Gray'),
                                   ('green', 'Green'), ('lime', 'Lime'),
                                   ('maroon', 'Maroon'), ('pink', 'Pink'),
                                   ('purple', 'Purple'), ('red', 'Red'),
                                   ('yellow', 'Yellow')], string="Font Color", default='black')
    sequence = fields.Integer(string="Sequence")
    field_id = fields.Many2one('ir.model.fields', string="Fields Name")
    wizard_id = fields.Many2one('wizard.product.small.label.report', string="Barcode Label ID")
    field_width = fields.Float(string="Field Width(%)", default=100.00)
    margin_value = fields.Char(string="Field Margin(%)(T,R,B,L)", default='0,0,0,0',
                               help="Field Margin(%)T(Top),R(Right),B(Bottom),L(Left)")
    with_currency = fields.Boolean(string="With Currency")
    field_align = fields.Selection([('center', 'Center'), ('right', 'Right'), ('left', 'Left')],
                                   string="Align", default='center')
    font_weight = fields.Selection([('normal', 'Normal'), ('bold', 'Bold')],
                                   string="Font Weight", default='normal')
    field_border = fields.Integer(string="Border")


class product_attribute_value(models.Model):
    _inherit = 'product.attribute.value'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if self._context.get('from_wizard') and self._context.get('product_id'):
            product_record = self.env['product.product'].browse([self._context.get('product_id')])
            args.append(
                ('id', 'in', [attribute.id for attribute in product_record.product_template_attribute_value_ids]))
        return super(product_attribute_value, self).name_search(name, args, operator='ilike', limit=limit)


class ir_model_fields(models.Model):
    _inherit = 'ir.model.fields'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if self._context.get('from_wizard'):
            field_record = self.browse([self._context.get('field_id')])
            args += ['|', ('ttype', 'not in', ('many2many', 'one2many', 'many2one')),
                     ('name', 'in', ['categ_id', 'product_template_attribute_value_ids', 'uom_id'])]
        return super(ir_model_fields, self).name_search(name, args, operator='ilike', limit=limit)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

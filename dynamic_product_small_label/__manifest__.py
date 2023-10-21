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

{
    'name': "Dynamic Product Small Label",
    'version': '16.0.1.0',
    'category': 'Product',
    'description': """
        User can create custom label template by frontend and can print the dynamic product label report.
    """,
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'website': 'http://www.acespritech.com',
    'summary': 'Create custom label template and print dynamic product label report.',
    'depends': [
        'base', 
        'sale_management', 
        'purchase', 
        'stock', 
        'account'
    ],
    'price': 149,
    'currency': 'EUR',
    'data': [
         'security/ir.model.access.csv',
         'views/prod_small_lbl_rpt.xml',
         'views/product_small_fields_label.xml',
         'views/wizard_product_small_label_report.xml',
         'reports/dynamic_product_small_label_report.xml',
         'data/design_data.xml',
    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

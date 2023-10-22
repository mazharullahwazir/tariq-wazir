# -*- coding: utf-8 -*-
{
    'name': "wb_pos_restrict",

    'summary': """
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['point_of_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            "wb_pos_restrict/static/src/js/wb_simple_button.js",
            "wb_pos_restrict/static/src/xml/wb_simple_button.xml",
        ]
    }
}

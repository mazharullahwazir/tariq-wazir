# -*- coding: utf-8 -*-


{
    'name': 'Print Repair Order',
    'summary': """Generate PDF Report of Repair Order""",
    'version': '16.0.1.0',
    'author': 'ZAMZAM INTERNATIONAL',
    'category': 'MRP Repair',
    'depends': [
        'base',
        'repair',
        'helpdesk_repair',
        'mrp_repair_discount',
        ],
    'license': 'AGPL-3',
    'data': [
        'views/repair_order_view.xml',
        'wizard/wizard_view.xml',
        'wizard/repairorder_template.xml',
        'wizard/repairorder_template1.xml',
        # 'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
}

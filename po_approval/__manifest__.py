# -*- coding: utf-8 -*-
{
    'name': "Purchase Order approval process",

    'summary': """
        Approval-related PO features""",

    'description': """
        Features:
            - If PO is not in RFQ state, needs Assistant/Manager approval to be canceled.
                - Approval request must be sent by user, with the cancel reason.
            - POs must be double-checked. To proceed to Purchase Order state must be approved
            by asssitant, and later, by the manager.
    """,

    'author': "IP Expert DR",
    'website': "http://www.ipexdr.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Purchase',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['purchase', 'log_wizard'],

    # always loaded
    'data': [
        'security/security.xml',
        # 'security/ir.model.access.csv',
        'views/purchase_views.xml',
        'views/res_config_settings_views.xml',
        'reports/po_report.xml',
        'reports/rfq_report.xml',
        'data/paperformat_us_landscape.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    'css': [
        'static/src/css/style.css'
    ]
}

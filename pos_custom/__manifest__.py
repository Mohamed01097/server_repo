{
    'name': 'POS Customizations',
    'category': 'Point of Sale',
    'summary': 'Customized point of sale features',
    'description': "Customized point of sale features",
    'version': '16.0.1.0',
    'author': 'Amr ElAdl',
    'depends': ['base', 'point_of_sale', 'hraj_marketing', 'web_domain_field'],
    'data': [
        # Security
        'security/ir.model.access.csv',
        # Views
        'views/res_users_view.xml',
        'views/pos_payment_method_view.xml',
        'views/pos_order_view.xml',
        'views/account_move_view.xml',
        # Report
        'report/car_report.xml',
        'report/report.xml',
        # Wizard
        'wizards/car_report_view.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            "pos_custom/static/src/js/*.js",
            "pos_custom/static/src/xml/*.xml",
        ],
    },
    'installable': True,
}

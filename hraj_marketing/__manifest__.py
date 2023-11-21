{
    'name': 'Hraj Marketing',
    'summary': 'Hraj Marketing',
    'description': 'Hraj Marketing',
    'version': '16.0.1.0',
    'author': 'M.Helal',
    'depends': ['base','hr','sale_management','purchase','point_of_sale'],
    'post_init_hook': 'post_init_hook',
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml'
    ],
    'assets': {
        'point_of_sale.assets': [

        ],
    },
    'installable': True,
}

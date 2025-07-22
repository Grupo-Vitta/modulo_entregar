{
    'name': 'Logística API Integración',
    'version': '1.0.0',
    'summary': 'Integración con API logística externa para envíos, precios y geolocalización',
    'author': 'Sebastian Diaz',
    'category': 'Custom',
    'depends': ['base', 'stock', 'sale', 'delivery'],  
    'data': [ 
    'security/ir.model.access.csv',
    'views/shipping_wizard_view.xml',
    'views/shipping_status_wizard_view.xml',
    'views/shipping_menu.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

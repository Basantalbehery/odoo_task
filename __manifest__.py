{
    'name': 'Porcelia Equipment Loan Manager',
    'version': '19.0.1.0.0',
    'category': 'Human Resources/Equipment',
    'summary': 'Manage equipment loans, penalties, and tracking',
    'author': 'Porcelia / Your Name',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/equipment_groups.xml',
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'views/equipment_item_views.xml',
        'views/equipment_category_views.xml',
        'views/equipment_loan_views.xml',
        'views/menus.xml'
    ],
    'installable': True,
    'application': True,
}
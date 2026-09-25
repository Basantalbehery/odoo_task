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
        'data/equipment_loan_cron.xml',
        'wizard/equipment_loan_return_wizard_views.xml',
        'views/res_users_views.xml',
        'views/equipment_item_views.xml',
        'views/equipment_category_views.xml',
        'views/equipment_loan_views.xml',
        'views/equipment_dashboard_views.xml',
        'report/equipment_loan_report.xml',
        'views/menus.xml'
    ],
    'installable': True,
    'application': True,
    
    'assets': {
        'web.assets_backend': [
            'porcelia_equipment_loan/static/src/components/condition_gauge/condition_gauge.js',
            'porcelia_equipment_loan/static/src/components/condition_gauge/condition_gauge.xml',
            'porcelia_equipment_loan/static/src/components/condition_gauge/condition_gauge.scss',
            'porcelia_equipment_loan/static/src/components/dashboard/equipment_dashboard.js',
            'porcelia_equipment_loan/static/src/components/dashboard/equipment_dashboard.xml',
            'porcelia_equipment_loan/static/src/components/dashboard/equipment_dashboard.scss',
        ],
    },
}
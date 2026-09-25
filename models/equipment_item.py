from odoo import models, fields, api

class EquipmentItem(models.Model):
    _name = 'equipment.item'
    _description = 'Equipment Item'

    name = fields.Char(string='Item Name', required=True)
    code = fields.Char(string='Item Code', required=True, copy=False, default='/')
    category_id = fields.Many2one('equipment.category', string='Category', ondelete='restrict')
    image_1920= fields.Image(string='Image')
    active = fields.Boolean(string='Active', default=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related='company_id.currency_id', store=True)
    daily_rate =  fields.Monetary(string='Daily Rate', currency_field='currency_id')
    condition_score = fields.Integer(string='Condition Score', default=100)
    
    
    state =  fields.Selection([
        ('available', 'Available'),
        ('on_loan', 'On Loan'),
        ('maintenance', 'Maintenance'),
        ('scrapped', 'Scrapped'),
    ], string='State', default='available', compute='_compute_state', store=True)
    
    
    loan_ids = fields.One2many('equipment.loan', 'item_id', string='Loans')
    loan_count = fields.Integer(string='Loan Count', compute='_compute_loan_date')
    total_days_on_loan = fields.Integer(string='Total Loan Days', compute='_compute_loan_date')
    
    
    _sql_constraints = [
        ('code_company_unique', 'unique(code, company_id)', 'The item code must be unique per company.'),
    ]

    
    @api.depends('loan_ids.state')
    def _compute_state(self):
        for item in self:
            confirmed_loans = item.loan_ids.filtered(lambda l: l.state == 'confirmed')
            if confirmed_loans:
                item.state = 'on_loan'
            elif item.state not in ['maintenance', 'scrapped']:
                item.state = 'available'
            else:
                item.state = item.state
    
    @api.depends('loan_ids', 'loan_ids.state', 'loan_ids.date_start', 'loan_ids.date_due', 'loan_ids.date_return')            
    def _compute_loan_date(self):
        count_data = self.env['equipment.loan']._read_group(
            [('item_id', 'in', self.ids)],
            ['item_id'],
            ['__count']
        )
        
        count_map = {item.id: count for item, count in count_data}
        
        days_data = self.env['equipment.loan']._read_group(
            [('item_id', 'in', self.ids), ('state', 'in', ['confirmed', 'returned'])],
            ['item_id'],
            ['duration_days:sum']
        )
        days_map = {item.id: days_sum for item, days_sum in days_data}
        
        for item in self:
            item.loan_count = count_map.get(item.id, 0)
            item.total_days_on_loan = days_map.get(item.id, 0)
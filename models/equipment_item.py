from odoo import models, fields, api

class EquipmentItem(models.Model):
    _name = 'equipment.item'
    _description = 'Equipment Item'

    name = fields.Char(string='Item Name', required=True, help="The name of the equipment item.")
    code = fields.Char(string='Item Code', required=True, copy=False, default='/', index=True, help="A unique code for the equipment item.")
    category_id = fields.Many2one('equipment.category', string='Category', ondelete='restrict', index=True, help="The category to which the equipment item belongs.")
    image_1920= fields.Image(string='Image', help="An image representing the equipment item.")
    active = fields.Boolean(string='Active', default=True, index=True, help="Indicates whether the equipment item is active.")
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company, help="The company that owns the equipment item.")
    currency_id = fields.Many2one('res.currency', string='Currency', related='company_id.currency_id', store=True, help="The currency used for the equipment item.")
    daily_rate =  fields.Monetary(string='Daily Rate', currency_field='currency_id', help="The daily rental rate for the equipment item.")
    condition_score = fields.Integer(string='Condition Score', default=100, help="A score representing the condition of the equipment item, ranging from 0 (poor) to 100 (excellent).")
    
    
    state =  fields.Selection([
        ('available', 'Available'),
        ('on_loan', 'On Loan'),
        ('maintenance', 'Maintenance'),
        ('scrapped', 'Scrapped'),
    ], string='State', default='available', compute='_compute_state', store=True, index=True, help="The current state of the equipment item, indicating whether it is available, on loan, under maintenance, or scrapped.")
    
    
    loan_ids = fields.One2many('equipment.loan', 'item_id', string='Loans', help="The loans associated with the equipment item.")
    loan_count = fields.Integer(string='Loan Count', compute='_compute_loan_date', help="The number of loans for the equipment item.")
    total_days_on_loan = fields.Integer(string='Total Loan Days', compute='_compute_loan_date', help="The total number of days the equipment item has been on loan.")
    
    
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
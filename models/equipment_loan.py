from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta
import math


class EquipmentLoan(models.Model):
    _name = 'equipment.loan'
    _description = 'Equipment Loan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_start desc, id desc'

    name = fields.Char(string='Loan Reference', required=True, copy=False, default='/', readonly=True, help="A unique reference for the equipment loan, automatically generated.")
    item_id = fields.Many2one('equipment.item', string='Equipment Item', required=True, ondelete='restrict', index=True, help="The equipment item being loaned.")
    borrower_id = fields.Many2one('res.partner', string='Borrower', required=True, index=True, help="The partner who borrowed the equipment.")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, help="The company that owns the equipment loan.")
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', help="The currency used for the equipment loan.", store=True)
    date_start = fields.Datetime(string='Start Date', default=fields.Datetime.now, required=True, index=True, help="The date and time when the equipment loan starts.")
    date_due = fields.Datetime(string='Due Date', required=True, index=True, help="The date and time when the equipment loan is due.")
    date_return = fields.Datetime(string='Actual Return Date', readonly=True, help="The date and time when the equipment was actually returned.")
    daily_rate = fields.Monetary(string='Daily Rate', related='item_id.daily_rate', store=True, help="The daily rental rate for the equipment item.")
    total_price = fields.Monetary(string='Total Price', compute='_compute_total_price', store=True, help="The total price for the equipment loan, calculated based on the daily rate and duration.")
    days_late = fields.Integer(string='Days Late', compute='_compute_days_late', store=True, help="The number of days the equipment loan is late, calculated based on the due date and actual return date.")
    duration_days = fields.Integer(string='Duration (Days)', compute='_compute_duration_days', store=True, help="The duration of the equipment loan in days.")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('returned', 'Returned'),
        ('cancelled', 'Cancelled'),
    ], string='State', default='draft', required=True, tracking=True, index=True, help="The current state of the equipment loan, indicating whether it is in draft, confirmed, returned, or cancelled.")


    note = fields.Text(string='Notes', help="Additional notes about the equipment loan.")
    
    
    _sql_constraints = [
        ('check_dates', 'CHECK (date_due >= date_start)', 'Due date must be greater than or equal to start date.'),
    ]
    
    @api.depends('date_start', 'date_due', 'date_return', 'state')
    def _compute_duration_days(self):
        now = fields.Datetime.now()
        for loan in self:
            if loan.state in ['confirmed', 'returned'] and loan.date_start:
                end_date = loan.date_return or loan.date_due or now
                if end_date > loan.date_start:
                    delta = end_date - loan.date_start
                    loan.duration_days = max(math.ceil(delta.total_seconds() / 86400), 1)
                    continue
            loan.duration_days = 0


    @api.depends('date_start', 'date_due', 'daily_rate')
    def _compute_total_price(self):
        for loan in self:
            if loan.date_start and loan.date_due:
                delta = loan.date_due - loan.date_start
                days = max(delta.days, 1)
                loan.total_price = days * loan.daily_rate
            else:
                loan.total_price = 0.0

    @api.depends('date_due', 'date_return', 'state')
    def _compute_days_late(self):
        now = fields.Datetime.now()
        for loan in self:
            if loan.state == 'confirmed' and loan.date_due and now > loan.date_due:
                delta = now - loan.date_due
                loan.days_late = math.ceil(delta.total_seconds() / 86400)
            elif loan.state == 'returned' and loan.date_due and loan.date_return and loan.date_return > loan.date_due:
                delta = loan.date_return - loan.date_due
                loan.days_late = math.ceil(delta.total_seconds() / 86400)
            else:
                loan.days_late = 0

    @api.constrains('item_id', 'date_start', 'date_due', 'state')
    def _check_item_availability(self):
        for loan in self:
            if loan.state == 'confirmed':
                overlapping_loans = self.search([
                    ('id', '!=', loan.id),
                    ('item_id', '=', loan.item_id.id),
                    ('state', '=', 'confirmed'),
                    ('date_start', '<', loan.date_due),
                    ('date_due', '>', loan.date_start),
                ])
                if overlapping_loans:
                    raise ValidationError(f"The item '{loan.item_id.name}' is already loaned during this time period!")

    def action_confirm(self):
        for loan in self:
            if loan.state == 'draft':
                if loan.name == '/':
                    loan.name = self.env['ir.sequence'].next_by_code('equipment.loan') or '/'
                loan.state = 'confirmed'

    def action_return(self):
        for loan in self:
            if loan.state == 'confirmed':
                loan.date_return = fields.Datetime.now()
                loan.state = 'returned'

    def action_cancel(self):
        for loan in self:
            if loan.state in ['draft', 'confirmed']:
                loan.state = 'cancelled'
                
                
    @api.ondelete(at_uninstall=False)
    def _check_unlink(self):
        for loan in self:
            if loan.state not in ['draft', 'cancelled']:
                raise ValidationError("You can only delete draft or cancelled loans.")

    @api.model
    def _cron_check_overdue_loans(self):
        overdue_loans = self.search([
            ('state', '=', 'confirmed'),
            ('date_due', '<', fields.Datetime.now())
        ])
        for loan in overdue_loans:
            existing_activity = self.env['mail.activity'].search([
                ('res_model', '=', 'equipment.loan'),
                ('res_id', '=', loan.id),
                ('summary', '=', 'Overdue Loan Notification')
            ])
            if not existing_activity:
                loan.activity_schedule(
                    'mail.mail_activity_data_warning',
                    summary='Overdue Loan Notification',
                    user_id=loan.borrower_id.user_ids[:1].id or self.env.uid
                )
                
                
    @api.model
    def get_dashboard_data(self, period='month'):
        now = fields.Datetime.now()
        if period == 'week':
            start_date = now - timedelta(days=7)
        elif period == 'month':
            start_date = now - timedelta(days=30)
        else:
            start_date = None
        
        
        loan_domain = []
        if start_date:
            loan_domain = [('create_date', '>=', start_date)]
            
            
        total_items = self.env['equipment.item'].search_count([('active', '=', True)])
        items_on_loan = self.env['equipment.item'].search_count([('state', '=', 'on_loan')])

        
        overdue_domain = [
            ('state', '=', 'confirmed'),
            ('date_due', '<', now)
        ]
        overdue_loans_count = self.search_count(overdue_domain)


        aggregated_penalties = self._read_group(
            loan_domain,
            [],
            ['total_price:sum']
        )
        total_penalties = aggregated_penalties[0][0] if aggregated_penalties and aggregated_penalties[0][0] else 0.0


        top_overdue_records = self.search(
            overdue_domain,
            order='days_late desc',
            limit=5
        )

        top_overdue = [{
            'id': loan.id,
            'name': loan.name,
            'item_name': loan.item_id.name,
            'borrower_name': loan.borrower_id.name,
            'days_late': loan.days_late,
        } for loan in top_overdue_records]

        return {
            'total_items': total_items,
            'items_on_loan': items_on_loan,
            'overdue_loans': overdue_loans_count,
            'total_penalties': total_penalties,
            'top_overdue': top_overdue,
        }
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class EquipmentLoan(models.Model):
    _name = 'equipment.loan'
    _description = 'Equipment Loan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_start desc, id desc'

    name = fields.Char(string='Loan Reference', required=True, copy=False, default='/', readonly=True)
    item_id = fields.Many2one('equipment.item', string='Equipment Item', required=True, ondelete='restrict')
    borrower_id = fields.Many2one('res.partner', string='Borrower', required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    date_start = fields.Datetime(string='Start Date', default=fields.Datetime.now, required=True)
    date_due = fields.Datetime(string='Due Date', required=True)
    date_return = fields.Datetime(string='Actual Return Date', readonly=True)
    daily_rate = fields.Monetary(string='Daily Rate', related='item_id.daily_rate', store=True)
    total_price = fields.Monetary(string='Total Price', compute='_compute_total_price', store=True)
    days_late = fields.Integer(string='Days Late', compute='_compute_days_late', store=True)
    
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('returned', 'Returned'),
        ('cancelled', 'Cancelled'),
    ], string='State', default='draft', required=True, tracking=True)


    note = fields.Text(string='Notes')
    
    
    _sql_constraints = [
        ('check_dates', 'CHECK (date_due >= date_start)', 'Due date must be greater than or equal to start date.'),
    ]
    
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
                loan.days_late = (now - loan.date_due).days
            elif loan.state == 'returned' and loan.date_due and loan.date_return and loan.date_return > loan.date_due:
                loan.days_late = (loan.date_return - loan.date_due).days
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
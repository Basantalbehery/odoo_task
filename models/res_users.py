from odoo import models, fields
class ResUsers(models.Model):
    _inherit = 'res.users'

    equipment_loan_ids = fields.One2many('equipment.loan', compute="_compute_equipment_loans", string='Equipment Loans')
    
    
    def _compute_equipment_loans(self):
        for user in self:
            user.equipment_loan_ids = self.env['equipment.loan'].search([('borrower_id', '=', user.partner_id.id)])
from odoo import fields, models

class ResUsers(models.Model):
    _inherit = 'res.users'

    equipment_loan_ids = fields.One2many(
        'equipment.loan',
        'borrower_id',
        string='Equipment Loans'
    )
    equipment_loan_count = fields.Integer(
        string='Loans Count',
        compute='_compute_equipment_loan_count'
    )

    def _compute_equipment_loan_count(self):
        for user in self:
            user.equipment_loan_count = len(user.equipment_loan_ids)

    def action_view_user_loans(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("porcelia_equipment_loan.action_equipment_loan")
        action['domain'] = [('borrower_id', '=', self.id)]
        action['context'] = {'default_borrower_id': self.id}
        return action
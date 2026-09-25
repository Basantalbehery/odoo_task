from odoo import models, fields, api

class EquipmentLoanReturnWizard(models.TransientModel):
    _name = 'equipment.loan.return.wizard'
    _description = 'Equipment Loan Return Wizard'

    
    condition_score = fields.Integer(string='New Condition Score', default=100)

    def action_apply_return(self):
        active_ids = self.env.context.get('active_ids', [])
        loans = self.env['equipment.loan'].browse(active_ids)
        for loan in loans:
            if loan.state == 'confirmed':
                loan.action_return()
                if hasattr(loan.item_id, 'condition_score'):
                    loan.item_id.condition_score = self.condition_score

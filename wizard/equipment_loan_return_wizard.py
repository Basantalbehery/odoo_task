from odoo import models, fields, _
from odoo.exceptions import UserError

class EquipmentLoanReturnWizard(models.TransientModel):
    _name = 'equipment.loan.return.wizard'
    _description = 'Equipment Loan Return Wizard'

    
    date_return = fields.Datetime(
            string='Return Date',
            default=fields.Datetime.now,
            required=True
    )
    condition_score = fields.Integer(
        string='Condition Score (0-100)',
        default=100,
        required=True
    )
    note = fields.Text(string='Return Note')

    def action_confirm_return(self):
        active_ids = self.env.context.get('active_ids', [])
        if not active_ids:
            raise UserError(_("No loans selected for return."))

        loans = self.env['equipment.loan'].browse(active_ids)
        for loan in loans:
            if loan.state == 'confirmed':
                loan.write({
                    'date_return': self.date_return,
                    'state': 'returned',
                })
                if self.note:
                    existing_note = loan.notes or ''
                    loan.notes = f"{existing_note}\nReturn Note: {self.note}".strip()
                

                if loan.item_id:
                    loan.item_id.condition_score = max(0, min(100, self.condition_score))
                

                loan.message_post(
                    body=_("Equipment returned via wizard on %s. Condition score updated to %s.") % (
                        self.date_return, self.condition_score
                    )
                )

        return {'type': 'ir.actions.act_window_close'}
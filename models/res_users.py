from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    equipment_loan_ids = fields.One2many(
        'equipment.loan',
        'borrower_id',
        string='Equipment Loans',
        help="The equipment loans associated with this user."
    )
    equipment_loan_count = fields.Integer(
        string='Loans Count',
        compute='_compute_equipment_loan_count',
        help="The number of equipment loans associated with this user."
    )

    @api.depends('equipment_loan_ids')
    def _compute_equipment_loan_count(self):
        partner_ids = self.mapped('partner_id.id')
        read_group_res = self.env['equipment.loan']._read_group(
            [('borrower_id', 'in', partner_ids)],
            ['borrower_id'],
            ['__count']
        )
        mapping = {partner.id: count for partner, count in read_group_res}
        for user in self:
            user.equipment_loan_count = mapping.get(user.partner_id.id, 0)

    def action_view_user_loans(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("porcelia_equipment_loan.action_equipment_loan")
        action['domain'] = [('borrower_id', '=', self.partner_id.id)]
        action['context'] = {'default_borrower_id': self.partner_id.id}
        return action
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from odoo.fields import Datetime
from datetime import timedelta


class TestEquipmentLoan(TransactionCase):

    def setUp(self):
        super().setUp()
        self.category = self.env['equipment.category'].create({'name': 'Laptops'})
        self.item = self.env['equipment.item'].create({
            'name': 'Test Laptop',
            'code': 'LAP-001',
            'category_id': self.category.id,
            'daily_rate': 50.0,
        })
        self.user = self.env['res.users'].create({
            'name': 'Test Borrower',
            'login': 'test_borrower',
            'email': 'borrower@test.com',
        })

    def test_01_overlap_rule(self):
        """Test that overlapping loans raise a ValidationError."""
        now = Datetime.now()
        self.env['equipment.loan'].create({
            'item_id': self.item.id,
            'borrower_id': self.user.id,
            'date_start': now,
            'date_due': now + timedelta(days=3),
            'state': 'confirmed',
        })

        with self.assertRaises(ValidationError):
            self.env['equipment.loan'].create({
                'item_id': self.item.id,
                'borrower_id': self.user.id,
                'date_start': now + timedelta(days=1),
                'date_due': now + timedelta(days=4),
                'state': 'confirmed',
            })

    def test_02_penalty_calculation(self):
        """Test late penalty computation on return wizard/action."""
        now = Datetime.now()
        loan = self.env['equipment.loan'].create({
            'item_id': self.item.id,
            'borrower_id': self.user.id,
            'date_start': now - timedelta(days=5),
            'date_due': now - timedelta(days=2),
            'state': 'confirmed',
        })
        loan.date_return = now
        loan.action_return()
        
        self.assertEqual(loan.days_late, 2)
        self.assertEqual(loan.penalty_amount, 100.0)
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, AccessError
from odoo.fields import Datetime
from datetime import timedelta


class TestEquipmentLoan(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = cls.env['equipment.category'].create({'name': 'Laptops'})
        cls.item = cls.env['equipment.item'].create({
            'name': 'Test Laptop',
            'code': 'LAP-001',
            'category_id': cls.category.id,
            'daily_rate': 50.0,
        })
        

        cls.user_a = cls.env['res.users'].create({
            'name': 'Borrower A',
            'login': 'borrower_a',
            'email': 'borrowera@test.com',
            'groups_id': [(6, 0, [cls.env.ref('porcelia_equipment_loan.group_equipment_user').id])],
        })
        
        cls.user_b = cls.env['res.users'].create({
            'name': 'Borrower B',
            'login': 'borrower_b',
            'email': 'borrowerb@test.com',
            'groups_id': [(6, 0, [cls.env.ref('porcelia_equipment_loan.group_equipment_user').id])],
        })

    def test_01_overlap_rule(self):
        """Test that overlapping loans raise a ValidationError."""
        now = Datetime.now()
        self.env['equipment.loan'].create({
            'item_id': self.item.id,
            'borrower_id': self.user_a.id,
            'date_start': now,
            'date_due': now + timedelta(days=3),
            'state': 'confirmed',
        })

        with self.assertRaises(ValidationError):
            self.env['equipment.loan'].create({
                'item_id': self.item.id,
                'borrower_id': self.user_b.id,
                'date_start': now + timedelta(days=1),
                'date_due': now + timedelta(days=4),
                'state': 'confirmed',
            })

    def test_02_penalty_calculation(self):
        """Test late penalty computation on return."""
        now = Datetime.now()
        loan = self.env['equipment.loan'].create({
            'item_id': self.item.id,
            'borrower_id': self.user_a.id,
            'date_start': now - timedelta(days=5),
            'date_due': now - timedelta(days=2),
            'state': 'confirmed',
        })
        loan.date_return = now
        
        if hasattr(loan, 'action_return'):
            loan.action_return()
        else:
            loan.state = 'returned'
        
        self.assertGreaterEqual(loan.days_late, 2)
        self.assertEqual(loan.penalty_amount, loan.days_late * self.item.daily_rate)

    def test_03_record_rule_user_access(self):
        """Test that Equipment User cannot read loans of another user."""
        loan_b = self.env['equipment.loan'].create({
            'item_id': self.item.id,
            'borrower_id': self.user_b.id,
            'date_start': Datetime.now(),
            'date_due': Datetime.now() + timedelta(days=2),
            'state': 'confirmed',
        })


        with self.assertRaises(AccessError):
            loan_b.with_user(self.user_a).read(['name', 'borrower_id'])
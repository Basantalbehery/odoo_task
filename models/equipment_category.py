from odoo import models, fields, api

class EquipmentCategory(models.Model):
    _name = 'equipment.category'
    _description = 'Equipment Category'
    _parent_store = True
    _rec_name = 'complete_name'
    _order = 'complete_name'

    name = fields.Char(string='Category Name', required=True, translate=True)
    complete_name = fields.Char(string='Complete Name', compute='_compute_complete_name')
    parent_id = fields.Many2one('equipment.category', string='Parent Category', index=True, ondelete='cascade')
    child_ids = fields.One2many('equipment.category', 'parent_id', string='Child Categories')
    parent_path = fields.Char(index=True)
    item_ids = fields.One2many('equipment.item', 'category_id', string='Items')
    item_count = fields.Integer(string='Item Count', compute='_compute_item_count')


    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = f"{category.parent_id.complete_name} / {category.name}"
            else:
                category.complete_name = category.name

    def _compute_item_count(self):
        read_group_res = self.env['equipment.item'].read_group(
            [('category_id', 'in', self.ids)],
            ['category_id'],
            ['__count']
        )
        mapping = {category.id: count for category, count in read_group_res}
        for category in self:
            category.item_count = mapping.get(category.id, 0)
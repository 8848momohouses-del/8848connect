from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    store_performance_count = fields.Integer(
        compute='_compute_store_performance_count')

    def _compute_store_performance_count(self):
        groups = self.env['8848.store.performance']._read_group(
            [('franchise_id', 'in', self.ids)], ['franchise_id'], ['__count'])
        counts = {partner.id: count for partner, count in groups}
        for partner in self:
            partner.store_performance_count = counts.get(partner.id, 0)

    def action_view_store_performance(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id(
            '8848_store_performance.action_store_performance')
        action['domain'] = [('franchise_id', '=', self.id)]
        action['context'] = {'default_franchise_id': self.id}
        return action

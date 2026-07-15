from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    royalty_statement_count = fields.Integer(
        compute='_compute_royalty_statement_count')

    def _compute_royalty_statement_count(self):
        groups = self.env['8848.royalty.statement']._read_group(
            [('franchise_id', 'in', self.ids)], ['franchise_id'], ['__count'])
        counts = {partner.id: count for partner, count in groups}
        for partner in self:
            partner.royalty_statement_count = counts.get(partner.id, 0)

    def action_view_royalty_statements(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id(
            '8848_royalty.action_royalty_statement')
        action['domain'] = [('franchise_id', '=', self.id)]
        action['context'] = {'default_franchise_id': self.id}
        return action

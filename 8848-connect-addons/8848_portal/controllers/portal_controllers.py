from odoo import http
from odoo.http import request

class FranchisePortal(http.Controller):

    @http.route(['/my/franchise'], type='http', auth="user", website=True)
    def franchise_dashboard(self, **kw):
        partner = request.env.user.partner_id
        if not partner.is_franchise:
            return request.redirect('/my')

        # Get pending deliveries
        pending_deliveries = request.env['stock.picking'].sudo().search([
            ('partner_id', '=', partner.id),
            ('state', 'not in', ['done', 'cancel'])
        ])

        # Get outstanding balance (if any) from account move
        invoices = request.env['account.move'].sudo().search([
            ('partner_id', '=', partner.id),
            ('move_type', '=', 'out_invoice'),
            ('payment_state', 'in', ['not_paid', 'partial'])
        ])
        outstanding_balance = sum(invoices.mapped('amount_residual'))

        # Get monthly royalty statements
        statements = request.env['8848.royalty.statement'].sudo().search([
            ('franchise_id', '=', partner.id)
        ])

        values = {
            'partner': partner,
            'pending_deliveries': pending_deliveries,
            'outstanding_balance': outstanding_balance,
            'statements': statements,
            'page_name': 'franchise_dashboard',
        }
        return request.render("8848_portal.portal_franchise_dashboard", values)

from odoo import http
from odoo.http import request

    @http.route(['/my/franchise/select'], type='http', auth="user", website=True, methods=['POST'])
    def select_franchise(self, franchise_id, redirect='/my/franchise', **kw):
        franchise_id = int(franchise_id)
        permitted = request.env.user._get_permitted_franchise_ids()
        if franchise_id in permitted:
            request.session['active_franchise_id'] = franchise_id
        return request.redirect(redirect)

    @http.route(['/my/franchise'], type='http', auth="user", website=True)
    def franchise_dashboard(self, **kw):
        permitted_ids = request.env.user._get_permitted_franchise_ids()
        if not permitted_ids:
            return request.redirect('/my')

        active_id = request.session.get('active_franchise_id')
        if not active_id or active_id not in permitted_ids:
            active_id = permitted_ids[0]
            request.session['active_franchise_id'] = active_id

        active_franchise = request.env['res.partner'].sudo().browse(active_id)
        permitted_franchises = request.env['res.partner'].sudo().browse(permitted_ids)

        # Standard models might need sudo if portal user lacks explicit read ACL, 
        # but we restrict strictly by active_id which is proven to be permitted.
        # We will use sudo here safely because we are strictly domain-locking to active_id.
        pending_deliveries = request.env['stock.picking'].sudo().search([
            ('partner_id', '=', active_id),
            ('state', 'not in', ['done', 'cancel'])
        ])

        invoices = request.env['account.move'].sudo().search([
            ('partner_id', '=', active_id),
            ('move_type', '=', 'out_invoice'),
            ('payment_state', 'in', ['not_paid', 'partial'])
        ])
        outstanding_balance = sum(invoices.mapped('amount_residual'))

        statements = request.env['8848.royalty.statement'].sudo().search([
            ('franchise_id', '=', active_id)
        ])

        values = {
            'active_franchise': active_franchise,
            'permitted_franchises': permitted_franchises,
            'pending_deliveries': pending_deliveries,
            'outstanding_balance': outstanding_balance,
            'statements': statements,
            'page_name': 'franchise_dashboard',
        }
        return request.render("8848_portal.portal_franchise_dashboard", values)

from odoo import http
from odoo.http import request

class FranchiseFinancePortal(http.Controller):

    @http.route(['/my/invoices'], type='http', auth="user", website=True)
    def invoice_list(self, **kw):
        permitted_ids = request.env.user._get_permitted_franchise_ids('finance')
        if not permitted_ids:
            return request.redirect('/my/franchise')
            
        active_id = request.session.get('active_franchise_id')
        if not active_id or active_id not in permitted_ids:
            return request.redirect('/my/franchise')
            
        invoices = request.env['account.move'].sudo().search([
            ('partner_id', '=', active_id),
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted')
        ], order='invoice_date desc')
        
        values = {
            'invoices': invoices,
            'page_name': 'franchise_invoices',
        }
        return request.render("8848_portal.portal_franchise_invoices", values)

    @http.route(['/my/invoices/<int:invoice_id>'], type='http', auth="user", website=True)
    def invoice_details(self, invoice_id, **kw):
        permitted_ids = request.env.user._get_permitted_franchise_ids('finance')
        invoice = request.env['account.move'].sudo().browse(invoice_id)
        
        if not invoice.exists() or invoice.partner_id.id not in permitted_ids:
            return request.redirect('/my/invoices')
            
        values = {
            'invoice': invoice,
            'page_name': 'franchise_invoice_details',
        }
        return request.render("8848_portal.portal_franchise_invoice_details", values)

    @http.route(['/my/statements'], type='http', auth="user", website=True)
    def statement_list(self, **kw):
        permitted_ids = request.env.user._get_permitted_franchise_ids('finance')
        if not permitted_ids:
            return request.redirect('/my/franchise')
            
        active_id = request.session.get('active_franchise_id')
        if not active_id or active_id not in permitted_ids:
            return request.redirect('/my/franchise')
            
        statements = request.env['8848.royalty.statement'].sudo().search([
            ('franchise_id', '=', active_id)
        ], order='date_end desc')
        
        values = {
            'statements': statements,
            'page_name': 'franchise_statements',
        }
        return request.render("8848_portal.portal_franchise_statements", values)

    @http.route(['/my/statements/<int:stmt_id>'], type='http', auth="user", website=True)
    def statement_details(self, stmt_id, **kw):
        permitted_ids = request.env.user._get_permitted_franchise_ids('finance')
        statement = request.env['8848.royalty.statement'].sudo().browse(stmt_id)
        
        if not statement.exists() or statement.franchise_id.id not in permitted_ids:
            return request.redirect('/my/statements')
            
        values = {
            'stmt': statement,
            'page_name': 'franchise_statement_details',
        }
        return request.render("8848_portal.portal_franchise_statement_details", values)

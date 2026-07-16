from odoo import http
from odoo.http import request

class FranchiseSupportPortal(http.Controller):

    @http.route(['/my/messages'], type='http', auth="user", website=True)
    def message_list(self, **kw):
        permitted_ids = request.env.user._get_permitted_franchise_ids()
        if not permitted_ids:
            return request.redirect('/my/franchise')
            
        active_id = request.session.get('active_franchise_id')
        if not active_id or active_id not in permitted_ids:
            return request.redirect('/my/franchise')
            
        messages = request.env['8848.communication.message'].sudo().search([
            ('partner_id', '=', active_id),
            ('portal_visibility', '=', True)
        ], order='date desc')
        
        values = {
            'messages': messages,
            'page_name': 'franchise_messages',
        }
        return request.render("8848_portal.portal_franchise_messages", values)

    @http.route(['/my/support'], type='http', auth="user", website=True)
    def support_list(self, **kw):
        permitted_ids = request.env.user._get_permitted_franchise_ids()
        if not permitted_ids:
            return request.redirect('/my/franchise')
            
        active_id = request.session.get('active_franchise_id')
        if not active_id or active_id not in permitted_ids:
            return request.redirect('/my/franchise')
            
        tickets = request.env['8848.support.ticket'].sudo().search([
            ('franchise_id', '=', active_id)
        ], order='create_date desc')
        
        values = {
            'tickets': tickets,
            'page_name': 'franchise_support',
        }
        return request.render("8848_portal.portal_franchise_support", values)

    @http.route(['/my/support/new'], type='http', auth="user", website=True)
    def support_new(self, **kw):
        permitted_ids = request.env.user._get_permitted_franchise_ids()
        if not permitted_ids:
            return request.redirect('/my/franchise')
            
        return request.render("8848_portal.portal_franchise_support_new", {'page_name': 'franchise_support_new'})

    @http.route(['/my/support/create'], type='http', auth="user", website=True, methods=['POST'])
    def support_create(self, subject, category, priority, description, **kw):
        permitted_ids = request.env.user._get_permitted_franchise_ids()
        active_id = request.session.get('active_franchise_id')
        
        if not active_id or active_id not in permitted_ids:
            return request.redirect('/my/franchise')
            
        request.env['8848.support.ticket'].sudo().create({
            'name': subject,
            'category': category,
            'priority': priority,
            'description': description,
            'franchise_id': active_id,
            'user_id': request.env.user.id
        })
        
        return request.redirect('/my/support')

    @http.route(['/my/support/<int:ticket_id>'], type='http', auth="user", website=True)
    def support_details(self, ticket_id, **kw):
        permitted_ids = request.env.user._get_permitted_franchise_ids()
        ticket = request.env['8848.support.ticket'].sudo().browse(ticket_id)
        
        if not ticket.exists() or ticket.franchise_id.id not in permitted_ids:
            return request.redirect('/my/support')
            
        values = {
            'ticket': ticket,
            'page_name': 'franchise_support_details',
        }
        return request.render("8848_portal.portal_franchise_support_details", values)

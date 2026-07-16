from odoo import http
from odoo.http import request

class FranchiseProfilePortal(http.Controller):

    @http.route(['/my/documents'], type='http', auth="user", website=True)
    def document_list(self, **kw):
        permitted_ids = request.env.user._get_permitted_franchise_ids()
        if not permitted_ids:
            return request.redirect('/my/franchise')
            
        active_id = request.session.get('active_franchise_id')
        if not active_id or active_id not in permitted_ids:
            return request.redirect('/my/franchise')
            
        # Fetch attachments linked to the franchise record (e.g. manuals, agreements)
        documents = request.env['ir.attachment'].sudo().search([
            ('res_model', '=', 'res.partner'),
            ('res_id', '=', active_id)
        ])
        
        values = {
            'documents': documents,
            'page_name': 'franchise_documents',
        }
        return request.render("8848_portal.portal_franchise_documents", values)

    @http.route(['/my/profile'], type='http', auth="user", website=True)
    def profile_view(self, **kw):
        values = {
            'partner': request.env.user.partner_id,
            'page_name': 'franchise_profile',
        }
        return request.render("8848_portal.portal_franchise_profile", values)

    @http.route(['/my/profile/update'], type='http', auth="user", website=True, methods=['POST'])
    def profile_update(self, name, phone, **kw):
        # Instead of directly modifying the user, we create a support ticket request 
        # to ensure no direct mutation of core records bypasses internal controls
        active_id = request.session.get('active_franchise_id')
        if not active_id:
            return request.redirect('/my/profile')
            
        description = f"Profile update request:\\nName: {name}\\nPhone: {phone}"
        request.env['8848.support.ticket'].sudo().create({
            'name': 'Profile Update Request',
            'category': 'other',
            'priority': 'low',
            'description': description,
            'franchise_id': active_id,
            'user_id': request.env.user.id
        })
        
        return request.redirect('/my/profile?success=1')

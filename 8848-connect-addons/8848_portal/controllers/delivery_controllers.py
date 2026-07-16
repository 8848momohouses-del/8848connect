from odoo import http
from odoo.http import request

class FranchiseDeliveryPortal(http.Controller):

    @http.route(['/my/deliveries'], type='http', auth="user", website=True)
    def delivery_list(self, **kw):
        permitted_ids = request.env.user._get_permitted_franchise_ids('order')
        if not permitted_ids:
            return request.redirect('/my/franchise')
            
        active_id = request.session.get('active_franchise_id')
        if not active_id or active_id not in permitted_ids:
            return request.redirect('/my/franchise')
            
        deliveries = request.env['stock.picking'].sudo().search([
            ('partner_id', '=', active_id),
            ('picking_type_code', '=', 'outgoing')
        ], order='scheduled_date desc')
        
        values = {
            'deliveries': deliveries,
            'page_name': 'franchise_deliveries',
        }
        return request.render("8848_portal.portal_franchise_deliveries", values)

    @http.route(['/my/deliveries/<int:picking_id>'], type='http', auth="user", website=True)
    def delivery_details(self, picking_id, **kw):
        permitted_ids = request.env.user._get_permitted_franchise_ids('order')
        picking = request.env['stock.picking'].sudo().browse(picking_id)
        
        if not picking.exists() or picking.partner_id.id not in permitted_ids:
            return request.redirect('/my/deliveries')
            
        # Try to find associated route stop for POD info securely
        stop = request.env['8848.delivery.route.stop'].sudo().search([
            ('picking_id', '=', picking.id)
        ], limit=1)
        
        values = {
            'delivery': picking,
            'stop': stop,
            'page_name': 'franchise_delivery_details',
        }
        return request.render("8848_portal.portal_franchise_delivery_details", values)

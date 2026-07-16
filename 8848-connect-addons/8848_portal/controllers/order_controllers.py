from odoo import http
from odoo.http import request

class FranchiseOrderPortal(http.Controller):

    @http.route(['/my/orders/new'], type='http', auth="user", website=True)
    def new_order_catalogue(self, **kw):
        permitted_ids = request.env.user._get_permitted_franchise_ids('order')
        if not permitted_ids:
            return request.redirect('/my/franchise')

        active_id = request.session.get('active_franchise_id')
        if not active_id or active_id not in permitted_ids:
            active_id = permitted_ids[0]
            request.session['active_franchise_id'] = active_id

        active_franchise = request.env['res.partner'].sudo().browse(active_id)
        
        # Determine pricelist
        pricelist = active_franchise.property_product_pricelist

        # Fetch products
        products = request.env['product.product'].sudo().search([
            ('sale_ok', '=', True),
            ('is_portal_orderable', '=', True),
            ('active', '=', True)
        ])

        # Server-side price calculation
        product_prices = {}
        for product in products:
            if pricelist:
                price = pricelist._get_product_price(product, 1.0, active_franchise)
            else:
                price = product.list_price
            product_prices[product.id] = price
            
        # Get current draft order
        draft_order = request.env['sale.order'].sudo().search([
            ('partner_id', '=', active_id),
            ('state', 'in', ['draft', 'sent']),
            ('approval_state', '=', 'draft')
        ], limit=1)

        values = {
            'active_franchise': active_franchise,
            'products': products,
            'product_prices': product_prices,
            'draft_order': draft_order,
            'page_name': 'franchise_catalogue',
        }
        return request.render("8848_portal.portal_franchise_catalogue", values)

    @http.route(['/my/orders/cart/update'], type='http', auth="user", website=True, methods=['POST'])
    def cart_update(self, product_id, quantity, **kw):
        product_id = int(product_id)
        quantity = float(quantity)
        
        permitted_ids = request.env.user._get_permitted_franchise_ids('order')
        if not permitted_ids:
            return request.redirect('/my/franchise')
            
        active_id = request.session.get('active_franchise_id')
        if not active_id or active_id not in permitted_ids:
            return request.redirect('/my/franchise')
            
        active_franchise = request.env['res.partner'].sudo().browse(active_id)
        
        draft_order = request.env['sale.order'].sudo().search([
            ('partner_id', '=', active_id),
            ('state', 'in', ['draft', 'sent']),
            ('approval_state', '=', 'draft')
        ], limit=1)
        
        if not draft_order:
            draft_order = request.env['sale.order'].sudo().create({
                'partner_id': active_id,
                'approval_state': 'draft'
            })
            
        order_line = draft_order.order_line.filtered(lambda l: l.product_id.id == product_id)
        if order_line:
            order_line.product_uom_qty += quantity
        else:
            # Force server-side price calculation by letting onchange trigger, 
            # or we manually fetch it here securely.
            request.env['sale.order.line'].sudo().create({
                'order_id': draft_order.id,
                'product_id': product_id,
                'product_uom_qty': quantity,
            })
            
        return request.redirect('/my/orders/new')
        
    @http.route(['/my/orders/cart/submit'], type='http', auth="user", website=True, methods=['POST'])
    def cart_submit(self, order_id, **kw):
        order_id = int(order_id)
        permitted_ids = request.env.user._get_permitted_franchise_ids('order')
        
        order = request.env['sale.order'].sudo().browse(order_id)
        if not order.exists() or order.partner_id.id not in permitted_ids or order.approval_state != 'draft':
            return request.redirect('/my/franchise')
            
        # Transition state to pending approval
        order.sudo().write({'approval_state': 'pending'})
        order.message_post(body="Order submitted from Franchise Portal.")
        
        return request.redirect('/my/orders')

    @http.route(['/my/orders'], type='http', auth="user", website=True)
    def order_history(self, **kw):
        permitted_ids = request.env.user._get_permitted_franchise_ids('order')
        if not permitted_ids:
            return request.redirect('/my/franchise')
            
        active_id = request.session.get('active_franchise_id')
        if not active_id or active_id not in permitted_ids:
            return request.redirect('/my/franchise')
            
        orders = request.env['sale.order'].sudo().search([
            ('partner_id', '=', active_id),
            ('approval_state', '!=', 'draft')
        ], order='date_order desc')
        
        values = {
            'orders': orders,
            'page_name': 'franchise_order_history',
        }
        return request.render("8848_portal.portal_franchise_order_history", values)
        
    @http.route(['/my/orders/<int:order_id>'], type='http', auth="user", website=True)
    def order_details(self, order_id, **kw):
        permitted_ids = request.env.user._get_permitted_franchise_ids('order')
        order = request.env['sale.order'].sudo().browse(order_id)
        if not order.exists() or order.partner_id.id not in permitted_ids:
            return request.redirect('/my/orders')
            
        values = {
            'order': order,
            'page_name': 'franchise_order_details',
        }
        return request.render("8848_portal.portal_franchise_order_details", values)

    @http.route(['/my/orders/<int:order_id>/reorder'], type='http', auth="user", website=True, methods=['POST'])
    def reorder(self, order_id, **kw):
        permitted_ids = request.env.user._get_permitted_franchise_ids('order')
        old_order = request.env['sale.order'].sudo().browse(order_id)
        if not old_order.exists() or old_order.partner_id.id not in permitted_ids:
            return request.redirect('/my/orders')
            
        active_id = old_order.partner_id.id
        request.session['active_franchise_id'] = active_id
        
        draft_order = request.env['sale.order'].sudo().search([
            ('partner_id', '=', active_id),
            ('state', 'in', ['draft', 'sent']),
            ('approval_state', '=', 'draft')
        ], limit=1)
        
        if not draft_order:
            draft_order = request.env['sale.order'].sudo().create({
                'partner_id': active_id,
                'approval_state': 'draft'
            })
            
        for line in old_order.order_line:
            if not line.product_id.is_portal_orderable or not line.product_id.active:
                continue
            
            existing = draft_order.order_line.filtered(lambda l: l.product_id.id == line.product_id.id)
            if existing:
                existing.product_uom_qty += line.product_uom_qty
            else:
                request.env['sale.order.line'].sudo().create({
                    'order_id': draft_order.id,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.product_uom_qty,
                })
                
        return request.redirect('/my/orders/new')

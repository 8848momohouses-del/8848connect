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

        values = {
            'active_franchise': active_franchise,
            'products': products,
            'product_prices': product_prices,
            'page_name': 'franchise_catalogue',
        }
        return request.render("8848_portal.portal_franchise_catalogue", values)

from odoo import http
from odoo.http import request

class FranchisePortal(http.Controller):

    @http.route(['/my/franchise'], type='http', auth="user", website=True)
    def franchise_dashboard(self, **kw):
        # Temporarily redirected until Batch P3 implements the secure dashboard
        return request.redirect('/my')

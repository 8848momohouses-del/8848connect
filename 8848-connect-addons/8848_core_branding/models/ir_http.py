# -*- coding: utf-8 -*-
from odoo import models

class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        result = super(IrHttp, self).session_info()
        # Override the title to remove Odoo branding
        if 'server_version_info' in result:
            result['server_version_info'] = []
        return result

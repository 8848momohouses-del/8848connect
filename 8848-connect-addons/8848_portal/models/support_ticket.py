from odoo import models, fields, api

class SupportTicket(models.Model):
    _name = '8848.support.ticket'
    _description = 'Support Ticket'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Subject', required=True, tracking=True)
    description = fields.Text(string='Description', required=True)
    franchise_id = fields.Many2one('res.partner', string='Franchise', domain=[('is_franchise', '=', True)], required=True, tracking=True)
    user_id = fields.Many2one('res.users', string='Submitted By', default=lambda self: self.env.user, readonly=True)
    
    category = fields.Selection([
        ('order', 'Order Issue'),
        ('delivery', 'Delivery Issue'),
        ('quality', 'Quality Complaint'),
        ('finance', 'Billing & Finance'),
        ('other', 'Other')
    ], string='Category', required=True, tracking=True)
    
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], string='Priority', default='medium', tracking=True)
    
    state = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed')
    ], string='Status', default='new', tracking=True)

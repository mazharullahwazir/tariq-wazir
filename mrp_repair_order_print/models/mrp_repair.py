from odoo import api, fields, models



class Repair(models.Model):
    _inherit = 'repair.order'

    x_assigned_to = fields.Many2one('hr.employee')

    

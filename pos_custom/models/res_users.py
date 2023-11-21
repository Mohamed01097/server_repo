# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    vendor_ids = fields.Many2many('res.partner', string='Assigned Vendors', domain="[('supplier_rank','>',0)]")

    
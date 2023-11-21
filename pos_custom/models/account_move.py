# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    car_id = fields.Many2one('vendor.truck', string=' Vendor Truck')

    
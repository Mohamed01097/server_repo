# -*- coding: utf-8 -*-

from odoo import models, fields


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    is_default = fields.Boolean('Default')
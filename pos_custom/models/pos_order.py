# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PosOrder(models.Model):
    _inherit = 'pos.order'

    car_id = fields.Many2one('vendor.truck', string='Vendor Truck')

    @api.model
    def _order_fields(self, ui_order):
        order_fields = super(PosOrder, self)._order_fields(ui_order)
        car_dict = ui_order.get('car_id', False)
        car_id = car_dict.get('id', False) if car_dict else False
        order_fields['car_id'] = car_id
        return order_fields
    
    def _export_for_ui(self, order):
        result = super(PosOrder, self)._export_for_ui(order)
        result.update({
            'car_id': order.car_id.id,
        })
        return result
    
    def _prepare_invoice_vals(self):
        invoice_vals = super(PosOrder, self)._prepare_invoice_vals()
        invoice_vals['car_id'] = self.car_id.id
        return invoice_vals


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    car_id = fields.Many2one('vendor.truck', related='order_id.car_id')
    partner_id = fields.Many2one('res.partner', related='order_id.partner_id')

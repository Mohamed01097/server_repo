
from odoo import api, fields, models, _
import json


class PosSessionCar(models.TransientModel):
    _name = 'pos.session.car'

    session_id = fields.Many2one(comodel_name="pos.session", string='POS Session')
    car_ids_domain = fields.Char('Cars Domain', compute="_get_cars_domain")
    car_ids = fields.Many2many(comodel_name="vendor.truck", string='Cars')
    
    def get_car_orders(self, orders, car):
        return orders.filtered(lambda order:order.car_id == car)
    
    def check_if_car_has_order_for_pos(self):
        order_lines = self.session_id.order_ids if self.session_id else False
        cars_in_orders = order_lines.mapped('car_id') if order_lines else False
        if cars_in_orders and self.car_ids:
            return any(i in cars_in_orders.ids for i in self.car_ids.ids)
        else:
            return False
    
    @api.depends('session_id')
    def _get_cars_domain(self):
        for rec in self:
            order_lines = rec.session_id.order_ids if rec.session_id else False
            cars_in_orders = order_lines.mapped('car_id') if order_lines else False
            rec.car_ids_domain = json.dumps([('id', 'in', cars_in_orders.ids)]) if cars_in_orders else json.dumps([('id', 'in', [])])
    
    def print_report(self):
        return self.env.ref('pos_custom.eos_car_report').report_action(self)

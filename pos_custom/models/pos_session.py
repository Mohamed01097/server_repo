# -*- coding: utf-8 -*-

from odoo import models
from odoo.addons.point_of_sale.models.pos_session import PosSession


def _get_pos_ui_res_partner_new(self, params):
        if not self.config_id.limited_partners_loading:
            return self.env['res.partner'].search_read(**params['search_params'])
        partner_ids = [res[0] for res in self.config_id.get_limited_partners_loading()]
        # Need to search_read because get_limited_partners_loading
        # might return a partner id that is not accessible.
        params['search_params']['domain'] = [('id', 'in', partner_ids), ('customer_rank', '>', 0)]
        return self.env['res.partner'].search_read(**params['search_params'])

PosSession._get_pos_ui_res_partner = _get_pos_ui_res_partner_new

class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_pos_payment_method(self):
        result = super()._loader_params_pos_payment_method()
        result['search_params']['fields'].append('is_default')
        return result

    def _loader_params_res_partner(self):
        result = super()._loader_params_res_partner()
        result['search_params']['fields'].append('is_combined_invoice')
        result['search_params']['fields'].append('customer_rank')
        # result['search_params']['domain'] = [('customer_rank', '>', 0)]
        return result
    
    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()
        result += [
            'vendor.truck',
        ]
        return result
    
    def _loader_params_vendor_truck(self):
        user_config_vendors = self.env.user.vendor_ids
        trucks = self.env['vendor.truck'].search([])
        empty_trucks = self.env['vendor.truck'].search([('id', 'in', [])])
        if user_config_vendors:
            assigned_trucks = trucks.filtered(lambda t:t.vendor_id.id in user_config_vendors.ids)
            domain_ids = assigned_trucks
        else:
            domain_ids = empty_trucks
        return {
            'search_params': {
                'domain': [('id', 'in', domain_ids.ids)],
                'fields': [
                    'name', 'license', 'type', 'model', 'driver', 'vendor_id', 'work_type'
                ],
            },
        }

    def _get_pos_ui_vendor_truck(self, params):
        return self.env['vendor.truck'].search_read(**params['search_params'])
    
    def get_pos_ui_vendor_truck_by_params(self, custom_search_params):
        """
        :param custom_search_params: a dictionary containing params of a search_read()
        """
        params = self._loader_params_vendor_truck()
        # custom_search_params will take priority
        params['search_params'] = {**params['search_params'], **custom_search_params}
        cars = self.env['vendor.truck'].search_read(**params['search_params'])
        return cars
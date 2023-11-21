from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    # UNSPSC category codes can be used in Mexico.
    all_partners = env['res.partner'].search([])
    all_partners.is_combined_invoice = False

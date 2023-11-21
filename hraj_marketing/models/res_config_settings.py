from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    debit_account_id = fields.Many2one('account.account')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    debit_account_id = fields.Many2one('account.account', related='company_id.debit_account_id', readonly=0, store=0)




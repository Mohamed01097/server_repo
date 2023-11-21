from odoo import models, fields, api


class VendorEmployee(models.Model):
    _name = 'vendor.employee'
    _description = 'VendorEmployee'

    name = fields.Char('اسم الموظف')
    job_position = fields.Char('المنصب الوظيفى')
    phone = fields.Char('رقم الهاتف')
    mobile = fields.Char('رقم الجوال')
    email = fields.Char('الإيميل')
    send_invoice = fields.Boolean('إرسال الفواتير')
    vendor_id = fields.Many2one(
        comodel_name='res.partner', domain="[('supplier_rank','>',0)]")


class ResPartner(models.Model):
    _inherit = 'res.partner'

    employee_ids = fields.One2many(
        comodel_name='vendor.employee',
        inverse_name='vendor_id',
        string='السيارات',
        required=False)

    # cust_type = fields.Selection(
    #     string='نوع العميل',
    #     selection=[('', ''),
    #                ('', ''), ],
    #     required=False, )


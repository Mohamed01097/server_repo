from odoo import models, fields, api


class VendorTruck(models.Model):
    _name = 'vendor.truck'
    _description = 'VendorTruck'

    name = fields.Char('رقم اللوحة')
    license = fields.Char('اسم السائق')
    type = fields.Char('النوع')
    work_type = fields.Selection(
        string='حراج/تسويق',
        selection=[
            ('hraj', 'حراج'),
            ('market', 'تسويق'),
        ],
        required=False, )
    model = fields.Char('الموديل')
    driver = fields.Char(related='driver_id.name', store=True)
    driver_id = fields.Many2one(string='السائق',
        comodel_name='res.partner', domain="[('supplier_rank','>',0)]")
    vendor_id = fields.Many2one(
        comodel_name='res.partner', domain="[('supplier_rank','>',0)]")


class VendorPhone(models.Model):
    _name = 'vendor.phone'
    _description = 'VendorPhone'

    name = fields.Char('رقم الهاتف')
    type = fields.Selection(
        string='نوع الهاتف',
        selection=[
            ('home', 'منزل'),
            ('mobile', 'جوال'),
            ('work', 'عمل'),
        ],
        required=False, )

    vendor_id = fields.Many2one(
        comodel_name='res.partner', domain="[('supplier_rank','>',0)]")


class ResPartner(models.Model):
    _inherit = 'res.partner'

    truck_ids = fields.One2many(
        comodel_name='vendor.truck',
        inverse_name='vendor_id',
        string='السيارات',
        required=False)

    phone_ids = fields.One2many(
        comodel_name='vendor.phone',
        inverse_name='vendor_id',
        string='التليفونات',
        required=False)
    
    is_combined_invoice = fields.Boolean('عميل تجميع فواتير', default=False)
    combine_type = fields.Selection([('noraml', 'عادي'), ('office', 'مكتب')], string='نوع التجميع')
    discount_percent = fields.Float('نسبة الخصم %', digits=(16, 2))


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    pos_orders = fields.One2many('pos.order', 'employee_id')
    customer = fields.Many2one(
        comodel_name='res.partner', domain="[('customer_rank','>',0)]")
    journal = fields.Many2one(
        comodel_name='account.journal')
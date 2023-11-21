from odoo import models, fields, api
import pandas as pd


class Settlement(models.Model):
    _name = 'settlement'
    _description = 'VendorTruck'

    name = fields.Char('رقم مسلسل', default='New', readonly=1)
    date = fields.Date(string='التاريخ', default=lambda s: fields.Date.context_today(s))

    employee = fields.Many2one('hr.employee', string='البائع')
    department = fields.Many2one('hr.department', related='employee.department_id', string='القسم')

    truck = fields.Many2one('vendor.truck', string='السيارة')

    @api.onchange('employee')
    def onchange_employee(self):
        trucks = self.employee.user_id.vendor_ids.mapped('truck_ids')
        return {'domain': {'truck': [('id', 'in', trucks.ids)]}}

    driver_id = fields.Many2one('res.partner', related='truck.driver_id', string='السائق')
    work_type = fields.Selection(related='truck.work_type', string='نوع الخدمة')

    vendor_id = fields.Many2one(comodel_name='res.partner', related='truck.vendor_id')

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')

    commission = fields.Monetary(currency_field='currency_id', readonly=1)

    receivables_ids = fields.One2many('settlement.line', 'settlement_id', readonly=0)
    expenses_ids = fields.One2many('expense.line', 'settlement_id', readonly=0)

    @api.onchange('employee', 'date', 'truck')
    def onchange_method(self):
        self.receivables_ids = [[6, 0, []]]
        self.expenses_ids = [[6, 0, []]]
        expense_lines = [
            (0, 0, {
                'name': 'cash',
                'cost': 0,
                'partner': self.employee.customer.id}),

            (0, 0, {
                'name': 'debit',
                'partner': self.driver_id.id}),

            (0, 0, {
                'name': 'card',
                'partner': self.vendor_id.id}),

            (0, 0, {
                'name': 'operation',
                'partner': self.vendor_id.id}),

            (0, 0, {
                'name': 'other', }),

        ]
        receivables_ids = self.employee.pos_orders.filtered(
            lambda o: o.date_order.date() == self.date and o.car_id == self.truck)
        if receivables_ids:
            lines = receivables_ids.mapped('lines')
            print(lines.mapped('product_id'))
            # Convert lines to DataFrame
            df = pd.DataFrame(
                [(line.product_id.id, line.partner_id.id, line.qty, line.price_unit, line.price_subtotal,
                  line.price_subtotal_incl, line.product_uom_id) for line
                 in lines],
                columns=['product_id', 'partner_id', 'qty', 'price_unit', 'price_subtotal', 'price_subtotal_incl',
                         'product_uom_id'])
            # Group by product_id and price_unit, and calculate sum
            grouped = df.groupby(['product_id', 'partner_id', 'price_unit', 'product_uom_id']).sum().reset_index()

            print(grouped)

            # Create new lines
            new_lines = [(0, 0, {
                'product_id': int(row['product_id']),
                'customer': int(row['partner_id']),
                'qty': row['qty'],
                'product_uom_id': int(row['product_uom_id']),
                'price_unit': row['price_unit'],
                'price_subtotal': row['price_subtotal'],
                'price_subtotal_incl': row['price_subtotal_incl'],
            }) for _, row in grouped.iterrows()]

            self.receivables_ids = new_lines
            self.commission = sum(lines.mapped('price_subtotal_incl'))

            self.expenses_ids = [[6, 0, []]]

            cash_payments = receivables_ids.mapped('payment_ids').filtered(
                lambda p: p.payment_method_id.journal_id.type == 'cash')
            expense_lines = [
                (0, 0, {
                    'name': 'cash',
                    'cost': sum(cash_payments.mapped('amount')),
                    'partner': self.employee.customer.id}),

                (0, 0, {
                    'name': 'debit',
                    'partner': self.driver_id.id}),

                (0, 0, {
                    'name': 'card',
                    'partner': self.vendor_id.id}),

                (0, 0, {
                    'name': 'operation',
                    'partner': self.vendor_id.id}),

                (0, 0, {
                    'name': 'other', }),

            ]
        self.expenses_ids = expense_lines

    def button_create_vendor_bill(self):

        self.bill.invoice_line_ids.sudo().unlink()
        # Prepare Vendor Bill values
        bill_vals = {
            'partner_id': self.vendor_id.id,  # Replace with your vendor field
            'invoice_line_ids': [],
            'car_id': self.truck.id,
            'move_type': 'in_invoice',
        }

        # For each line in receivables_ids, create an invoice line
        for line in self.receivables_ids:
            invoice_line_vals = {
                'product_id': line.product_id.id,
                'vendor_truck_id': self.truck.id,
                'quantity': line.qty,
                'price_unit': line.price_unit,
                'discount': self.vendor_id.discount_percent,
                # 'account_id': line.product_id.property_account_expense_id.id or line.product_id.categ_id.property_account_expense_categ_id.id,

            }
            bill_vals['invoice_line_ids'].append((0, 0, invoice_line_vals))

        # Create Vendor Bill
        if not self.bill:
            self.bill = self.env['account.move'].create(bill_vals)
        else:
            self.bill.write(bill_vals)
        return {
            'name': 'Vendor Bill',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': self.bill.id,
        }

    bill = fields.Many2one('account.move')

    def button_create_driver_card_customer_invoice(self):

        self.invoice.invoice_line_ids.sudo().unlink()

        if self.expenses_ids:
            line = self.expenses_ids.filtered(lambda l: l.name == 'card')
            # Prepare Vendor Bill values
            bill_vals = {
                'partner_id': line.partner.id,  # Replace with your vendor field
                'invoice_line_ids': [],
                'car_id': self.truck.id,
                'move_type': 'out_invoice',
            }

            # For each line in receivables_ids, create an invoice line

            invoice_line_vals = {
                'product_id': self.env.ref('hraj_marketing.product_service_driver_card').id,
                'vendor_truck_id': self.truck.id,
                'quantity': 1,
                'price_unit': line.cost,

            }
            bill_vals['invoice_line_ids'].append((0, 0, invoice_line_vals))

            if not self.invoice:
                self.invoice = self.env['account.move'].create(bill_vals)
            else:
                self.invoice.write(bill_vals)

            return {
                'name': 'Driver Card Invoice',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'account.move',
                'res_id': self.invoice.id,
            }

    invoice = fields.Many2one('account.move')

    def button_create_debit_bill(self):
        self.debit_bill.invoice_line_ids.sudo().unlink()
        if self.expenses_ids:
            line = self.expenses_ids.filtered(lambda l: l.name == 'debit')
            # Prepare Vendor Bill values
            bill_vals = {
                'partner_id': line.partner.id,
                'invoice_line_ids': [],
                'car_id': self.truck.id,
                'move_type': 'in_invoice',
            }

            # For each line in receivables_ids, create an invoice line

            invoice_line_vals = {
                'product_id': self.env.ref('hraj_marketing.product_service_debit').id,
                'vendor_truck_id': self.truck.id,
                'quantity': 1,
                'price_unit': line.cost,

            }
            bill_vals['invoice_line_ids'].append((0, 0, invoice_line_vals))

            # Create Vendor Bill
            if not self.debit_bill:
                self.debit_bill = self.env['account.move'].create(bill_vals)
            else:
                self.debit_bill.write(bill_vals)
#############
            self.debit_entry.line_ids.sudo().unlink()

            # Prepare Vendor Bill values
            debit_account_id = self.env.company.debit_account_id
            if not debit_account_id:
                raise ValueError("No default debit account defined in settings")

            journal = self.employee.journal

            if not journal:
                raise ValueError("No default journal for this employee")

            # Prepare Journal Entry values
            journal_entry_vals = {
                'partner_id': self.vendor_id.id,
                'car_id': self.truck.id,
                'journal_id': journal.id,
                'line_ids': [],
                'move_type': 'entry',
            }

            # Create a Journal Entry line for credit
            journal_entry_line_vals_credit = {
                'name': 'Credit Line',
                'account_id': journal.default_account_id.id,
                'credit': line.cost,
            }
            journal_entry_vals['line_ids'].append((0, 0, journal_entry_line_vals_credit))

            # Create a Journal Entry line for debit
            journal_entry_line_vals_debit = {
                'name': 'Debit Line',
                'account_id': debit_account_id.id,
                'debit': line.cost,
            }
            journal_entry_vals['line_ids'].append((0, 0, journal_entry_line_vals_debit))

            # Create Journal Entry
            if not self.debit_entry:
                self.debit_entry = self.env['account.move'].create(journal_entry_vals)
            else:
                self.debit_entry.write(journal_entry_vals)

            return {
                'name': 'Debit Bill',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'account.move',
                'res_id': self.debit_bill.id,
            }

    debit_bill = fields.Many2one('account.move')
    debit_entry = fields.Many2one('account.move')

    def button_create_operation_entry(self):
        self.operation_entry.line_ids.sudo().unlink()

        if self.expenses_ids:
            line = self.expenses_ids.filtered(lambda l: l.name == 'operation')

            # Prepare Vendor Bill values
            debit_account_id = self.env.company.debit_account_id
            if not debit_account_id:
                raise ValueError("No default debit account defined in settings")

            journal = self.employee.journal

            if not journal:
                raise ValueError("No default journal for this employee")

            # Prepare Journal Entry values
            journal_entry_vals = {
                'partner_id': self.vendor_id.id,
                'car_id': self.truck.id,
                'journal_id': journal.id,
                'line_ids': [],
                'move_type': 'entry',
            }

            # Create a Journal Entry line for credit
            journal_entry_line_vals_credit = {
                'name': 'Credit Line',
                'account_id': journal.default_account_id.id,
                'credit': line.cost,
            }
            journal_entry_vals['line_ids'].append((0, 0, journal_entry_line_vals_credit))

            # Create a Journal Entry line for debit
            journal_entry_line_vals_debit = {
                'name': 'Debit Line',
                'account_id': debit_account_id.id,
                'debit': line.cost,
            }
            journal_entry_vals['line_ids'].append((0, 0, journal_entry_line_vals_debit))

            # Create Journal Entry
            if not self.operation_entry:
                self.operation_entry = self.env['account.move'].create(journal_entry_vals)
            else:
                self.operation_entry.write(journal_entry_vals)

            return {
                'name': 'Debit Bill',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'account.move',
                'res_id': self.operation_entry.id,
            }

    operation_entry = fields.Many2one('account.move')

    def open_related_invoice(self):
        return {
            'name': 'Open Related Invoice',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'domain': [('id', '=', self.invoice.id)],
        }

    def open_related_bill(self):
        return {
            'name': 'Open Related Bill',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'domain': [('id', 'in', [self.debit_bill.id,self.bill.id])],
        }

    def open_related_entries(self):
        return {
            'name': 'Open Related Bill',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', [self.operation_entry.id,self.debit_entry.id])],
        }

    def write(self, values):
        res = super().write(values)
        self.button_create_vendor_bill()
        self.button_create_driver_card_customer_invoice()
        self.button_create_debit_bill()
        self.button_create_operation_entry()
        return res

    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('settlement.code')
        res = super().create(values)
        res.button_create_vendor_bill()
        res.button_create_driver_card_customer_invoice()
        res.button_create_debit_bill()
        res.button_create_operation_entry()
        return res

    seller_total = fields.Float()
    seller_tax = fields.Float()
    seller_balance = fields.Float()

    total_no_tax = fields.Float()
    total_tax = fields.Float()
    commission = fields.Float()
    total_expenses = fields.Float()
    total_final = fields.Float()

    related_moves = fields.Many2many(
        comodel_name='account.move', compute='_compute_related_moves')

    related_entries = fields.Many2many(
        comodel_name='account.move', compute='_compute_related_moves')

    def _compute_related_moves(self):
        for rec in self:
            rec.related_moves = [(6,0, (rec.debit_bill | rec.bill | rec.invoice).ids)]
            rec.related_entries = [(6, 0, (rec.operation_entry | rec.debit_entry).ids)]


class SettlementLine(models.Model):
    _name = 'settlement.line'
    _inherit = 'pos.order.line'

    order_id = fields.Many2one(required=0)
    customer = fields.Many2one('res.partner')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='settlement_id.currency_id')
    price_subtotal = fields.Float(string='Subtotal w/o Tax', digits=0,
                                  readonly=0, required=0)

    price_subtotal_incl = fields.Float(string='Subtotal', digits=0,
                                       readonly=0, required=0)

    settlement_id = fields.Many2one('settlement')

    @api.ondelete(at_uninstall=False)
    def _unlink_except_order_state(self):
        pass

    margin = fields.Monetary(string="Margin", compute=None)
    margin_percent = fields.Float(string="Margin (%)", compute=None, digits=(12, 4))

    @api.onchange('qty', 'discount', 'price_unit', 'tax_ids')
    def _onchange_qty(self):
        if self.product_id:
            # if not self.order_id.pricelist_id:
            #     raise UserError(_('You have to select a pricelist in the sale form.'))
            price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
            self.price_subtotal = self.price_subtotal_incl = price * self.qty
            if (self.tax_ids):
                taxes = self.tax_ids.compute_all(price, self.currency_id, self.qty,
                                                 product=self.product_id, partner=False)
                self.price_subtotal = taxes['total_excluded']
                self.price_subtotal_incl = taxes['total_included']


class ExpenseLine(models.Model):
    _name = 'expense.line'

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')

    name = fields.Selection(string='اسم العهدة', selection=[
        ('cash', 'النقدي'),
        ('debit', 'آجل'),
        ('card', 'كارت'),
        ('operation', 'م. تشغيل'),
        ('other', 'م. أخرى'),
    ], )

    cost = fields.Monetary()
    partner = fields.Many2one('res.partner')
    notes = fields.Text()
    settlement_id = fields.Many2one('settlement')

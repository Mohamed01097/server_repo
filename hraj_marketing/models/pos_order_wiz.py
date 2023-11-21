from odoo import models, fields, api, exceptions


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    vendor_truck_id = fields.Many2one('vendor.truck')


class POSOrder(models.Model):
    _inherit = 'pos.order'

    invoice_id = fields.Many2one('account.move')
    is_invoiced = fields.Boolean()


class POSOrderFilterWizard(models.TransientModel):
    _name = "pos.order.filter.wizard"

    date_from = fields.Date('Date From', required=True, default=lambda s: fields.Date.context_today(s))
    date_to = fields.Date('Date To', required=True, default=lambda s: fields.Date.context_today(s))
    customer_id = fields.Many2one('res.partner', 'Customer', required=0)
    customer_ids = fields.Many2many('res.partner', required=True, relation='hrj_wiz_cust')

    all_customers = fields.Boolean('All Customers')

    @api.onchange('all_customers')
    def _onchange_all_customers(self):
        if self.all_customers:
            self.customer_ids = self.env['res.partner'].search([('customer_rank', '>=', 1)])
        else:
            self.customer_ids = self.env['res.partner']

    def action_filter_and_combine(self):
        # Filter POS orders
        invoices = []
        for customer_id in self.customer_ids:
            if customer_id.is_combined_invoice:
                employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
                pos_orders = self.env['pos.order'].search([
                    ('invoice_id', '=', False),
                    ('state', 'not in', ('draft', 'cancel')),
                    ('date_order', '>=', self.date_from),
                    ('date_order', '<=', self.date_to),
                    ('partner_id', '=', customer_id.id),
                    ('employee_id', '=', employee_id.id)

                ])
            else:
                pos_orders = self.env['pos.order'].search([
                    ('invoice_id', '=', False),
                    ('state', 'not in', ('draft', 'cancel')),
                    ('date_order', '>=', self.date_from),
                    ('date_order', '<=', self.date_to),
                    ('partner_id', '=', customer_id.id),
                ])

            print(pos_orders.mapped('is_invoiced'))

            # Check if we have any pos orders, if not raise an exception
            if not pos_orders:
                raise exceptions.UserError(
                    'No POS orders to be invoiced in the selected date range for the selected customer.')

            # Create invoice
            invoice_vals = {
                'partner_id': customer_id.id,
                'invoice_date': fields.Date.context_today(self),
                'move_type': 'out_invoice',
                'invoice_line_ids': [],
            }

            # Create invoice lines from POS orders
            for pos_order in pos_orders:
                for line in pos_order.lines:
                    invoice_line_vals = {
                        'name': line.product_id.name,
                        'quantity': line.qty,
                        'price_unit': line.price_unit,
                        'product_id': line.product_id.id,
                        'vendor_truck_id': line.car_id.id,
                    }
                    invoice_vals['invoice_line_ids'].append((0, 0, invoice_line_vals))

            # Create the invoice
            invoice = self.env['account.move'].create(invoice_vals)

            # You might want to automatically post the invoice
            invoice.action_post()
            invoices.append((invoice.id))

            pos_orders.sudo().write({'invoice_id': invoice.id})

        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'res_model': 'account.move',
            'domain': [('id', 'in', invoices)],
            'view_mode': 'tree,form',
            'target': 'current',
        }

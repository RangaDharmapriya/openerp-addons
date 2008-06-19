###############################################################################
##
## Copyright (c) 2005-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
##
## WARNING: This program as such is intended to be used by professional
## programmers who take the whole responsability of assessing all potential
## consequences resulting from its eventual inadequacies and bugs
## End users who are looking for a ready-to-use solution with commercial
## garantees and support are strongly adviced to contract a Free Software
## Service Company
##
## This program is Free Software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License
## as published by the Free Software Foundation; either version 2
## of the License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
##
###############################################################################

import time
from report import report_sxw
from osv import osv


class pos_details(report_sxw.rml_parse):

	def _get_qty_total(self, objects):
		#code for the sum of qty_total
		return reduce(lambda acc, object:
										acc + reduce(
												lambda sum_qty, line:
														sum_qty + line.qty,
												object.lines,
												0 ),
									objects,
									0)

	def _get_sum_discount(self, objects):
		#code for the sum of discount value
		return reduce(lambda acc, object:
										acc + reduce(
												lambda sum_dis, line:
														sum_dis + ((line.price_unit * line.qty ) * (line.discount / 100)),
												object.lines,
												0.0),
									objects,
									0.0 )

	def _get_payments(self, objects):
		result = {}
		for o in objects:
			for p in o.payments:
				result[p.journal_id.name] = result.get(p.journal_id.name, 0.0) + p.amount
		return result

	def _paid_total(self, objects):
		return sum(self._get_payments(objects).values(), 0.0)

	def _sum_invoice(self, objects):
		return reduce(lambda acc, obj:
												acc + obj.invoice_id.amount_total,
									[o for o in objects if o.invoice_id and o.invoice_id.number],
									0.0)

	def _ellipsis(self, string, maxlen=100, ellipsis = '...'):
		ellipsis = ellipsis or ''
		return string[:maxlen - len(ellipsis) ] + (ellipsis, '')[len(string) < maxlen]

	def _strip_name(self, name, maxlen=50):
		return self._ellipsis(name, maxlen, ' ...')

	def _get_tax_amount(self, objects):
		res = {}
		list_ids=[]
		for order in objects:
			for line in order.lines:
				if len(line.product_id.taxes_id):
					tax = line.product_id.taxes_id[0]
					res[tax.name] = (line.price_unit * line.qty * (1-(line.discount or 0.0) / 100.0)) + (tax.id in list_ids and res[tax.name] or 0)
					list_ids.append(tax.id)
		return res

	def _get_sales_total(self, objects):
		return reduce(lambda x, o: x + len(o.lines), objects, 0)

	def _get_period(self, objects):
		date_orders = [object.date_order for object in objects]
		min_date = min(date_orders)
		max_date = max(date_orders)
		if min_date == max_date:
			return '%s' % min_date
		else:
			return '%s - %s' % (min_date, max_date)

	def __init__(self, cr, uid, name, context):
		super(pos_details, self).__init__(cr, uid, name, context)
		self.total = 0.0
		self.localcontext.update({
			'time': time,
			'strip_name': self._strip_name,
			'getpayments': self._get_payments,
			'getqtytotal': self._get_qty_total,
			'getsumdisc': self._get_sum_discount,
			'getpaidtotal': self._paid_total,
			'getsuminvoice': self._sum_invoice,
			'gettaxamount': self._get_tax_amount,
			'getsalestotal': self._get_sales_total,
			'getperiod': self._get_period,
		})

report_sxw.report_sxw('report.pos.details', 'pos.order', 'addons/point_of_sale/report/pos_details.rml', parser=pos_details, header=None)


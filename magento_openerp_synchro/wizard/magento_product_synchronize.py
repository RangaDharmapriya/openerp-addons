# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008 Smile S.A. (http://www.smile.fr) All Rights Reserved.
# Copyright (c) 2009 Zikzakmedia S.L. (http://www.zikzakmedia.com) All Rights Reserved.
# @authors: Sylvain Pamart, Raphaël Valyi, Jordi Esteve
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import wizard
import pooler


def do_export(self, cr, uid, data, context):

    self.pool = pooler.get_pool(cr.dbname)
    product_pool = self.pool.get('product.product')
    return product_pool.do_export(cr, uid, data, context)


#===============================================================================
#   Wizard Declaration
#===============================================================================

_export_done_form = '''<?xml version="1.0"?>
<form string="Product and Stock Synchronization">
    <separator string="Products exported" colspan="4" />
    <field name="prod_new"/>
    <field name="prod_update"/>
    <field name="prod_fail"/>
</form>'''

_export_done_fields = {
    'prod_new': {'string':'New products', 'readonly': True, 'type':'integer'},
    'prod_update': {'string':'Updated products', 'readonly': True, 'type':'integer'},
    'prod_fail': {'string':'Failed to export products', 'readonly': True, 'type':'integer'},
}

class wiz_magento_product_synchronize(wizard.interface):
    states = {
        'init': {
            'actions': [do_export],
            'result': {'type': 'form', 'arch': _export_done_form, 'fields': _export_done_fields, 'state': [('end', 'End')] }
        }
    }
wiz_magento_product_synchronize('magento.products.sync');

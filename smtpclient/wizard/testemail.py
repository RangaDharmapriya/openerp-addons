##############################################################################
#
# Copyright (c) 2005-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
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

form = '''<?xml version="1.0"?>
<form string="Test Email">
    <field name="emailto" colspan="4"/>
</form>'''

fields = {
    'emailto': {'string': 'Email Address', 'required':True, 'size': 255 , 'type': 'char', 'help': 'Enter email on which address you want to get the Verifiation Code'}
}

class testemail(wizard.interface):
    
    def send_code(self, cr, uid, data, context):
        smtpserver = pooler.get_pool(cr.dbname).get('email.smtpclient').browse(cr, uid, data['id'], context)
        state = smtpserver.test_verivy_email(cr, uid, [data['id']], data['form']['emailto'], test=True)
        if not state:
            raise Exception, 'Verification Failed, Please check the Server Configuration!!!'
        return {}
    
    states = {
        'init': {
            'actions': [],
            'result': {'type':'form', 'arch':form, 'fields':fields, 'state':[('end','Cancel'),('send','Send Email')]}
        },
        'send': {
            'actions': [send_code],
            'result': {'type':'state', 'state':'end'}
        }
    }
testemail('email.testemail')



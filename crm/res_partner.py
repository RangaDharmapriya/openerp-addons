# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields,osv

class res_partner(osv.osv):
    """ Inherits partner and adds CRM information in the partner form """
    _inherit = 'res.partner'

    def _opportunity_meeting_count(self, cr, uid, ids, field_name, arg, context=None):
        res = dict(map(lambda x: (x,{'opportunity_count': 0, 'meeting_count': 0}), ids))
        # the user may not have access rights for opportunities or meetings
        try:
            for partner in self.browse(cr, uid, ids, context):
                res[partner.id] = {
                    'opportunity_count': len(partner.opportunity_ids),
                    'meeting_count': len(partner.meeting_ids),
                }
        except:
            pass
        return res

    def _opportunities_stat_button(self, cr, uid, ids, field_name, arg, context=None):
        html = "<div><strong>%s</strong> opportunities</div>"
        return {partner.id: html % len(partner.opportunity_ids) for partner in self.browse(cr, uid, ids, context)}
        res = {}

    def _meetings_stat_button(self, cr, uid, ids, field_name, arg, context=None):
        html = "<div><strong>%s</strong> meetings</div>"
        return {partner.id: html % len(partner.meeting_ids) for partner in self.browse(cr, uid, ids, context)}

    def _calls_stat_button(self, cr, uid, ids, field_name, arg, context=None):
        html = "<div><strong>%s</strong> calls</div>"
        return {partner.id: html % len(partner.phonecall_ids) for partner in self.browse(cr, uid, ids, context)}

    _columns = {
        'section_id': fields.many2one('crm.case.section', 'Sales Team'),
        'opportunity_ids': fields.one2many('crm.lead', 'partner_id',\
            'Leads and Opportunities', domain=[('probability', 'not in', ['0', '100'])]),
        'opportunities_stat_button': fields.function(_opportunities_stat_button, string="Opportunities", type='html'),
        'meeting_ids': fields.many2many('calendar.event', 'calendar_event_res_partner_rel','res_partner_id', 'calendar_event_id',
            'Meetings'),
        'meetings_stat_button': fields.function(_meetings_stat_button, string="Meetings", type='html'),
        'phonecall_ids': fields.one2many('crm.phonecall', 'partner_id',\
            'Phonecalls'),
        'calls_stat_button': fields.function(_calls_stat_button, string="Calls", type='html'),
        'opportunity_count': fields.function(_opportunity_meeting_count, string="Opportunity", type='integer', multi='opp_meet'),
        'meeting_count': fields.function(_opportunity_meeting_count, string="# Meetings", type='integer', multi='opp_meet'),
    }

    def copy(self, cr, uid, record_id, default=None, context=None):
        if default is None:
            default = {}

        default.update({'opportunity_ids': [], 'meeting_ids' : [], 'phonecall_ids' : []})

        return super(res_partner, self).copy(cr, uid, record_id, default, context)

    def redirect_partner_form(self, cr, uid, partner_id, context=None):
        search_view = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'base', 'view_res_partner_filter')
        value = {
            'domain': "[]",
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'res.partner',
            'res_id': int(partner_id),
            'view_id': False,
            'context': context,
            'type': 'ir.actions.act_window',
            'search_view_id': search_view and search_view[1] or False
        }
        return value

    def make_opportunity(self, cr, uid, ids, opportunity_summary, planned_revenue=0.0, probability=0.0, partner_id=None, context=None):
        categ_obj = self.pool.get('crm.case.categ')
        categ_ids = categ_obj.search(cr, uid, [('object_id.model','=','crm.lead')])
        lead_obj = self.pool.get('crm.lead')
        opportunity_ids = {}
        for partner in self.browse(cr, uid, ids, context=context):
            if not partner_id:
                partner_id = partner.id
            opportunity_id = lead_obj.create(cr, uid, {
                'name' : opportunity_summary,
                'planned_revenue' : planned_revenue,
                'probability' : probability,
                'partner_id' : partner_id,
                'categ_ids' : categ_ids and categ_ids[0:1] or [],
                'type': 'opportunity'
            }, context=context)
            opportunity_ids[partner_id] = opportunity_id
        return opportunity_ids


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

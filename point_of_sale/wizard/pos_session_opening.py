#!/usr/bin/env python

from osv import osv, fields
from tools.translate import _
import netsvc

class pos_session_opening(osv.osv_memory):
    _name = 'pos.session.opening'

    _columns = {
        'pos_config_id' : fields.many2one('pos.config', 'Point of Sale', required=True),
        'pos_session_id' : fields.many2one('pos.session', 'PoS Session'),
        'pos_state' : fields.char('Session State'),
    }

    def open_ui(self, cr, uid, ids, context=None):
        context = context or {}
        data = self.browse(cr, uid, ids[0], context=context)
        context['active_id'] = data.pos_session_id.id
        return {
            'type' : 'ir.actions.client',
            'name' : 'Start Point Of Sale',
            'tag' : 'pos.ui',
            'context' : context
        }

    def open_existing_session_cb_close(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        wizard = self.browse(cr, uid, ids[0], context=context)
        wf_service.trg_validate(uid, 'pos.session', wizard.pos_session_id.id, 'cashbox_control', cr)
        return self.open_session_cb(cr, uid, ids, context)

    def open_session_cb(self, cr, uid, ids, context=None):
        assert len(ids) == 1, "you can open only one session at a time"
        proxy = self.pool.get('pos.session')
        wizard = self.browse(cr, uid, ids[0], context=context)
        if not wizard.pos_session_id:
            values = {
                'user_id' : uid,
                'config_id' : wizard.pos_config_id.id,
            }
            session_id = proxy.create(cr, uid, values, context=context)
            return self._open_session(session_id)
        return self._open_session(wizard.pos_session_id.id)

    def open_existing_session_cb(self, cr, uid, ids, context=None):
        assert len(ids) == 1
        wizard = self.browse(cr, uid, ids[0], context=context)
        return self._open_session(wizard.pos_session_id.id)

    def _open_session(self, session_id):
        return {
            'name': _('Session'),
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'pos.session',
            'res_id': session_id,
            'view_id': False,
            'type': 'ir.actions.act_window',
        }

    def on_change_config(self, cr, uid, ids, config_id, context=None):
        result = {
            'pos_session_id': False,
            'pos_state': False
        }
        if not config_id:
            return {'value': result}
        proxy = self.pool.get('pos.session')
        session_ids = proxy.search(cr, uid, [
            ('state', '<>', 'closed'),
            ('config_id', '=', config_id),
        ], context=context)
        if session_ids:
            result['pos_state'] = proxy.browse(cr, uid, session_ids[0], context=context).state
            result['pos_session_id'] = session_ids[0]
        return {'value' : result}

    def default_get(self, cr, uid, fieldnames, context=None):
        so = self.pool.get('pos.session')
        session_ids = so.search(cr, uid, [('state','<>','closed'), ('user_id','=',uid)], context=context)
        if session_ids:
            result = so.browse(cr, uid, session_ids[0], context=context).config_id.id
        else:
            current_user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
            result = current_user.pos_config and current_user.pos_config.id or False
        if not result:
            r = self.pool.get('pos.config').search(cr, uid, [], context=context)
            result = r and r[0] or False
        return {
            'pos_config_id' : result
        }
pos_session_opening()

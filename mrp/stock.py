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

from openerp.osv import fields
from openerp.osv import osv


class StockMove(osv.osv):
    _inherit = 'stock.move'
    
    _columns = {
        'production_id': fields.many2one('mrp.production', 'Production', select=True),
    }

    
    def _action_explode(self, cr, uid, move, context=None):
        """ Explodes pickings.
        @param move: Stock moves
        @return: True
        """
        bom_obj = self.pool.get('mrp.bom')
        move_obj = self.pool.get('stock.move')
        procurement_obj = self.pool.get('procurement.order')
        product_obj = self.pool.get('product.product')
        processed_ids = [move.id]
 
        bis = bom_obj.search(cr, uid, [
            ('product_id','=',move.product_id.id),
            ('bom_id','=',False),
            ('type','=','phantom')])
        if bis:
            factor = move.product_qty
            bom_point = bom_obj.browse(cr, uid, bis[0], context=context)
            res = bom_obj._bom_explode(cr, uid, bom_point, factor, [])
            state = 'confirmed'
            if move.state == 'assigned':
                state = 'assigned'
            for line in res[0]: 
                valdef = {
                    'picking_id': move.picking_id.id,
                    'product_id': line['product_id'],
                    'product_uom': line['product_uom'],
                    'product_qty': line['product_qty'],
                    'product_uos': line['product_uos'],
                    'product_uos_qty': line['product_uos_qty'],
                    'move_dest_id': move.id,
                    'state': state,
                    'name': line['name'],
                    'procurements': [],
                }
                mid = move_obj.copy(cr, uid, move.id, default=valdef)
                processed_ids.append(mid)
                prodobj = product_obj.browse(cr, uid, line['product_id'], context=context)
                proc_id = procurement_obj.create(cr, uid, {
                    'name': (move.picking_id.origin or ''),
                    'origin': (move.picking_id.origin or ''),
                    'date_planned': move.date,
                    'product_id': line['product_id'],
                    'product_qty': line['product_qty'],
                    'product_uom': line['product_uom'],
                    'product_uos_qty': line['product_uos'] and line['product_uos_qty'] or False,
                    'product_uos':  line['product_uos'],
                    'location_id': move.location_id.id,
                    'procure_method': prodobj.procure_method,
                    'move_id': mid,
                })
                procurement_obj.signal_button_confirm(cr, uid, [proc_id])
                
            move_obj.write(cr, uid, [move.id], {
                'location_dest_id': move.location_id.id, # dummy move for the kit
                'picking_id': False,
                'state': 'confirmed'
            })
            procurement_ids = procurement_obj.search(cr, uid, [('move_id','=',move.id)], context)
            procurement_obj.signal_button_confirm(cr, uid, procurement_ids)
            procurement_obj.signal_button_wait_done(cr, uid, procurement_ids)
        return processed_ids
    
    def action_consume(self, cr, uid, ids, product_qty, location_id=False, context=None):
        """ Consumed product with specific quatity from specific source location.
        @param product_qty: Consumed product quantity
        @param location_id: Source location
        @return: Consumed lines
        """       
        res = []
        production_obj = self.pool.get('mrp.production')
        for move in self.browse(cr, uid, ids):
            move.action_confirm(context)
            new_moves = super(StockMove, self).action_consume(cr, uid, [move.id], product_qty, location_id, context=context)
            production_ids = production_obj.search(cr, uid, [('move_lines', 'in', [move.id])])
            for prod in production_obj.browse(cr, uid, production_ids, context=context):
                if prod.state == 'confirmed':
                    production_obj.force_production(cr, uid, [prod.id])
            production_obj.signal_button_produce(cr, uid, production_ids)
            for new_move in new_moves:
                if new_move == move.id:
                    #This move is already there in move lines of production order
                    continue
                production_obj.write(cr, uid, production_ids, {'move_lines': [(4, new_move)]})
                res.append(new_move)
        return res
    
    def action_scrap(self, cr, uid, ids, product_qty, location_id, context=None):
        """ Move the scrap/damaged product into scrap location
        @param product_qty: Scraped product quantity
        @param location_id: Scrap location
        @return: Scraped lines
        """  
        res = []
        production_obj = self.pool.get('mrp.production')
        for move in self.browse(cr, uid, ids, context=context):
            new_moves = super(StockMove, self).action_scrap(cr, uid, [move.id], product_qty, location_id, context=context)
            #If we are not scrapping our whole move, tracking and lot references must not be removed
            production_ids = production_obj.search(cr, uid, [('move_lines', 'in', [move.id])])
            for prod_id in production_ids:
                production_obj.signal_button_produce(cr, uid, [prod_id])
            for new_move in new_moves:
                production_obj.write(cr, uid, production_ids, {'move_lines': [(4, new_move)]})
                res.append(new_move)
        return res


    def write(self, cr, uid, ids, vals, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = super(StockMove, self).write(cr, uid, ids, vals, context=context)
        from openerp import workflow
        for move in self.browse(cr, uid, ids, context=context):
            if move.production_id and move.production_id.state == 'confirmed':
                workflow.trg_trigger(uid, 'stock.move', move.production_id.id, cr)
        return res

class StockPicking(osv.osv):
    _inherit = 'stock.picking'

    #
    # Explode picking by replacing phantom BoMs
    #
    def action_explode(self, cr, uid, move_ids, *args):
        """Explodes moves by expanding kit components"""
        move_obj = self.pool.get('stock.move')
        todo = move_ids[:]
        for move in move_obj.browse(cr, uid, move_ids):
            todo.extend(move_obj._action_explode(cr, uid, move))
        return list(set(todo))



class split_in_production_lot(osv.osv_memory):
    _inherit = "stock.move.split"

    def split(self, cr, uid, ids, move_ids, context=None):
        """ Splits move lines into given quantities.
        @param move_ids: Stock moves.
        @return: List of new moves.
        """
        new_moves = super(split_in_production_lot, self).split(cr, uid, ids, move_ids, context=context)
        production_obj = self.pool.get('mrp.production')
        production_ids = production_obj.search(cr, uid, [('move_lines', 'in', move_ids)])
        production_obj.write(cr, uid, production_ids, {'move_lines': [(4, m) for m in new_moves]})
        return new_moves


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

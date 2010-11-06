# -*- encoding: utf-8 -*-
########################################################################
#
#   OOOP, OpenObject On Python
#   Copyright (C) 2010 Impulzia S.L. All Rights Reserved.
#   Gamaliel Toro <argami@impulzia.com>
#   $Id$
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
########################################################################

from osv import osv, fields
from ooop import OOOP

class impulzia_ooop(osv.osv_memory):
    """ OOOP."""
    _name = "impulzia.ooop"
    _description = "ooop wrapper to bypass the orm"
    
    def get(self, *args):
        return self._ooop = OOOP(parent=args[0], cr=args[1], uid=args[2])
    

impulzia_ooop()

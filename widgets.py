# Copyright (c) 2006 Nuxeo SAS <http://nuxeo.com>
# Authors:
# - Anahide Tchertchian <at@nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
#-------------------------------------------------------------------------------
# $Id$
#-------------------------------------------------------------------------------
"""CPSComment widgets definitions.
"""

from Globals import InitializeClass

from Products.CPSSchemas.Widget import widgetRegistry
from Products.CPSSchemas.BasicWidgets import CPSCompoundWidget


class CommentHeaderWidget(CPSCompoundWidget):
    """Comment Header widget
    """
    meta_type = 'Comment Header Widget'
    render_method = 'widget_comment_header_render'

InitializeClass(CommentHeaderWidget)

widgetRegistry.register(CommentHeaderWidget)

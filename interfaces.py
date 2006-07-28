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
"""CPSComment interfaces
"""

import zope.interface

from Products.CMFCore.interfaces import IDiscussionResponse
from Products.CMFCore.interfaces import IDiscussable
from Products.CMFCore.interfaces import IDiscussionTool
from Products.CPSRelation.interfaces import IPrefixedResource

class IComment(IDiscussionResponse, IDiscussable):
    """Interface for comment
    """

class ICommentResource(IPrefixedResource):
    """Interface for comment resource

    Local name has to be an integer
    """

class ICommentTool(IDiscussionTool):
    """Interface for the comment tool
    """

class IDiscussableContent(zope.interface.Interface):
    """Interface for discussable document
    """

    content = zope.interface.Attribute("Original content")

    def overrideDiscussionFor(allowDiscussion):
        """Override discussability or clear the setting.
        """

    def isDiscussionAllowedFor():
        """Get boolean indicating whether discussion is allowed.
        """

    def isDiscussable():
        """Return True if can be discussed
        """

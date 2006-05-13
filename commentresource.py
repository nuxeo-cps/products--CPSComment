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
"""Comment resource to be used in relations
"""

import zope.interface

from Products.CPSRelation.resourceregistry import ResourceRegistry
from Products.CPSRelation.node import PrefixedResource

from Products.CPSComment.interfaces import IComment
from Products.CPSComment.interfaces import ICommentResource


class CommentResource(PrefixedResource):
    """Comment Resource
    """

    zope.interface.implements(ICommentResource)
    prefix = 'comment'

    def __init__(self, localname):
        self.localname = localname
        self.uri = self.prefix + ':' + self.localname


ResourceRegistry.register(CommentResource)


# adapter

@zope.component.adapter(IComment)
@zope.interface.implementer(ICommentResource)
def getCommentResource(comment):
    """return a CommentResource from an IComment
    """
    return CommentResource(localname=comment.getId())

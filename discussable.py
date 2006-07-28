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
"""Discussable object to ease integration with new types of discussable content
"""

from logging import getLogger

import zope.interface

from OFS.interfaces import IItem
from AccessControl import Unauthorized
from Acquisition import aq_base

from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName

from Products.CPSCore.interfaces import ICPSProxy
from Products.CPSDocument.interfaces import ICPSDocument
from Products.CPSComment.interfaces import IDiscussableContent
from Products.CPSComment.permissions import AddComment

logger = getLogger("CPSComment.discussable")


class NotDiscussable(object):
    """Not discussable content
    """

    zope.interface.implements(IDiscussableContent)

    def __init__(self, content):
        """Init
        """
        self.content = content

    def overrideDiscussionFor(self, allowDiscussion):
        """Do nothing
        """
        logger.error("overrideDiscussionFor: %s is not discussable"%(
            self.content,))

    def isDiscussable(self):
        """Return False
        """
        return False

    def isDiscussionAllowedFor(self):
        """Return False
        """
        return False


class DiscussableDocument(object):
    """Discussable document
    """

    zope.interface.implements(IDiscussableContent)

    def __init__(self, document):
        """Init
        """
        self.content = document

    def overrideDiscussionFor(self, allowDiscussion):
        """Override discussability or clear the setting.
        """
        content = self.content
        if not _checkPermission(ModifyPortalContent, content):
            raise Unauthorized("Cannot modify object %s"%(content,))

        if allowDiscussion is None or allowDiscussion == 'None':
            if hasattr(aq_base(content), 'allow_discussion'):
                del content.allow_discussion
            else:
                logger.error("Could not disable discussion on %s"%(content,))
        else:
            content.allow_discussion = bool(allowDiscussion)

    def isDiscussionAllowedFor(self):
        """Get boolean indicating whether discussion is allowed.
        """
        allow = False
        content = self.content
        # check permission to add comments in general
        if _checkPermission(AddComment, content):
            if hasattr(aq_base(content), 'allow_discussion'):
                # check permission to add comment on content
                allow = bool(content.allow_discussion)
            else:
                # check permission to add comment on content type
                type_info = content.getTypeInfo()
                if type_info:
                    allow = bool(type_info.allowDiscussion())
                else:
                    logger.error("allow_discussion not found for %s"%(content,))
        return allow

    def isDiscussable(self):
        """Return True if can be discussed
        """
        return True


class DiscussableProxy(object):
    """Discussable document
    """

    zope.interface.implements(IDiscussableContent)

    def __init__(self, document):
        """Init
        """
        self.content = document

    def overrideDiscussionFor(self, allowDiscussion):
        """Override discussability or clear the setting.
        """
        content = self.content
        if not _checkPermission(ModifyPortalContent, content):
            raise Unauthorized("Cannot modify object %s"%(content,))

        document = content.getContent()
        if allowDiscussion is None or allowDiscussion == 'None':
            if hasattr(aq_base(document), 'allow_discussion'):
                del document.allow_discussion
            else:
                logger.error("Could not disable discussion on %s"%(document,))
        else:
            document.allow_discussion = bool(allowDiscussion)

    def isDiscussionAllowedFor(self):
        """Get boolean indicating whether discussion is allowed.
        """
        allow = False
        content = self.content
        # check permission to add comments in general
        if _checkPermission(AddComment, content):
            document = content.getContent()
            if hasattr(aq_base(document), 'allow_discussion'):
                # check permission to add comment on content
                allow = bool(document.allow_discussion)
            else:
                # check permission to add comment on content type
                type_info = document.getTypeInfo()
                if type_info:
                    allow = bool(type_info.allowDiscussion())
                else:
                    logger.error("allow_discussion not found for %s"%(document,))
        return allow

    def isDiscussable(self):
        """Return True
        """
        return True


# adapters


@zope.component.adapter(IItem)
@zope.interface.implementer(IDiscussableContent)
def getNotDiscussable(content):
    """Return IDiscussableContent from IItem
    """
    return NotDiscussable(content)

# XXX AT: comment is a document too
@zope.component.adapter(ICPSDocument)
@zope.interface.implementer(IDiscussableContent)
def getDocumentDiscussable(document):
    """Return IDiscussableContent from ICPSDocument
    """
    return DiscussableDocument(document)

@zope.component.adapter(ICPSProxy)
@zope.interface.implementer(IDiscussableContent)
def getProxyDiscussable(proxy):
    """Return IDiscussableContent from ICPSProxy
    """
    return DiscussableProxy(proxy)

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
"""Discussable objects for capsule documents
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

from nuxeo.capsule.interfaces import IDocument as ICapsuleDocument
from nuxeo.capsule.interfaces import IProxy as ICapsuleProxy

logger = getLogger("CPSComment.capsule.discussable")

class DiscussableCapsuleDocument(object):
    """Discussable document
    """

    zope.interface.implements(IDiscussableContent)

    property_name = 'dc:allowDiscussion'

    def __init__(self, document):
        """Init
        """
        self.content = document


    def overrideDiscussionFor(self, allowDiscussion):
        """Override discussability or clear the setting.
        """
        content = self.content
        if (not _checkPermission(ModifyPortalContent, content)
            # take care of frozen documents
            or content.isReadOnly()):
            raise Unauthorized("Cannot modify object %s"%(content,))

        if (not allowDiscussion
            or allowDiscussion is None
            or allowDiscussion == 'None'):
            try:
                content.setProperty(self.property_name, False)
            except KeyError:
                logger.error("%s property not found for %s"%
                             (self.property_name, content,))
        else:
            try:
                content.setProperty(self.property_name, True)
            except KeyError:
                logger.error("%s property not found for %s"%
                             (self.property_name, content,))


    def isDiscussionAllowedFor(self):
        """Get boolean indicating whether discussion is allowed.
        """
        allow = False
        content = self.content
        # check permission to add comments in general
        if _checkPermission(AddComment, content):
            if content.hasProperty(self.property_name):
                allow = bool(content.getProperty(self.property_name))
            else:
                # check permission to add comment on content type
                type_info = content.getTypeInfo()
                if type_info:
                    allow = bool(type_info.allowDiscussion())
                else:
                    logger.error("%s property not found for %s"%
                                 (self.property_name, content,))
        return allow


    def isDiscussable(self):
        """Return True if can be discussed
        """
        return True


class DiscussableCapsuleProxy(object):
    """Discussable proxy
    """

    zope.interface.implements(IDiscussableContent)

    property_name = 'dc:allowDiscussion'

    def __init__(self, proxy):
        """Init
        """
        self.content = proxy


    def overrideDiscussionFor(self, allowDiscussion):
        """Override discussability or clear the setting.
        """
        # cannot be changed, proxy points to a frozen document
        pass


    def isDiscussionAllowedFor(self):
        """Get boolean indicating whether discussion is allowed.
        """
        allow = False
        content = self.content
        # check permission to add comments in general
        if _checkPermission(AddComment, content):
            document = content.getContent()
            if document.hasProperty(self.property_name):
                allow = bool(document.getProperty(self.property_name))
            else:
                # check permission to add comment on content type
                type_info = document.getTypeInfo()
                if type_info:
                    allow = bool(type_info.allowDiscussion())
                else:
                    logger.error("%s property not found for %s"%
                                 (self.property_name, document,))
        return allow


    def isDiscussable(self):
        """Return True if can be discussed
        """
        return True


# adapters

@zope.component.adapter(ICapsuleDocument)
@zope.interface.implementer(IDiscussableContent)
def getCapsuleDocumentDiscussable(document):
    """Return IDiscussableContent from ICapsuleDocument
    """
    return DiscussableCapsuleDocument(document)


@zope.component.adapter(ICapsuleProxy)
@zope.interface.implementer(IDiscussableContent)
def getCapsuleProxyDiscussable(proxy):
    """Return IDiscussableContent from ICapsuleProxy
    """
    return DiscussableCapsuleProxy(proxy)

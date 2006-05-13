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

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo, Unauthorized
from Acquisition import aq_parent, aq_inner, aq_base

import zope.interface

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ModifyPortalContent

from Products.CPSRelation.node import PrefixedResource
from Products.CPSRelation.statement import Statement

from Products.CPSDocument.CPSDocument import CPSDocument

from Products.CPSComment.interfaces import IComment
from Products.CPSComment.permissions \
     import AddComment, ViewComment, EditComment, DeleteComment


COMMENT_PORTAL_TYPE = 'Comment'

class Comment(CPSDocument):
    """A CPSDocument following the Discussable interface
    """

    meta_type = 'CPS Comment'
    portal_type = COMMENT_PORTAL_TYPE

    zope.interface.implements(IComment)

    security = ClassSecurityInfo()

    # DiscussionResponse interface methods

    security.declareProtected(ViewComment, 'inReplyTo')
    def inReplyTo(self, REQUEST=None):
        """Return the Discussable object which this item is associated with

        Permissions: ViewComment
        Returns: a Discussable object or None
        """
        comment = None
        ctool = getToolByName(self, 'portal_comment')
        self_resource = ctool._getCommentResource(self)
        graph = ctool._getCommentGraph()
        comment_resources = graph.getSubjects(
            PrefixedResource('cps', 'hasReply'), self_resource)
        proxy = self.getProxy()
        for comment_resource in comment_resources:
            comment_id = comment_resource.localname
            try:
                comment = ctool.getComment(comment_id, proxy)
            except Unauthorized:
                pass
            else:
                # return only the first one found
                break

        return comment


    security.declareProtected(EditComment, 'setReplyTo')
    def setReplyTo(self, reply_to):
        """Make this object a response to the passed object.

        reply_to is a comment.

        Permissions: EditComment
        Returns: None
        """
        ctool = getToolByName(self, 'portal_comment')
        proxy = self.getProxy()
        if ctool._isCommentOf(reply_to, proxy):
            statement = Statement(ctool._getCommentResource(reply_to),
                                  PrefixedResource('cps', 'hasReply'),
                                  ctool._getCommentResource(self))
            graph = ctool._getCommentGraph()
            graph.add([statement])
            # XXX see if other reply relations have to be deleted for this
            # object


    security.declareProtected(ViewComment, 'parentsInThread')
    def parentsInThread(self, size=0):
        """Return the list of object which are this object's parents.

        Parents are parents from the point of view of the threaded
        discussion. They are ordered oldest to newest.

        If 'size' is not zero, only the closest 'size' parents will be
        returned.
        """
        parents = []
        current = self
        while not size or len(parents) < size:
            parent = current.inReplyTo()
            if parent is None:
                break
            assert not parent in parents  # sanity check
            parents.insert(0, parent)
            if parent.meta_type != self.meta_type:
                break
            current = parent
        return parents


    # Discussable interface methods

    security.declareProtected(AddComment, 'createReply')
    def createReply(self, title, text, Creator=None, **kw):
        """Create a reply in the proper place
        """
        ctool = getToolByName(self, 'portal_comment')
        kw.update({
            'title': title,
            'text': text,
            })
        if Creator is not None:
            kw['Creator'] = Creator

        proxy = self.getProxy()
        comment_id = ctool.createComment(proxy,
                                         self.portal_type,
                                         reply_to=self,
                                         **kw)
        return comment_id


    security.declareProtected(ViewComment, 'getReplies')
    def getReplies(self):
        """Return a sequence of comments objects which are replies to this one
        """
        ctool = getToolByName(self, 'portal_comment')
        reply_ids = self._getReplyResults()
        replies = []
        proxy = self.getProxy()
        for reply_id in reply_ids:
            try:
                reply = ctool.getComment(reply_id, proxy)
            except Unauthorized:
                pass
            else:
                replies.append(reply)
        return replies


    security.declareProtected(ViewComment, 'quotedContents')
    def quotedContents(self):
        """Return this object's contents in a form suitable for inclusion as a
        quote in a response.
        """
        ctool = getToolByName(self, 'portal_comment')
        proxy = self.getProxy()
        return ctool.getQuotedContents(self, proxy)


    security.declareProtected(ViewComment, '_getReplyResults')
    def _getReplyResults(self):
        """Get a list of ids of comments which are replies to this one

        No security checks are done
        """
        ctool = getToolByName(self, 'portal_comment')
        graph = ctool._getCommentGraph()
        resources = graph.getObjects(ctool._getCommentResource(self),
                                     PrefixedResource('cps', 'hasReply'))
        reply_ids = [resource.localname for resource in resources]
        return reply_ids


    security.declareProtected(ViewComment, 'getProxy')
    def getProxy(self):
        """Get proxy this comment is related to

        comment is wrapped in the proxy context so just take it parent
        """
        return aq_parent(aq_inner(self))


    # do no index comments, overload CMFCatalogAware related methods inherited
    # by CPSDocument.

    security.declareProtected(ModifyPortalContent, 'indexObject')
    def indexObject(self):
        """Index the object in the portal catalog: skipped
        """
        pass

    security.declareProtected(ModifyPortalContent, 'unindexObject')
    def unindexObject(self):
        """Unindex the object from the portal catalog: skipped
        """
        pass

    security.declareProtected(ModifyPortalContent, 'reindexObject')
    def reindexObject(self, idxs=[]):
        """Reindex the object in the portal catalog: skipped.

        Notify the document id modified so that specific metadata are computed
        (modification date, creator, for instance)
        """
        if idxs == []:
            # Update the modification date.
            if hasattr(aq_base(self), 'notifyModified'):
                self.notifyModified()

    security.declareProtected(ModifyPortalContent, 'reindexObjectSecurity')
    def reindexObjectSecurity(self, skip_self=False):
        """Reindex security-related indexes on the object: skipped.
        """
        pass


InitializeClass(Comment)


def addComment(container, id, REQUEST=None, **kw):
    """Factory method
    """

    instance = Comment(id, **kw)
    container._setObject(id, instance)

    if REQUEST:
        object = container._getOb(id)
        REQUEST.RESPONSE.redirect(object.absolute_url() + '/manage_main')

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

import sys
import random
import logging

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo, Unauthorized
from Acquisition import aq_base

from zope.interface import implements

from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.permissions import ModifyPortalContent, View
from Products.CMFCore.CMFBTreeFolder import CMFBTreeFolder
from Products.CMFCore.ActionProviderBase import ActionProviderBase

from Products.CPSCore.CPSTypes import TypeConstructor, TypeContainer
from Products.CPSCore.interfaces import ICPSProxy
from Products.CPSCore.EventServiceTool import getEventService

from Products.CPSRelation.interfaces import IVersionResource
from Products.CPSRelation.interfaces import IVersionHistoryResource
from Products.CPSRelation.node import PrefixedResource
from Products.CPSRelation.statement import Statement

from Products.CPSComment.permissions import ViewComment
from Products.CPSComment.permissions import EditComment
from Products.CPSComment.permissions import DeleteComment
from Products.CPSComment.interfaces import IComment
from Products.CPSComment.interfaces import ICommentTool
from Products.CPSComment.interfaces import IDiscussableContent
from Products.CPSComment.comment import Comment
from Products.CPSComment.commentresource import getCommentResource


logger = logging.getLogger('CPSComment.CommentTool')

class CommentTool(UniqueObject, TypeConstructor, TypeContainer,
                  CMFBTreeFolder, ActionProviderBase):
    """Comment Tool following the CMF IDiscussionTool interface
    """
    id = 'portal_comment'
    # do not use 'CPS Discussion Tool' because it is used by CPSForum
    meta_type = 'CPS Comment Tool'

    implements(ICommentTool)

    security = ClassSecurityInfo()

    _properties = (
        {'id': 'graph_id', 'type': 'string', 'mode': 'w',
         'label': "Relations graph id",
         },
        # XXX AT: this will not work using IOBTree graphs, because we only have
        # the docid to identify a document -> will not be possible to attach
        # comment to a specifi version
        {'id': 'comment_version', 'type': 'boolean', 'mode': 'w',
         'label': "Comment a document version (Redland needed)",
         },
        )
    graph_id = 'CPSComment'
    comment_version = False

    def __init__(self):
        CMFBTreeFolder.__init__(self, self.id)

    # Interface methods

    security.declareProtected(View, 'overrideDiscussionFor')
    def overrideDiscussionFor(self, content, allowDiscussion):
        """Override discussability for the given object or clear the setting.
        """
        discussable = IDiscussableContent(content)
        return discussable.overrideDiscussionFor(allowDiscussion)


    security.declareProtected(View, 'getDiscussionFor')
    def getDiscussionFor(self, content):
        """Get DiscussionItemContainer for content, create it if necessary.
        """
        raise NotImplementedError


    security.declareProtected(View, 'isDiscussionAllowedFor')
    def isDiscussionAllowedFor(self, content):
        """Get boolean indicating whether discussion is allowed for content.
        """
        discussable = IDiscussableContent(content)
        return discussable.isDiscussionAllowedFor()

    # API

    # relations management

    security.declarePrivate('_getCommentGraph')
    def _getCommentGraph(self):
        """Get the graph used to store comments relations
        """
        rtool = getToolByName(self, 'portal_relations')
        return rtool.getGraph(self.graph_id)


    security.declarePrivate('_getProxyResource')
    def _getProxyResource(self, proxy):
        """Get the resource to use for proxies
        """
        if self.comment_version:
            resource = IVersionResource(proxy)
        else:
            resource = IVersionHistoryResource(proxy)
        return resource


    security.declarePrivate('_getCommentResource')
    def _getCommentResource(self, comment):
        """Get the resource to use for comments
        """
        return getCommentResource(comment)


    # comments management

    security.declarePrivate('_getFreeCommentId')
    def _getFreeCommentId(self, proposed_id=None):
        """Get a free comment id to use in relations

        Comment ids have to be integers, they're chosen among free repository
        docids so that there is no collision between proxies and comments
        unique identifiers.
        """
        otool = getToolByName(self, 'portal_repository')
        # accept a given id for tests
        if (proposed_id
            and proposed_id.isdigit()
            and not otool.keyRange(proposed_id+'__0001',
                                   proposed_id+'__9999')
            and not self.has_key(proposed_id)):
            return proposed_id

        while 1:
            comment_id = otool.getFreeDocid()
            if not self.has_key(comment_id):
                return comment_id


    security.declarePrivate('_getWrappedComment')
    def _getWrappedComment(self, comment, proxy):
        """Get comment wrapped into the proxy context
        """
        #logger.debug("comment=%s, proxy=%s"%(comment, proxy))
        comment = aq_base(comment).__of__(proxy)
        if not _checkPermission(ViewComment, comment):
            raise Unauthorized("Cannot view comment %s"%(comment,))
        if not self._isCommentOf(comment, proxy):
            # XXX add a manager bypass?
            raise Unauthorized("Comment %s is not a comment of proxy %s"%
                               (comment, proxy))
        return comment


    security.declarePrivate('isCommentOf')
    def _isCommentOf(self, comment, proxy):
        """Check if comment is a comment of given proxy
        """
        graph = self._getCommentGraph()
        statement = Statement(self._getProxyResource(proxy),
                              PrefixedResource('cps', 'hasComment'),
                              self._getCommentResource(comment))
        return graph.hasStatement(statement)


    security.declareProtected(View, 'isDiscussable')
    def isDiscussable(self, object):
        """Return True if given object is a proxy
        """
        discussable = IDiscussableContent(object)
        return discussable.isDiscussable()


    security.declarePrivate('_getComment')
    def _getComment(self, comment_id):
        """Get comment with given comment_id
        """
        try:
            comment = self._getOb(str(comment_id))
        except KeyError, err:
            raise KeyError("Comment not found: %s" %(err,))
        return comment


    security.declareProtected(View, 'getComment')
    def getComment(self, comment_id, proxy):
        """Get comment with given comment_id, wrapped into the proxy context
        """
        comment = self._getComment(comment_id)
        comment = self._getWrappedComment(comment, proxy)
        return comment


    security.declareProtected(View, 'createComment')
    def createComment(self, proxy, ptype_id, reply_to=None, **kw):
        """Create a comment of the given proxy

        ptype_id is the portal type to use for comments.
        reply_to is the optional comment this comment is an answer of (thread
        information).
        Attributes representing the comment are passed as keywords.
        """
        if not self.isDiscussionAllowedFor(proxy):
            raise Unauthorized("Discussion not allowed on %s"%(proxy,))

        # check that this comment is already linked to the given proxy
        reply = None
        if reply_to is not None:
            if not self._isCommentOf(reply_to, proxy):
                # add log at info level
                reply = None
            else:
                reply = reply_to

        if kw.has_key('id'):
            comment_id = self._getFreeCommentId(proposed_id=kw['id'])
            del kw['id']
        else:
            comment_id = self._getFreeCommentId()
        comment_id = self.invokeFactory(ptype_id, comment_id, **kw)
        comment = self._getComment(comment_id)

        # relations
        comment_resource = self._getCommentResource(comment)
        statements = [
            Statement(self._getProxyResource(proxy),
                      PrefixedResource('cps', 'hasComment'),
                      comment_resource),
            ]
        if reply is not None:
            statements.append(Statement(self._getCommentResource(reply),
                                        PrefixedResource('cps', 'hasReply'),
                                        comment_resource))
        graph = self._getCommentGraph()
        graph.add(statements)

        # XXX old-style comment id, we will trigger a Zope 3 Interface when
        # CPSSubscriptions is compatible with it
        evtool = getEventService(self)
        evtool.notify('comment_created', proxy, {})

        return str(comment_id)


    security.declareProtected(View, 'editComment')
    def editComment(self, comment, proxy, **kw):
        """Edit given comment

        Validate the comment and write to it if it's valid.
        Optional kw are passed to the CPSDocument validate method.

        Return the validation boolean.
        """
        comment = self._getWrappedComment(comment, proxy)
        if not _checkPermission(EditComment, comment):
            raise Unauthorized("Cannot modify comment %s"%(comment,))
        # validate it in its own context, otherwise catalog will index it with
        # a wrong path
        comment = self._getComment(comment.getId())
        is_valid, ds = comment.validate(**kw)
        return is_valid


    security.declarePrivate('_deleteCommentRelations')
    def _deleteCommentRelations(self, comment):
        """Delete the comment relations without security checks
        """
        resource = self._getCommentResource(comment)
        graph = self._getCommentGraph()
        statements = graph.getStatements(
            Statement(None, None, resource))
        statements += graph.getStatements(
            Statement(resource, None, None))
        graph.remove(statements)


    # XXX make sure this method is called when deleting a comment...
    security.declareProtected(View, 'deleteComment')
    def deleteComment(self, comment_id, proxy):
        """Delete the given comment
        """
        try:
            comment = self.getComment(comment_id, proxy)
        except KeyError:
            # comment not found
            pass
        else:
            if not _checkPermission(DeleteComment, comment):
                raise Unauthorized("Cannot delete comment %s"%(comment,))
            self.manage_delObjects(comment.getId())


    security.declareProtected(View, 'getQuotedContents')
    def getQuotedContents(self, comment, proxy):
        """Get quoted contents for given comment wrapped in the proxy
        context
        """
        comment = self._getWrappedComment(comment, proxy)
        # if cluster does not exist, the default comment view is returned (html
        # output)
        quoted = comment.render(layout_mode='view', cluster='quoted')
        return quoted


    security.declareProtected(View, 'getComments')
    def getComments(self, proxy, sorted=True, sort_on='CreationDate',
                    reverse=False, limit=0):
        """Get comments for given proxy
        """
        comments = []
        if self.isDiscussable(proxy):
            graph = self._getCommentGraph()
            comment_resources = graph.getObjects(
                self._getProxyResource(proxy),
                PrefixedResource('cps', 'hasComment'))
            # the comment resource local name is its id
            loop = 0
            for comment_resource in comment_resources:
                comment_id = comment_resource.localname
                try:
                    comment = self.getComment(comment_id, proxy)
                except Unauthorized:
                    pass
                else:
                    comments.append(comment)
                    loop += 1
                    if limit and not sorted and loop >= limit:
                        break
        if sorted:
            def comment_sortkey(comment):
                info = getattr(aq_base(comment), sort_on, comment.getId())
                if callable(info):
                    info = info()
                return info
            comments.sort(key=comment_sortkey)
            if reverse:
                comments.reverse()
            if limit:
                comments = comments[:limit]
        return comments


    security.declareProtected(View, 'getCommentsThreaded')
    def getCommentsThreaded(self, proxy):
        """Get comments for given proxy, threaded
        """
        raise NotImplementedError


    # XXX AT: to refactor
    security.declarePrivate('_cleanCommentsOf')
    def _cleanCommentsOf(self, proxy):
        """Clean comments related to proxy

        Useful when receiving notifications of proxy deletion
        """
        proxy_resource = self._getProxyResource(proxy)
        if self.comment_version:
            # only delete comments for given proxy
            proxies = [proxy]
        else:
            # check first that no other proxies with this docid exist
            capsule = False
            try:
                from nuxeo.capsule.interfaces import IDocument
            except ImportError, err:
                if sys.exc_info()[2].tb_next is not None:
                    # ImportError was caused deeper
                    raise
            else:
                if IDocument.providedBy(proxy):
                    capsule = True
            if capsule:
                # FIXME AT: need to get all proxies for this version history +
                # workspace document
                proxies = [proxy]
            else:
                pxtool = getToolByName(self, 'portal_proxies')
                proxies = pxtool.listProxies(proxy_resource.docid)

        if len(proxies) <= 1:
            # delete only isolated comments related to this one
            comments = self.getComments(proxy, sorted=False)
            for comment in comments:
                graph = self._getCommentGraph()
                comment_resource = self._getCommentResource(comment)
                graph.remove([Statement(
                    proxy_resource,
                    PrefixedResource('cps', 'hasComment'),
                    comment_resource)])
                other = Statement(None,
                                  PrefixedResource('cps', 'hasComment'),
                                  comment_resource)
                if not graph.getStatements(other):
                    self.manage_delObjects(comment.getId())


    # BBB, Zope3 events are used now
    security.declarePrivate('notify_event')
    def notify_event(self, event_type, object, infos):
        """Standard event hook.
        """
        pass


    # ZMI

    manage_options = (CMFBTreeFolder.manage_options[:1] +
                      ActionProviderBase.manage_options +
                      CMFBTreeFolder.manage_options[1:])


InitializeClass(CommentTool)

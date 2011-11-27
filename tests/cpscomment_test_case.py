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
"""CPSComment unit test case
"""


from Testing.ZopeTestCase import ZopeTestCase

from Acquisition import aq_base

from Products.Five import zcml

from Products.CPSDefault.tests.CPSTestCase import CPSZCMLLayer
from Products.CPSRelation.relationtool import RelationTool
from Products.CPSRelation.interfaces import IVersionHistoryResource
from Products.CPSRelation.node import PrefixedResource
from Products.CPSRelation.statement import Statement

from Products.CPSComment.commenttool import CommentTool
from Products.CPSComment.comment import Comment
from Products.CPSComment.commentresource import CommentResource
from Products.CPSComment.permissions \
     import AddComment, ViewComment, EditComment, DeleteComment

from Products.CPSComment.tests.fake import FakeDocument
from Products.CPSComment.tests.fake import FakeTypesTool
from Products.CPSComment.tests.fake import FakeWorkflowTool
from Products.CPSComment.tests.fake import FakeProxyTool
from Products.CPSComment.tests.fake import FakeRepositoryTool

COMMENT_PERMISSIONS = [
    AddComment,
    ViewComment,
    EditComment,
    DeleteComment,
    ]


class CPSCommentTestCase(ZopeTestCase):

    layer = CPSZCMLLayer

    def setUp(self):
        ZopeTestCase.setUp(self)

        # setup needed permissions on portal
        self.setRoles('Manager')
        self.setPermissions(COMMENT_PERMISSIONS, role='Manager')

        # setup needed tools
        # comments
        self.folder._setObject(CommentTool.id, CommentTool())
        self.ctool = getattr(self.folder, CommentTool.id)
        # relations
        self.folder._setObject(RelationTool.id, RelationTool())
        self.rtool = getattr(self.folder, RelationTool.id)
        # initialize CPSRelation adapters configuration
        zcml.load_site()
        graph_id = 'CPSComment'
        self.rtool.addGraph(graph_id, 'IOBTree Graph')
        self.graph = self.rtool.getGraph(graph_id)
        self.graph.addRelation('hasComment', prefix='cps',
                               subject_prefix='docid',
                               object_prefix='comment')
        self.graph.addRelation('hasReply', prefix='cps',
                               subject_prefix='comment',
                               object_prefix='comment')
        # other useful tools
        self.folder._setObject(FakeTypesTool.id, FakeTypesTool())
        self.folder._setObject(FakeWorkflowTool.id, FakeWorkflowTool())
        self.folder._setObject(FakeProxyTool.id, FakeProxyTool())
        self.folder._setObject(FakeRepositoryTool.id, FakeRepositoryTool())


        # add content
        document_id = 'document'
        doc = FakeDocument(document_id, docid='123')
        self.folder._setObject(document_id, doc)
        self.document = getattr(self.folder, document_id)
        # mark id as used in repository
        self.folder.portal_repository._tree['123__0001'] = None

        # add two comments in the comment tool
        comment_id = '1'
        comment = Comment(comment_id, title='comment', text='my comment')
        self.ctool._setObject(comment_id, comment)
        comment = getattr(self.ctool, comment_id)
        self.comment = aq_base(comment).__of__(self.document)

        reply_id = '2'
        reply = Comment(reply_id, title='reply', text='my reply')
        self.ctool._setObject(reply_id, reply)
        reply = getattr(self.ctool, reply_id)
        self.reply = aq_base(reply).__of__(self.document)


    def _addTestRelations(self):
        statements = [
            Statement(IVersionHistoryResource(self.document),
                      PrefixedResource('cps', 'hasComment'),
                      CommentResource('1')),
            Statement(IVersionHistoryResource(self.document),
                      PrefixedResource('cps', 'hasComment'),
                      CommentResource('2')),
            Statement(CommentResource('1'),
                      PrefixedResource('cps', 'hasReply'),
                      CommentResource('2')),
            ]
        self.graph.add(statements)
        return statements

    def tearDown(self):
        ZopeTestCase.tearDown(self)
        del self.rtool
        del self.ctool
        del self.document
        del self.comment
        del self.reply

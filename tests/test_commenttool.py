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
"""Tests for the commenttool module.
"""

import unittest

from AccessControl import Unauthorized
from Acquisition import aq_inner, aq_parent

from zope.interface.verify import verifyClass

from Products.CMFCore.interfaces import IDiscussionTool

from Products.CPSRelation.interfaces import IVersionHistoryResource
from Products.CPSRelation.node import VersionHistoryResource
from Products.CPSRelation.node import PrefixedResource
from Products.CPSRelation.statement import Statement

from Products.CPSComment.commenttool import CommentTool
from Products.CPSComment.comment import Comment, COMMENT_PORTAL_TYPE
from Products.CPSComment.commentresource import CommentResource
from Products.CPSComment.tests.cpscomment_test_case import CPSCommentTestCase
from Products.CPSComment.tests.fake import FakeDocument

class TestCommentTool(CPSCommentTestCase):

    # fixture

    def setUp(self):
        CPSCommentTestCase.setUp(self)

    # tests

    def test_interface(self):
        verifyClass(IDiscussionTool, CommentTool)

    def test_creation(self):
        ctool = CommentTool()
        self.assertEquals(ctool.getId(), 'portal_comment')
        self.assertEquals(ctool.meta_type, 'CPS Comment Tool')

    def test_test_case_tool(self):
        self.assert_(isinstance(self.ctool, CommentTool))
        self.assertEquals(self.ctool.getId(), 'portal_comment')
        self.assertEquals(self.ctool.meta_type, 'CPS Comment Tool')

    def test_overrideDiscussionFor_document(self):
        self.assertEquals(hasattr(self.document, 'allow_discussion'), False)
        type_info = self.document.getTypeInfo()
        self.assertEquals(type_info.allowDiscussion(), True)
        self.assertEquals(self.ctool.isDiscussionAllowedFor(self.document),
                          False)
        # allow discussion on document
        self.ctool.overrideDiscussionFor(self.document, True)
        self.assertEquals(self.ctool.isDiscussionAllowedFor(self.document),
                          True)
        self.assertEquals(hasattr(self.document, 'allow_discussion'), True)
        self.assertEquals(self.document.allow_discussion, True)

    def test_overrideDiscussionFor_comment(self):
        self.assertEquals(hasattr(self.comment, 'allow_discussion'), False)
        type_info = self.comment.getTypeInfo()
        self.assertEquals(type_info.allowDiscussion(), True)
        self.assertEquals(self.ctool.isDiscussionAllowedFor(self.comment),
                          True)
        # do not allow discussion on comment
        self.ctool.overrideDiscussionFor(self.comment, False)
        self.assertEquals(self.ctool.isDiscussionAllowedFor(self.comment),
                          False)
        self.assertEquals(hasattr(self.comment, 'allow_discussion'), True)
        self.assertEquals(self.comment.allow_discussion, False)

    def test_getDiscussionFor(self):
        self.assertRaises(NotImplementedError,
                          self.ctool.getDiscussionFor,
                          self.document)

    def test_isDiscussionAllowedFor(self):
        self.assertEquals(self.ctool.isDiscussionAllowedFor(self.comment),
                          True)
        self.assertEquals(self.ctool.isDiscussionAllowedFor(self.document),
                          False)
        # allow discussion on it
        self.ctool.overrideDiscussionFor(self.document, True)
        self.assertEquals(self.ctool.isDiscussionAllowedFor(self.document),
                          True)

    def test__getCommentGraph(self):
        self.assertEquals(self.ctool._getCommentGraph(),
                          self.graph)

    def test__getProxyResource(self):
        self.assertEquals(self.ctool._getProxyResource(self.document),
                          VersionHistoryResource('123'))

    def test__getCommentResource(self):
        self.assertEquals(self.ctool._getCommentResource(self.comment),
                          CommentResource('1'))

    def checkFreeCommentId(self, comment_id):
        self.assertEquals(comment_id.isdigit(), True)
        self.assertEquals(self.ctool.has_key(comment_id), False)
        self.assertEquals(self.folder.portal_repository.has_key(comment_id), False)

    def test__getFreeCommentId(self):
        free_id = self.ctool._getFreeCommentId()
        self.checkFreeCommentId(free_id)

    def test__getFreeCommentId_proposed_id(self):
        # valid id
        proposed_id = '666'
        free_id = self.ctool._getFreeCommentId(proposed_id=proposed_id)
        self.assertEquals(free_id, proposed_id)
        self.checkFreeCommentId(free_id)

        # invalid: it's already a proxy docid
        proposed_id = '123'
        free_id = self.ctool._getFreeCommentId(proposed_id=proposed_id)
        self.assertNotEquals(free_id, proposed_id)
        self.checkFreeCommentId(free_id)

    def test__getComment(self):
        self._addTestRelations()
        comment = self.ctool._getComment(1)
        self.assertEquals(comment, self.comment)
        # test it is not wrapped in the proxy context
        self.assertEquals(comment.getProxy(), self.ctool)
        self.assertEquals(aq_inner(aq_parent(comment)), self.ctool)

    def test_getComment(self):
        self._addTestRelations()
        comment = self.ctool.getComment(1, self.document)
        self.assertEquals(comment,
                          self.comment)
        # test it is wrapped in the proxy context
        self.assertEquals(comment.getProxy(), self.document)
        self.assertEquals(aq_inner(aq_parent(comment)), self.document)

        # test to get it wrapped in another document context
        self.assertRaises(Unauthorized,
                          self.ctool.getComment, 1, FakeDocument('truc'))

    def test_isDiscussable(self):
        self.assertEquals(self.ctool.isDiscussable(self.document), True)
        self.assertEquals(self.ctool.isDiscussable(self.comment), True)
        self.assertEquals(self.ctool.isDiscussable(self. folder), False)

    def test__isCommentOf(self):
        self._addTestRelations()
        self.assertEquals(self.ctool._isCommentOf(self.comment, self.document),
                          True)
        self.assertEquals(self.ctool._isCommentOf(self.reply, self.document),
                          True)
        self.assertEquals(self.ctool._isCommentOf(self.comment,
                                                  FakeDocument('truc')),
                          False)

    def test_createComment(self):
        self._addTestRelations()
        self.assertEquals(self.ctool.getComments(self.document),
                          [self.comment, self.reply])
        self.assertEquals(list(self.ctool.objectIds()), ['1', '2'])
        self.assertRaises(Unauthorized,
                          self.ctool.createComment,
                          self.document,
                          COMMENT_PORTAL_TYPE,
                          reply_to=self.reply)
        # allow discussion on related document
        self.ctool.overrideDiscussionFor(self.document, True)
        new_comment_id = self.ctool.createComment(
            self.document, COMMENT_PORTAL_TYPE, reply_to=self.reply)
        self.assertEquals(new_comment_id.isdigit(), True)
        comment_ids = ['1', '2', new_comment_id]
        comment_ids.sort()
        self.assertEquals(list(self.ctool.objectIds()), comment_ids)
        new_comment = self.ctool.getComment(new_comment_id, self.document)
        self.assertEquals(self.ctool._isCommentOf(new_comment, self.document),
                          True)
        self.assertEquals(self.ctool.getComments(self.document),
                          [self.comment, self.reply, new_comment])
        self.assert_(isinstance(new_comment, Comment))
        self.assertEquals(new_comment.portal_type, COMMENT_PORTAL_TYPE)
        self.assertEquals(new_comment.inReplyTo(), self.reply)


    # XXX see functional tests for that
    #def test_editComment(self):

    def test_getComments(self):
        self._addTestRelations()
        self.assertEquals(self.ctool.getComments(self.document),
                          [self.comment, self.reply])

    def test_deleteComment(self):
        self._addTestRelations()
        comment_resource = CommentResource('1')
        self.assertEquals(self.graph.containsResource(comment_resource),
                          True)
        self.assertEquals(self.graph.getObjects(
            comment_resource, PrefixedResource('cps', 'hasReply')),
                          [CommentResource('2')])
        self.assertEquals(self.graph.getSubjects(
            PrefixedResource('cps', 'hasComment'), comment_resource),
                          [VersionHistoryResource('123')])
        self.assertEquals(list(self.ctool.objectIds()), ['1', '2'])
        self.ctool.deleteComment('1', self.document)
        # check no reference left in the graph
        self.assertEquals(self.graph.containsResource(comment_resource),
                          False)
        # check document is actually deleted
        self.assertEquals(list(self.ctool.objectIds()), ['2'])


    def test__cleanCommentsOf(self):
        # delete a document that has a shared comment
        statements = self._addTestRelations()
        # set reply as comment for another document
        document_id = 'document2'
        doc = FakeDocument(document_id, docid='1234')
        self.folder._setObject(document_id, doc)
        statement = Statement(IVersionHistoryResource(doc),
                              PrefixedResource('cps', 'hasComment'),
                              CommentResource('2'))
        self.graph.add([statement])
        all_statements = self.graph.getStatements()
        all_statements.sort()
        expected = statements + [statement]
        expected.sort()
        self.assertEquals(all_statements, expected)
        self.assertEquals(list(self.ctool.objectIds()), ['1', '2'])

        self.ctool._cleanCommentsOf(self.document)

        # check no reference left in the graph
        self.assertEquals(self.graph.getStatements(), [statement])
        # check comment is deleted and reply is not (still linked to a doc)
        self.assertEquals(list(self.ctool.objectIds()), ['2'])


    def test_notify_event_delete_document(self):
        expected = self._addTestRelations()
        expected.sort()
        all_statements = self.graph.getStatements()
        all_statements.sort()
        self.assertEquals(all_statements, expected)
        self.assertEquals(list(self.ctool.objectIds()), ['1', '2'])

        self.ctool.notify_event('sys_del_object', self.document, {})

        # check no reference left in the graph
        self.assertEquals(self.graph.getStatements(), [])
        self.assertEquals(list(self.ctool.objectIds()), [])


    def test_notify_event_delete_document_shared_comment(self):
        # delete a document that has a shared comment
        statements = self._addTestRelations()
        # set reply as comment for another document
        document_id = 'document2'
        doc = FakeDocument(document_id, docid='1234')
        self.folder._setObject(document_id, doc)
        statement = Statement(IVersionHistoryResource(doc),
                              PrefixedResource('cps', 'hasComment'),
                              CommentResource('2'))
        self.graph.add([statement])
        all_statements = self.graph.getStatements()
        all_statements.sort()
        expected = statements + [statement]
        expected.sort()
        self.assertEquals(all_statements, expected)
        self.assertEquals(list(self.ctool.objectIds()), ['1', '2'])

        self.ctool.notify_event('sys_del_object', self.document, {})

        # check no reference left in the graph
        self.assertEquals(self.graph.getStatements(), [statement])
        # check comment is deleted and reply is not (still linked to a doc)
        self.assertEquals(list(self.ctool.objectIds()), ['2'])

    def test_notify_event_delete_comment(self):
        # suppose comment has been deleted without using the deleteComment
        # method
        expected = self._addTestRelations()
        expected.sort()
        all_statements = self.graph.getStatements()
        all_statements.sort()
        self.assertEquals(all_statements, expected)
        self.assertEquals(list(self.ctool.objectIds()), ['1', '2'])

        self.ctool.notify_event('sys_del_object', self.reply, {})

        # check no reference left in the graph
        self.assertEquals(self.graph.getStatements(), [
            Statement(VersionHistoryResource('123'),
                      PrefixedResource('cps', 'hasComment'),
                      CommentResource('1')),
            ])
        # comment is deleted
        self.assertEquals(list(self.ctool.objectIds()), ['1'])

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCommentTool))
    return suite

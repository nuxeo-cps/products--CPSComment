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
"""Tests for the comment module.
"""

import unittest

from AccessControl import Unauthorized

from zope.interface.verify import verifyClass

from Products.CMFCore.interfaces import IDiscussionResponse, IDiscussable

from Products.CPSComment.tests.cpscomment_test_case import CPSCommentTestCase
from Products.CPSComment.comment import Comment, COMMENT_PORTAL_TYPE

class TestComment(CPSCommentTestCase):

    # fixture

    def setUp(self):
        CPSCommentTestCase.setUp(self)
        self._addTestRelations()

    # tests

    def test_interface(self):
        verifyClass(IDiscussionResponse, Comment)
        verifyClass(IDiscussable, Comment)

    def test_creation(self):
        comment = Comment('4', title='comment', text='my comment')
        self.assertEquals(comment.getId(), '4')
        self.assertEquals(comment.portal_type, COMMENT_PORTAL_TYPE)

    def test_test_case_comment(self):
        self.assertEquals(self.comment.getId(), '1')
        self.assert_(isinstance(self.comment, Comment))
        self.assertEquals(self.comment.portal_type, COMMENT_PORTAL_TYPE)

    def test_inReplyTo(self):
        self.assertEquals(self.comment.inReplyTo(), None)
        self.assertEquals(self.reply.inReplyTo(), self.comment)

    def test_setReplyTo(self):
        self.assertEquals(self.comment.inReplyTo(), None)
        self.comment.setReplyTo(self.reply)
        self.assertEquals(self.comment.inReplyTo(), self.reply)

    def test_parentsInThread(self):
        # XXX: test size if this useful...
        self.assertEquals(self.comment.parentsInThread(), [])
        self.assertEquals(self.reply.parentsInThread(), [self.comment])

    def test_createReply(self):
        self.assertEquals(list(self.ctool.objectIds()), ['1', '2'])
        self.ctool.overrideDiscussionFor(self.document, False)
        self.assertRaises(Unauthorized,
                          self.comment.createReply,
                          title='truc', text='machin')
        # allow discussion on related document
        self.ctool.overrideDiscussionFor(self.document, True)
        reply_id = self.comment.createReply(title='truc', text='machin')
        comment_ids = ['1', '2', reply_id]
        comment_ids.sort()
        self.assertEquals(list(self.ctool.objectIds()), comment_ids)
        reply = self.ctool.getComment(reply_id, self.document)
        self.assertEquals(reply.inReplyTo(), self.comment)

    def test_getReplies(self):
        self.assertEquals(self.comment.getReplies(), [self.reply])
        self.assertEquals(self.reply.getReplies(), [])

    #def test_quotedContents(self):
    #    # XXX this has to be changed...
    #    self.assertEquals(self.comment.quotedContents(), "")

    def test__getReplyResults(self):
        self.assertEquals(self.comment._getReplyResults(), ['2'])
        self.assertEquals(self.reply._getReplyResults(), [])

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestComment))
    return suite

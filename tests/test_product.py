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
"""Test the product installation
"""

import unittest

from Products.CMFCore.utils import getToolByName

from Products.CPSComment.tests.cpscomment_ftest_case import CPSCommentFTestCase
from Products.CPSComment.commenttool import CommentTool
from Products.CPSComment.comment import COMMENT_PORTAL_TYPE

class CPSCommentTests(CPSCommentFTestCase):

    def afterSetUp(self):
        CPSCommentFTestCase.afterSetUp(self)
        self.ctool = getToolByName(self.portal, CommentTool.id)

    def test_comment_tool(self):
        self.assert_(isinstance(self.ctool, CommentTool))
        self.assertEquals(self.ctool.id, CommentTool.id)
        self.assertEquals(self.ctool.meta_type, CommentTool.meta_type)

    def test_default_relations(self):
        rtool = getToolByName(self.portal, 'portal_relations', None)
        self.assertNotEquals(rtool, None)
        graph = rtool.getGraph('CPSComment')
        self.assertEquals(graph.meta_type, 'IOBTree Graph')
        relation_ids = [
            'hasComment',
            'hasReply',
            ]
        self.assertEquals(graph.listRelationIds(), relation_ids)

    def test_createComment(self):
        self.login('manager')
        # allow discussion on related document
        document = self.portal.workspaces
        self.ctool.overrideDiscussionFor(document, True)
        new_comment_id = self.ctool.createComment(document, COMMENT_PORTAL_TYPE)
        new_comment = self.ctool.getComment(new_comment_id, document)
        self.assertEquals(new_comment.portal_type, COMMENT_PORTAL_TYPE)
        wftool = self.portal.portal_workflow
        self.assertEquals(wftool.getInfoFor(new_comment, 'review_state'),
                          'visible')

    # XXX AT: currently broken using capsule: default configuration using an
    # IOBTreeGraph does not do the trick
    def test_discussable_objects(self):
        portal = self.portal
        ws = self.portal.workspaces
        self.assertEquals(self.ctool.isDiscussable(portal), False)
        self.assertEquals(self.ctool.isDiscussable(ws), True)
        self.assertEquals(self.ctool.isDiscussionAllowedFor(portal), False)
        self.assertEquals(self.ctool.isDiscussionAllowedFor(ws), False)
        self.assertEquals(self.ctool.getComments(portal), [])
        self.assertEquals(self.ctool.getComments(ws), [])

    # TODO
    #def test_default_permission_mappings(self):
    #    pass


def test_suite():
    tests = []
    tests.append(unittest.makeSuite(CPSCommentTests))
    return unittest.TestSuite(tests)

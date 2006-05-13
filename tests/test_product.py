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


class CPSCommentTests(CPSCommentFTestCase):

    def test_comment_tool(self):
        ctool = getToolByName(self.portal, CommentTool.id)
        self.assert_(isinstance(ctool, CommentTool))
        self.assertEquals(ctool.id, CommentTool.id)
        self.assertEquals(ctool.meta_type, CommentTool.meta_type)

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

    # TODO
    #def test_default_permission_mappings(self):
    #    pass

def test_suite():
    tests = []
    tests.append(unittest.makeSuite(CPSCommentTests))
    return unittest.TestSuite(tests)

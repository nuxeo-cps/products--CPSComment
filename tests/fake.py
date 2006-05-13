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
"""Fake objects, useful for tests
"""

import random
from OFS.Folder import Folder
from BTrees.OOBTree import OOBTree
from Products.CPSCore.ProxyBase import ProxyBase
from Products.CPSComment.comment import Comment, COMMENT_PORTAL_TYPE

# Fake doc has to be a proxy because this is tested in comment tool to know if
# document can be discussed, and because its interface is used to create its
# resource.
class FakeDocument(Folder, ProxyBase):

    def __init__(self, id, portal_type='Document', **kw):
        self.id = id
        self.portal_type = portal_type
        if kw.has_key('allow_discussion'):
            self.allow_discussion = kw.get('allow_discussion')
        if kw.has_key('docid'):
            self.docid = kw.get('docid')
        else:
            self.docid = '0'

    def getDocId(self):
        return self.docid

    def getTypeInfo(self):
        return FakeTypeInformation(self.portal_type)


class FakeTypeInformation:

    def __init__(self, id, allow_discussion=True):
        self.id = id
        self.allow_discussion = allow_discussion

    def allowDiscussion(self):
        return self.allow_discussion


class FakeTypesTool(Folder):

    id = 'portal_types'

    def getTypeInfo(self, content):
        ptype = content.portal_type
        if ptype == COMMENT_PORTAL_TYPE:
            allow_discussion = True
        else:
            # default behaviour
            allow_discussion = False
        type_info = FakeTypeInformation(ptype, allow_discussion=allow_discussion)
        return type_info


class FakeWorkflowTool(Folder):

    id = 'portal_workflow'

    def invokeFactoryFor(self, container, type_name, id, *args, **kw):
        if type_name == COMMENT_PORTAL_TYPE:
            ob = Comment(id, *args, **kw)
            container._setObject(id, ob)
        else:
            raise NotImplementedError
        return id


class FakeProxyTool(Folder):

    id = 'portal_proxies'

    def listProxies(self, docid):
        return []

    def handleObjectEvent(self, ob, event):
        pass


class FakeRepositoryTool(Folder):

    id = 'portal_repository'

    _tree = OOBTree()

    def has_key(self, key):
        return self._tree.has_key(key)

    def keyRange(self, k1, k2):
        return self._tree.keys(k1, k2)

    def getFreeDocid(self):
        while 1:
            docid = str(random.randrange(1, 2147483600))
            if not self.keyRange(docid+'__0001', docid+'__9999'):
                return docid

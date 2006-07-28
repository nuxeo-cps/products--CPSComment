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

from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.utils import ContentInit, ToolInit
from Products.CMFCore.permissions import AddPortalContent

from Products.GenericSetup import profile_registry
from Products.GenericSetup import EXTENSION

from Products.CPSCore.interfaces import ICPSSite

from Products.CPSComment import commenttool
from Products.CPSComment.comment import Comment, addComment
# register the node
from Products.CPSComment import commentresource

from Products.CPSUtil.testing.environment import setTestingEnvironmentIfNeeded

# for tests
setTestingEnvironmentIfNeeded()

registerDirectory('skins', globals())

# register widgets
from Products.CPSComment import widgets

def initialize(registrar):

    ToolInit(
        'CPS Tools',
        tools=(commenttool.CommentTool,),
        icon='tool.png',
        ).initialize(registrar)

    ContentInit(
        'CPSComment Types',
        content_types=(Comment,),
        permission=AddPortalContent,
        extra_constructors=(addComment,),
        fti=(),
        ).initialize(registrar)

    profile_registry.registerProfile(
        'default',
        'CPS Comment',
        "Comment product for CPS.",
        'profiles/default',
        'CPSComment',
        EXTENSION,
        for_=ICPSSite)

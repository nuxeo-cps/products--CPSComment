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
"""CPSComment XML adapters
"""

from zope.component import adapts
from zope.component import queryMultiAdapter
from zope.interface import implements

from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects
from Products.GenericSetup.utils import XMLAdapterBase
from Products.GenericSetup.utils import PropertyManagerHelpers

from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.interfaces import ISetupEnviron

COMMENT_TOOL = 'portal_comment'
COMMENT_NAME = 'comments'


def exportProperties(obj, parent_path, context):
    """ Export properties
    """
    exporter = queryMultiAdapter((obj, context), IBody)
    path = '%s%s' % (parent_path, obj.getId().replace(' ', '_'))
    if exporter:
        if exporter.name:
            path = '%s%s' % (parent_path, exporter.name)
        filename = '%s%s' % (path, exporter.suffix)
        body = exporter.body
        if body is not None:
            context.writeDataFile(filename, body, exporter.mime_type)

def importProperties(obj, parent_path, context):
    """ Import properties
    """
    importer = queryMultiAdapter((obj, context), IBody)
    path = '%s%s' % (parent_path, obj.getId().replace(' ', '_'))
    __traceback_info__ = path
    if importer:
        if importer.name:
            path = '%s%s' % (parent_path, importer.name)
        filename = '%s%s' % (path, importer.suffix)
        body = context.readDataFile(filename)
        if body is None and filename == 'types.xml':
            # BBB: for CMF 1.5 profiles
            body = context.readDataFile('typestool.xml')
        if body is not None:
            importer.filename = filename # for error reporting
            importer.body = body


def exportCommentTool(context):
    """Export comment tool as a set of XML files.
    """
    site = context.getSite()
    tool = getToolByName(site, COMMENT_TOOL, None)
    if tool is None:
        logger = context.getLogger(COMMENT_NAME)
        logger.info("Nothing to export.")
        return
    exportProperties(tool, '', context)


def importCommentTool(context):
    """Import comment tool from a set of XML
    files.
    """
    site = context.getSite()
    tool = getToolByName(site, COMMENT_TOOL)
    importProperties(tool, '', context)


class CommentToolXMLAdapter(XMLAdapterBase, PropertyManagerHelpers):
    """XML importer and exporter for Comment tool.
    """
    adapts(ISetupEnviron)
    implements(IBody)

    _LOGGER_ID = COMMENT_NAME
    name = COMMENT_NAME

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.appendChild(self._extractProperties())
        self._logger.info("Comment tool exported.")
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        if self.environ.shouldPurge():
            self._purgeProperties()
        self._initProperties(node)
        self._logger.info("Comment tool imported.")

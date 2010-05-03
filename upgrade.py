# (C) Copyright 2010 Georges Racinet
# Author: Georges Racinet <georges@racinet.fr>
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
# $Id$

import os
import logging

import transaction

from Products.CPSDocument.upgrade import _upgrade_doc_unicode

def upgrade_comments_unicode(portal):
    """Upgrade all comments to unicode."""
    ctool = portal.portal_comment

    logger = logging.getLogger('Products.CPSComment.upgrade.comments_unicode')

    total = len(ctool)

    done = 0
    for doc in ctool.iterValues():
        if not _upgrade_doc_unicode(doc):
            logger.error("Could not upgrade comment with id %s", doc)
            continue
        done += 1
        if done % 100 == 0:
            logger.info("Upgraded %d/%d comments", done, total)
            transaction.commit()

    logger.warn("Finished unicode upgrade of the %d/%d comments.", done, total)

def profile_installed(portal):
    return portal.hasObject('portal_comment')

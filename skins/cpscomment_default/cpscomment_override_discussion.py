##parameters=allow, REQUEST=None
# $Id$
"""Allow/disallow discussion on the document

Allow discussion is allow is True, else disallow it
"""

from Products.CMFCore.utils import getToolByName

comment_tool = getToolByName(context, 'portal_comment')
comment_tool.overrideDiscussionFor(context, allow)

if REQUEST is not None:
    if allow is True:
        psm = 'psm_comments_allowed'
    else:
        psm = 'psm_comments_disallowed'
    REQUEST.RESPONSE.redirect('%s?portal_status_message=%s' %
                              (context.absolute_url(), psm))

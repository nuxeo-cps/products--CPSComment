##parameters=comment_id, REQUEST=None
# $Id$
"""
Called when a document form is posted.

Validates data, then:

 - if there's no error, updates the object and redirects to it,

 - if there's an error, puts data in session and redirects to edit form.

A form uid is propagated during the redirect to uniquely identify the
form in the session.
"""

from urllib import urlencode
from Products.CMFCore.utils import getToolByName

ctool = getToolByName(context, 'portal_comment')
ctool.deleteComment(comment_id, context)

if REQUEST is not None:
    args = {
        'portal_status_message': 'psm_comment_deleted',
        }
    url = context.absolute_url() + '?' + urlencode(args)
    REQUEST.RESPONSE.redirect(url)

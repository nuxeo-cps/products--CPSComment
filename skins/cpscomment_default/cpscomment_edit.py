##parameters=REQUEST, comment_id, cluster=None, cpsdocument_edit_and_view_button=None, action=None
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
from Products.CPSDocument.utils import getFormUidUrlArg

ctool = getToolByName(context, 'portal_comment')
comment = ctool.getComment(comment_id, context)

# Check flexible controls
comment.editLayouts(REQUEST=REQUEST)

# Validate the document and write it if it's valid
is_valid = ctool.editComment(comment, context, request=REQUEST,
                             cluster=cluster, use_session=True)

if action is None:
    action = '/cpscomment_edit_form'

if is_valid:
    if cpsdocument_edit_and_view_button is not None:
        action = ''
    psm = 'psm_comment_changed'
    args = {}
else:
    psm = 'psm_content_error'
    args = getFormUidUrlArg(REQUEST)

args['portal_status_message'] = psm
args['comment_id'] = comment.getId()
url = context.absolute_url() + action + '?' + urlencode(args)
REQUEST.RESPONSE.redirect(url)

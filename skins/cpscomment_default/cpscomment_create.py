##parameters=REQUEST, cluster=None, type_name=None, reply_id=None
# $Id$
"""
Called when a document form is posted.

Validates data, then:

 - if there's no error, updates the object and redirects to it,

 - if there's an error, puts data in session and redirects to creation form.

A form uid is propagated during the redirect to uniquely identify the
form in the session.

CPSComment specifics:
- call to specific creation script
- handle reply_to features
"""
from urllib import urlencode
from Products.CMFCore.utils import getToolByName
from Products.CPSDocument.utils import getFormUidUrlArg

ti = getToolByName(context, 'portal_types').getTypeInfo(type_name)

comment_context = context
if reply_id is not None:
    ctool = getToolByName(context, 'portal_comment')
    comment_context = ctool.getComment(reply_id, context)

is_valid, ds = ti.validateObject(None, layout_mode='create', request=REQUEST,
                                 context=comment_context,
                                 cluster=cluster, use_session=True)

if is_valid:
    comment = context.createCPSComment(type_name, ds.getDataModel(), reply_id)
    url = context.absolute_url()
    action = comment.getTypeInfo().immediate_view
    psm = 'psm_comment_created'
    args = {'comment_id': comment.getId()}
else:
    url = context.absolute_url()
    action = 'cpscomment_create_form'
    psm = 'psm_content_error'
    args = {'type_name': type_name}
    if reply_id is not None:
        args.update({'reply_id': reply_id})
    args.update(getFormUidUrlArg(REQUEST))

args['portal_status_message'] = psm
url = url + '/' + action + '?' + urlencode(args)
REQUEST.RESPONSE.redirect(url)

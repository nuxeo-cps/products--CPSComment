##parameters=request=None, cluster=None, type_name=None, layout_mode='create', use_session=True
# $Id$
"""
Compute the rendering for a creation layout.

May use previous data from the request and session to display errors.

Returns the rendered HTML.

CPSComment specifics:
- handle reply_to features
"""
from Products.CMFCore.utils import getToolByName

ti = getToolByName(context, 'portal_types').getTypeInfo(type_name)

# if comment is a reply to another comment, use that comment as context, not
# the proxy

comment_context = context
if request is not None:
    reply_id = request.get('reply_id')
    if reply_id is not None:
        ctool = getToolByName(context, 'portal_comment')
        comment_context = ctool.getComment(reply_id, context)

rendered = ti.renderObject(None, layout_mode=layout_mode, cluster=cluster,
                           request=request, context=comment_context,
                           use_session=True, no_form=True) # XXX remove no_form
return rendered

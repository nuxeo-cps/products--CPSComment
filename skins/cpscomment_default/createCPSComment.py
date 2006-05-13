##parameters=type_name, datamodel, reply_id=None
# $Id$
"""
Create an empty object in the context according to the datamodel.

Datamodel may be examined to create a suitable id.

Returns the created object (usually a proxy).

CPSComment specifics:
- create comment using comment tool
"""
from Products.CMFCore.utils import getToolByName

ctool = getToolByName(context, 'portal_comment')

reply_to = None
if reply_id is not None:
    reply_to = ctool.getComment(reply_id, context)

language = datamodel.get('Language')
if not language:
    ts = getToolByName(context, 'translation_service')
    language = ts.getSelectedLanguage()

comment_id = ctool.createComment(context, type_name,
                                 reply_to=reply_to, datamodel=datamodel,
                                 language=language)
comment = ctool.getComment(comment_id, context)

return comment

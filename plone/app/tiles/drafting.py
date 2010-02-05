from zope.interface import implements
from zope.interface import implementer
from zope.interface import Interface

from zope.component import adapts
from zope.component import adapter

from zope.annotation.interfaces import IAnnotations

from plone.tiles.interfaces import ITileDataContext
from plone.tiles.interfaces import ITile

from plone.tiles.data import ANNOTATIONS_KEY_PREFIX

from plone.app.drafts.interfaces import IDrafting
from plone.app.drafts.interfaces import IDraftSyncer
from plone.app.drafts.interfaces import IDraft

from plone.app.drafts.proxy import DraftProxy
from plone.app.drafts.utils import getCurrentDraft

from plone.app.tiles.bookkeeping import ANNOTATIONS_KEY
from plone.app.tiles.bookkeeping import COUNTER_KEY

@implementer(ITileDataContext)
@adapter(Interface, IDrafting, ITile)
def draftingTileDataContext(context, request, tile):
    """If we are drafting a content item, record tile data and book-keeping
    information to the draft, but read existing data from the underlying
    object.
    """
    
    draft = getCurrentDraft(request, create=True)
    if draft is None:
        return context
    
    return DraftProxy(draft, context)

class TileDataDraftSyncer(object):
    """Copy draft persistent tile data and book-keeping information to the
    real object on save
    """
    
    implements(IDraftSyncer)
    adapts(IDraft, Interface)
    
    def __init__(self, draft, target):
        self.draft = draft
        self.target = target
    
    def __call__(self):
        
        draftAnnotations = IAnnotations(self.draft)
        targetAnnotations = IAnnotations(self.target)
        
        for key, value in draftAnnotations.iteritems():
            if (key.startswith(ANNOTATIONS_KEY_PREFIX) or
                key in (ANNOTATIONS_KEY, COUNTER_KEY)
            ):
                targetAnnotations[key] = value
        
        annotationsDeleted = getattr(self.draft, '_proxyAnnotationsDeleted', set())
        for key in annotationsDeleted:
            if (key.startswith(ANNOTATIONS_KEY_PREFIX) or
                key in (ANNOTATIONS_KEY, COUNTER_KEY)
            ):
                del targetAnnotations[key]

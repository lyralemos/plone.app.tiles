from zope.component import getAllUtilitiesRegisteredFor
from zope.component import getUtility

from AccessControl import Unauthorized
from Products.Five.browser import BrowserView

from zope.security import checkPermission
from zope.event import notify

from plone.tiles.interfaces import ITileType
from plone.tiles.interfaces import ITileDataManager

from plone.memoize.view import memoize

try:
    from zope.lifecycleevent import ObjectRemovedEvent
except ImportError:
    from zope.app.container.contained import ObjectRemovedEvent

class TileDelete(BrowserView):
    """Delete a given tile
    """
    
    def sortKey(self, type1, type2):
        return cmp(type1.title, type2.title)
    
    @memoize
    def tileTypes(self):
        """Get a list of addable ITileType objects representing tiles
        which are addable in the current context
        """
        types = []
        
        for type_ in getAllUtilitiesRegisteredFor(ITileType):
            if checkPermission(type_.add_permission, self.context):
                types.append(type_)
        
        types.sort(self.sortKey)
        return types
    
    def __call__(self):
        self.request['disable_border'] = True
        
        confirm = self.request.form.get('confirm', False)
        
        self.tileTypeName = self.request.form.get('type', None)
        self.tileId = self.request.form.get('id', None)
        
        self.deleted = False
        
        if confirm and self.tileTypeName and self.tileId:
            
            tileType = getUtility(ITileType, name=self.tileTypeName)
            
            if not checkPermission(tileType.add_permission, self.context):
                raise Unauthorized("You are not allowed to modify this tile type")
            
            tile = self.context.restrictedTraverse('@@' + self.tileTypeName)
            tile.id = self.tileId
            
            dm = ITileDataManager(tile)
            dm.delete()
            
            notify(ObjectRemovedEvent(tile, self.context, self.tileId))
            
            self.deleted = True
        
        elif 'form.button.Ok' in self.request.form:
            self.request.response.redirect(self.context.absolute_url() + '/view')
            return ''
        
        return self.index()
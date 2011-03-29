import cocos
from cocos.director import director
# import all the transitions
from cocos.scenes import *

from protoJukeboxScene import ProtoJukeboxScene
from proxy import Proxy

class LibraryScene( ProtoJukeboxScene ):

    def __init__(self):
        super( LibraryScene, self ).__init__()

        self.libraryLabel = cocos.text.Label("Library",
            font_name='Times New Roman',
            font_size=48,
            x=director.window.width//2, y=director.window.height//1.8,
            anchor_x='center', anchor_y='center')

        self.add( self.libraryLabel )

    def handleInput( self, input ):
        print "handleInput() ", input


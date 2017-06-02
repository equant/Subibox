import cocos
from cocos.director import director
# import all the transitions
from cocos.scenes import *
from proxy import Proxy

from rotaryDial import RotaryDial
from musicSearch import MusicSearch

class ProtoJukeboxScene( cocos.scene.Scene ):
    def __init__(self):
        super( ProtoJukeboxScene, self ).__init__()
        self.dial = RotaryDial()
        self.searchList = []
        self.musicSearch = MusicSearch()

    def handleInput( self, input ):
        Proxy.idle = False
        #self.recenterLabels()

    def buildSearchList(self, input):
        self.searchList = self.dial.appendNumberToList(input, self.searchList)
        #print "BEFORE: ", self.searchList
        #deleteList = []

    def setLabelText(self, label, text, defaultWidth):

        if label.element.text != text:
            label.element.text = text
            label.element.font_size = defaultWidth
            # Adjust font size if needed to fit track info on the screen
            #label.element.font_size = label.element.font_size - .001 
            while label.element.content_width > director.window.width - (Proxy.borderPixels * 2):
                #print "Current: ", label.element.font_size
                label.element.font_size -= 2
                #print "New: ", label.element.font_size

            #print "Font Size: ", label.element.font_size

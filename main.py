#! /usr/bin/env python

import subprocess, sys, random

import cocos
from cocos.director import director
# import all the transitions
from cocos.scenes import *

import pyglet
from pyglet.window import key

# My Classes
from arduinoSerial  import ArduinoSerial
from protoJukeboxScene import ProtoJukeboxScene
from lastfm import LastFMScene, LastFMMenuScene
from proxy import Proxy

def checkHarwareInterface(i, arduino):

    readlineString = arduino.readline()
    readlineString = readlineString.rstrip()

    # Is it valid?
    if readlineString != "":
        #print "STRING: ", readlineString

        director.scene.handleInput( readlineString )
        #if readlineString == "1":
            #if Proxy.inputMode == "search":
                #if Proxy.playMode == "lastfm":
                    ##director.replace( cocos.scene.Scene( LastFMScene() ) )
                    #try:
                        #director.replace( FadeTransition( Proxy.lastfm_scene, duration=1 ) )
                    #except:
                        #pass
        #elif readlineString == "2":
            #if Proxy.inputMode == "search":
                #if Proxy.playMode == "lastfm":
                    #try:
                        #director.replace( FadeTransition( Proxy.library_scene, duration=1 ) )
                    #except:
                        #pass

            #if len(fullSearchString) > 1:
                #playArtist(fullSearchString)
                #fullSearchString = ""
                #searchList = []

def main():

    # Setup Window...

    platform = pyglet.window.get_platform()
    display  = platform.get_default_display()

    ### DEV
    screen   = display.get_screens()[0]
    director.init(fullscreen=False, screen=screen)
    ### PRODUCTION
    #screen   = display.get_screens()[1]
    #director.init(fullscreen=True, screen=screen)

    director.window.set_mouse_visible(False)

    # Display Startup Screen
    jukebox_init_scene = JukeboxInitScene()
    director.run( jukebox_init_scene )
    

class JukeboxInitScene( ProtoJukeboxScene ):

    def __init__(self):
        super( JukeboxInitScene, self ).__init__()

        label = cocos.text.Label('Starting Up...',
            font_name='Times New Roman',
            font_size=48,
            x=director.window.width//2, y=director.window.height//1.8,
            anchor_x='center', anchor_y='center')

        self.label = label
        self.add( self.label )
        self.initialize()
        director.run( Proxy.lastfm_scene )

    def initialize(self):

        self.label.element.text = "Connecting to the Arduino..."
        # Connect to the Arduino...
        try:
            arduinoSerial = ArduinoSerial()
            arduino = arduinoSerial.connect()
            pyglet.clock.schedule(checkHarwareInterface, arduino)
        except:
            print "ERROR: Failed to connect to the arduino"
            sys.exit(0)

        self.label.element.text = "Loading Fonts..."
        pyglet.font.add_file('assets/avenir.ttf')
        pyglet.font.load('Avenir LT Std')

        self.label.element.text = "Initializing Scenes..."
        # Premake our scenes
        Proxy.lastfm_scene      = LastFMScene()
        Proxy.lastfm_scene.checkLastFM("arrrrgh!") # preload track name if lastfm is already playing
        Proxy.lastfm_menu_scene = LastFMMenuScene()
        #Proxy.library_scene = LibraryScene()




if __name__ == "__main__":
    main()

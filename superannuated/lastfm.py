# coding=UTF-8
import subprocess, sys, random

import cocos
from cocos.director import director
from cocos.sprite import Sprite
from cocos.menu import Menu, MenuItem
# import all the transitions
from cocos.scenes import *

import pyglet
from pyglet import image

from protoJukeboxScene import ProtoJukeboxScene
from proxy import Proxy

class LastFMScene( ProtoJukeboxScene ):

    def __init__(self, station="Dial Something"):
        super( LastFMScene, self ).__init__()

        # STATION NAME LABEL
        self.stationLabel = cocos.text.Label("",
            font_name = Proxy.default_font,
            font_size = Proxy.station_font_size,
            x = director.window.width//2, y = director.window.height//1.8,
            anchor_x='center', anchor_y='center')

        self.setLabelText(self.stationLabel, station, Proxy.station_font_size)

        # LAST FM LOGO
        #self.lastFMLogoImage = image.load("assets/images/lastfm/audioscrobbler_red.png")
        self.lastFMLogoImage = image.load("assets/images/lastfm/geekgirl.png")
        self.lastFMLogoSprite = Sprite( self.lastFMLogoImage )
        self.lastFMLogoSprite.scale = .25
        #self.lastFMLogoSprite.anchor_x = 0
        #self.lastFMLogoSprite.anchor_y = self.lastFMLogoSprite.height
        self.lastFMLogoSprite.x = (self.lastFMLogoSprite.width / 2) + Proxy.borderPixels
        self.lastFMLogoSprite.y = director.window.height - (self.lastFMLogoSprite.height / 2) - Proxy.borderPixels
        self.lastFMLogoSprite.opacity = 75

        # CURRENT TRACK LABEL
        self.lastFMLabel = cocos.text.Label('',
            font_name = Proxy.default_font,
            font_size = Proxy.track_font_size,
            x = director.window.width//2, y = director.window.height//9,
            anchor_x='center', anchor_y='center')

        # TIMERS
        self.schedule_interval(self.checkLastFM, 2)
        self.schedule_interval(self.idleLabels, 30)

        # ADD OBJECTS TO THE SCENE
        self.add( self.lastFMLogoSprite, 0 )
        self.add( self.stationLabel, 1 )
        self.add( self.lastFMLabel )


    ##############################################################
    # idleLabels()
    # Prevent burn-in by randomly moving labels around the screen

    def idleLabels(self, *args):
        if Proxy.idle == True:
            #print "Window: ", director.window.width, " x ", director.window.height
            #print "Label: ", self.stationLabel.element.content_width, " x ", self.stationLabel.element.content_height
            if random.randint(1,6) > 3:
                # Move Station Name
                self.stationLabel.element.y = random.randint(director.window.height/2, director.window.height - self.lastFMLabel.element.content_height)
                self.stationLabel.element.x = random.randint(Proxy.borderPixels + self.lastFMLabel.element.content_width/2, director.window.width - self.lastFMLabel.element.content_width/2 - Proxy.borderPixels)
            else:
                # Move lastFM Track
                self.lastFMLabel.element.y = random.randint(0 + self.lastFMLabel.element.content_height, director.window.height/2 - self.lastFMLabel.element.content_height)
                #self.lastFMLabel.element.x = random.randint(Proxy.borderPixels + self.lastFMLabel.element.content_width/2, director.window.width - self.lastFMLabel.element.content_width/2 - Proxy.borderPixels)
        else:
            Proxy.idle = True

    def recenterLabels(self):
        self.stationLabel.element.x = director.window.width//2
        self.stationLabel.element.y = director.window.height//1.8
        self.lastFMLabel.element.x  = director.window.width//2
        self.lastFMLabel.element.y  = director.window.height//9

    def checkLastFM(self, args):
        try:
            handle = subprocess.Popen("./lastfm.bash", stdout=subprocess.PIPE, stdin=subprocess.PIPE)
            output = handle.communicate()
            string = unicode(output[0], "utf-8")
            self.lastFMLabel.element.text = string[25:len(string)-1]
            self.lastFMLabel.element.font_size = Proxy.track_font_size
        except:
            self.lastFMLabel.element.text = ""

        #print "ßáĉẑУфЙنيخثصض"
        #self.lastFMLabel.element.text = u'ßáĉẑУфЙﻦﻴﺨﺜﺼﺿ'

        # Adjust font size if needed to fit track info on the screen
        while self.lastFMLabel.element.content_width > director.window.width:
            self.lastFMLabel.element.font_size = self.lastFMLabel.element.font_size - 4 


    ##############################################################
    # handleInput()
    # Prevent burn-in by randomly moving labels around the screen

    def handleInput( self, input ):
        Proxy.idle = False
        print "handleInput() ", input
        self.recenterLabels()

        if input == "1":
            if len(self.fullSearchString) > 1:
                self.playArtist(self.fullSearchString)
                self.lastSearchString = self.fullSearchString
                self.fullSearchString = ""
                self.searchList = []

        elif input == "10":
            director.run(cocos.scene.Scene(Proxy.lastfm_menu_scene))
            pass

        else:
            self.buildSearchList(input)
            print "BEFORE: ", self.searchList
            deleteList = []

            # Loop through dial combinations looking for artists
            allLettersResult = []
            for searchString in self.searchList:
                #print "searchString: " + searchString
                result = self.musicSearch.search(searchString)
                if result:
                    #newList = sorted(result, key=lambda foo: foo[1], reverse=True)
                    #print "FOO: ", newList[0][0], " : ", newList[0][1]
                    #self.fullSearchString = newList[0][0]
                    allLettersResult += result

                else:
                    # Remember dead-end combinations to delete later.
                    # Doing it now would screw up our loop.
                    deleteList.append(searchString)

            if allLettersResult:
                newList = sorted(allLettersResult, key=lambda foo: foo[1], reverse=True)
                self.fullSearchString = newList[0][0]
            else:
                self.fullSearchString = ""

            # Delete dead-end combinations
            for toDelete in deleteList:
                #print "Removing: " + toDelete
                self.searchList.remove(toDelete)

            print "AFTER: ", self.searchList
            print ""

            #self.stationLabel.element.text = self.fullSearchString
            self.setLabelText(self.stationLabel, self.fullSearchString, Proxy.station_font_size)


    ##########
    #

    def playArtist(self, artist):
            url = "lastfm://artist/" + str.replace(artist, " ", "+");
            print "Artist: ", artist
            myProcess = subprocess.Popen(["lastfm", url])



class LastFMMenuScene( ProtoJukeboxScene ):

    def __init__(self):
        super( LastFMMenuScene, self ).__init__()

        self.menu = cocos.menu.Menu('My Game Title')
        self.menu.create_menu([
            MenuItem('Test', self.test),
            MenuItem('Quit', pyglet.app.exit)])

        #menu.on_quit = pyglet.app.exit
        #director.run(cocos.scene.Scene(menu))

        #self.libraryLabel = cocos.text.Label("Menu",
            #font_name='Times New Roman',
            #font_size=48,
            #x=director.window.width//2, y=director.window.height//1.8,
            #anchor_x='center', anchor_y='center')

        self.add( self.menu )

    def test( self ):
        print "poop!"

    def handleInput( self, input ):
        pass


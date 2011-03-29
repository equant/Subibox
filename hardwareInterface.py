import subprocess
from rotaryDial  import RotaryDial
from musicSearch import Index
import pyglet
from pyglet.window import key

class InterfaceProxy:

    def __init__(self, arduino):
        self.arduino = arduino
        self.dial = RotaryDial(self)
        self.quit = 0
        self.displayString = "Dial Something"
        self.fullSearchString = ""
        self.searchList = []
        self.searchIndex = Index()

        #platform = pyglet.window.get_platform()
        #display  = platform.get_default_display()

        #display = window.get_platform().get_default_display()
        #screens = display.get_screens()

        window = pyglet.window.get_platform().get_default_display()

        self.lastFMLabel = pyglet.text.Label('',
                               font_name='Times New Roman',
                               font_size=24,
                               I=window.width//2, y=window.height//9,
                               anchor_x='center', anchor_y='center')

        pyglet.clock.schedule_interval_soft(self.checkLastFM, 2)

    def playArtist(self, artist):
            url = "lastfm://artist/" + str.replace(artist, " ", "+");
            print "Artist: ", artist
            myProcess = subprocess.Popen(["lastfm", url])

    def checkLastFM(self, pygletArgs):
        handle = subprocess.Popen("./lastfm.bash", stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        output = handle.communicate()
        string = unicode(output[0], "utf-8")
        if output:
            self.lastFMLabel.text = string[25:len(string)-1]
        else:
            self.lastFMLabel.text = ""
    
    def handleSerialString(self, pyFoo):
        # Get character from serial input
        self.readlineString = self.arduino.readline()
        self.readlineString = self.readlineString.rstrip()

        # Is it valid?
        if self.readlineString != "":

            if self.readlineString[0] == "G":
                pass
               # Do Radio Buttons

            else: 
                # check for a 'one' being dialed, because that's a speccial command...
                if self.readlineString == "1":
                    if len(self.fullSearchString) > 1:
                        self.playArtist(self.fullSearchString)
                        self.fullSearchString = ""
                        self.searchList = []

                else:
                    self.searchList = self.dial.handleSerial(self.readlineString, self.searchList)
                    print "BEFORE: ", self.searchList
                    deleteList = []

                    # Loop through dial combinations looking for artists
                    for searchString in self.searchList:
                        print "searchString: " + searchString
                        result = self.searchIndex.search(searchString)
                        if result:
                            self.fullSearchString = result
                            self.displayString = result
                        else:
                            # Remember dead-end combinations to delete later.
                            # Doing it now would screw up our loop.
                            deleteList.append(searchString)

                    # Delete dead-end combinations
                    for toDelete in deleteList:
                        print "Removing: " + toDelete
                        self.searchList.remove(toDelete)

                    print "AFTER: ", self.searchList
                    print ""

    def on_draw(self):
        self.lastFMLabel.draw()

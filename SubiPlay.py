#!/usr/bin/env python

#import os, sys, re, time
#import sqlite3
#import pandas as pd

#database_file = 'dbTools/subibox.sqlite.full'
#database_file = 'dbTools/subibox.sqlite'
#conn          = sqlite3.connect(database_file)

import mpd
from mpd import MPDClient

mpd_host = "192.168.1.81"
mpd_port = "6600"

#client.close()                     # send the close command
#client.disconnect()                # disconnect from the server

class Play():

    def __init__(self):
        self.client = MPDClient()               # create client object
        #client.timeout = 10                # network timeout in seconds (floats allowed), default: None
        #client.idletimeout = None          # timeout for fetching the result of the idle command is handled seperately, default: None

    def connect(self):
        try:
            self.client.connect(mpd_host, mpd_port)
            print("MPD Version: " + self.client.mpd_version)          # print the MPD version
        except OSError:
            print("Error connecting to MPD")
        except mpd.ConnectionError:
            # Already connected?
            pass

    def current_track_info(self):
        self.connect()
        return self.client.currentsong()

    def next_track(self):
        self.connect()
        self.client.next()

    def pause(self):
        self.connect()
        self.client.pause()

    def play_album(self, album_path):
        self.connect()
        # mpc -h 192.168.1.80 -p 6600 listall Yeah_Yeah_Yeahs/
# Maybe you need album_path[1:]?
        print("Requesting mpd play album: {}".format(album_path[1:]))
        self.client.clear()
        self.client.add(album_path)     # [1:] to strip leading /
        self.client.play()


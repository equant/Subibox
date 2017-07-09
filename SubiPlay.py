#!/usr/bin/env python

#import os, sys, re, time
#import sqlite3
#import pandas as pd

#database_file = 'dbTools/subibox.sqlite.full'
#database_file = 'dbTools/subibox.sqlite'
#conn          = sqlite3.connect(database_file)

import mpd
from mpd import MPDClient

from SubiConfig import MPD_HOST, MPD_PORT

class Play():

    def __init__(self):
        self.client = MPDClient()               # create client object
        #client.timeout = 10                # network timeout in seconds (floats allowed), default: None
        #client.idletimeout = None          # timeout for fetching the result of the idle command is handled seperately, default: None

    def connect(self):
        try:
            self.client.connect(MPD_HOST, MPD_PORT)
            print("MPD Version: " + self.client.mpd_version)          # print the MPD version
        except OSError:
            print("Error connecting to MPD")
        except mpd.ConnectionError:
            # Already connected?
            pass

    def current_track_info(self):
        self.connect()
        try:
            return self.client.currentsong()
        except mpd.ConnectionError as e:
            print("[ERROR] current_track_info(): mpd.ConnectionError".format(e))
            return None
        except mpd.CommandError as e:
            print("[ERROR] play_album(): mpd.CommandError".format(e))
            return None

    def next_track(self):
        self.connect()
        try: 
            self.client.next()
        except mpd.ConnectionError as e:
            print("[ERROR] next_track(): mpd.ConnectionError".format(e))
        except mpd.CommandError as e:
            print("[ERROR] play_album(): mpd.CommandError".format(e))

    def pause(self):
        self.connect()
        try:
            self.client.pause()
        except mpd.ConnectionError as e:
            print("[ERROR] pause(): mpd.ConnectionError".format(e))
        except mpd.CommandError as e:
            print("[ERROR] play_album(): mpd.CommandError".format(e))

    def play_album(self, album_path):
        self.connect()
        # mpc -h 192.168.1.80 -p 6600 listall Yeah_Yeah_Yeahs/
# Maybe you need album_path[1:]?
        print("Requesting mpd play album: {}".format(album_path[1:]))
        try: 
            self.client.clear()
            self.client.add(album_path[1:])     # [1:] to strip leading /
            self.client.play()
        except mpd.ConnectionError as e:
            print("[ERROR] play_album(): mpd.ConnectionError: {}".format(e))
        except mpd.CommandError as e:
            print("[ERROR] play_album(): mpd.CommandError: {}".format(e))


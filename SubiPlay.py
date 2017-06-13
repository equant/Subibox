#!/usr/bin/env python

#import os, sys, re, time
#import sqlite3
#import pandas as pd

#database_file = 'dbTools/subibox.sqlite.full'
#database_file = 'dbTools/subibox.sqlite'
#conn          = sqlite3.connect(database_file)

from mpd import MPDClient

mpd_host = "192.168.1.80"
mpd_port = "6600"

#client.close()                     # send the close command
#client.disconnect()                # disconnect from the server

class Play():

    def __init__(self):
        client = MPDClient()               # create client object
        client.timeout = 10                # network timeout in seconds (floats allowed), default: None
        client.idletimeout = None          # timeout for fetching the result of the idle command is handled seperately, default: None
        try:
            client.connect(mpd_host, mpd_port)  # connect to localhost:6600
            print("MPD Version: " + client.mpd_version)          # print the MPD version
            self.client = client
        except OSError:
            self.client = None

    def pause(self):
        if self.client is not None:
            print("[DEBUG][SubiPlay.Play.pause()")
            self.client.pause()

    def play_album(self):
        # mpc -h 192.168.1.80 -p 6600 listall Yeah_Yeah_Yeahs/
        pass


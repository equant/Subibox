import pylast
import lastfmapi

from passwords import LASTFM_API_SECRET, LASTFM_API_KEY

class SubiLastFm:
    def __init__(self):
        self.last = pylast.LastFMNetwork(api_key=LASTFM_API_KEY, api_secret=LASTFM_API_SECRET)

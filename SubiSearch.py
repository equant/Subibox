#!/usr/bin/env python

import os, sys, re, time
import sqlite3
#import pandas as pd
from collections import Counter

#database_file = 'dbTools/subibox.sqlite.full'
database_file    = 'dbTools/subibox.sqlite'
conn             = sqlite3.connect(database_file)
conn.row_factory = sqlite3.Row

def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print('{} function took {:0.3f} ms'.format(f.__name__, (time2-time1)*1000.0))
        return ret
    return wrap

class StringAnalyzer:
    """
    Analyze string and remove stop words
    """
    #stop_words = ['los','las','el','the','of','and','le','de','a','des','une','un','s','is','www','http','com','org','-']
    stop_words = ['www','http','com','org','-']
    def __init__(self):
        pass

    def analyze(self, text):
        words = []
        #text = self.strip_accents(text)
        text = re.compile('[\'`?"]').sub(" ", text)
        text = re.compile('[^A-Za-z0-9]').sub(" ", text)
        for word in text.split(" "):
            word = word.strip().lower()
            #if word not in self.stop_words:
            if word not in self.stop_words:
                #print("|{}|".format(word))
                words.append(word.lower())
        return words


class Search():

    def __init__(self, verbose=True):
        self.verbose = verbose

    def get_artist_albums(self, artist_id):
        try:
            artist_id = int(artist_id)
        except ValueError:
            print("SubiSearch.Search.get_artist_albums() [Warning] Value: {} doesn't look like an artist id.".format(artist_id))
        cursor = conn.execute("""\
                SELECT id, full_album_name, album_year, album_path, album_art
                  FROM albums
                 WHERE artist_id = ?
              ORDER BY album_year
                 """, (artist_id,))
        return cursor.fetchall()


    @timing
    def artist_search(self,query_list):
        print("Searching artists, query_list has {} items in it".format(len(query_list)))
        result = []

        for query in query_list:
            # -- Look for an exact match (100 pts)...
            time1 = time.time()
            cursor = conn.execute("""\
                    SELECT id, dial_compatible_artist_name, full_artist_name
                      FROM artists
                     WHERE dial_compatible_artist_name = ?
                  GROUP BY full_artist_name
                     """, (query,))
            row = cursor.fetchall()
            for i in range(len(row)):
                artist_id        = row[i][0]
                artist_full_name = row[i][2]
                result.append([artist_full_name, 100, artist_id])
                #print("{}:100".format(artist_full_name, " : 100"))
            time2 = time.time()
            print('Exact Matches took {:0.3f} ms'.format((time2-time1)*1000.0))

            time1 = time.time()
            # -- Look for an close match (20 pts)...
            cursor = conn.execute("""\
                    SELECT id, dial_compatible_artist_name, full_artist_name
                      FROM artists
                     WHERE dial_compatible_artist_name LIKE ?
                  GROUP BY full_artist_name
                     """, (query+'%',))
            row = cursor.fetchall()
            for i in range(len(row)):
                artist_id        = row[i][0]
                artist_full_name = row[i][2]
                result.append([artist_full_name, 20, artist_id])
                #print("{}:100".format(artist_full_name, " : 100"))
            time2 = time.time()
            print('Close (^) Matches took {:0.3f} ms'.format((time2-time1)*1000.0))

            time1 = time.time()
            # -- Look for a like match (10 pts)
            cursor = conn.execute("""\
                    SELECT a.id, a.dial_compatible_artist_name, a.full_artist_name
                      FROM artist_search_strings as ass
                 LEFT JOIN artists a
                        ON ass.artist_id = a.id
                     WHERE ass.search_string
                      LIKE ?
                  GROUP BY a.full_artist_name
                    """, ('%'+query+'%',))
            row = cursor.fetchall()
            for i in range(len(row)):
                artist_id        = row[i][0]
                artist_full_name = row[i][2]
                result.append([artist_full_name, 10, artist_id])
                #print("{}:10".format(artist_full_name, " : 10"))
            time2 = time.time()
            print('Any (*) Matches took {:0.3f} ms'.format((time2-time1)*1000.0))


        if len(result) > 0:
            time1 = time.time()
            # result looks like this...
            #['name', 'score', 'id'])
            # ...but we need to group duplicate scores.  We use a Counter() do to this
            # and make a dict to connect names and ids so we can remake result as
            # new_result, which has the same columns, but no duplicates.
            c = Counter()
            id_map = {}
            for artist_name, score, artist_id in result:
                id_map[artist_name] = artist_id
                c.update({artist_name: score})
            #print(list(c.items()))
            sorted_grouped_results = []
            for artist_name, score in sorted(c.items(), key=lambda x: x[1], reverse=True):
                d = {
                        'name'      : artist_name,
                        'score'     : score,
                        'id'        : id_map[artist_name]
                    }
                sorted_grouped_results.append(d)
            # Sort list by second column (score)...
            time2 = time.time()
            print('Sorting took {:0.3f} ms'.format((time2-time1)*1000.0))
            return sorted_grouped_results
        else:
            return None

    def get_album_colors(self, album_id):
        try:
            album_id = int(album_id)
        except ValueError:
            print("SubiSearch.Search.get_album_colors() [Warning] Value: {} doesn't look like an artist id.".format(album_id))
        cursor = conn.execute("""\
                SELECT color, color_sum
                  FROM album_colors
                 WHERE album_id = ?
              ORDER BY color_sum
                 """, (album_id,))
        #df = pd.DataFrame(cursor.fetchall(), columns=['color', 'color_sum'])
        return cursor.fetchall()



#!/usr/bin/env python

import os, sys, re, time
import sqlite3
import pandas as pd

database_file = 'dbTools/subibox.sqlite'
conn          = sqlite3.connect(database_file)

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

    def artist_search(self,query):
        print("Searching artists for: {}".format(query))
        result = []

        # -- Look for an exact match (100 pts)...
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
            print("{}:100".format(artist_full_name, " : 100"))

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
            print("{}:100".format(artist_full_name, " : 100"))

        # -- Look for a like match (10 pts)
        cursor = conn.execute("""\
                SELECT a.id, a.dial_compatible_artist_name, a.full_artist_name
                  FROM artist_search_strings as ass
             LEFT JOIN artists a
                    ON ass.artist_id = a.id
                 WHERE ass.search_string
                  LIKE ?
              GROUP BY a.full_artist_name
                """, (query+'%',))
        row = cursor.fetchall()
        for i in range(len(row)):
            artist_id        = row[i][0]
            artist_full_name = row[i][2]
            result.append([artist_full_name, 10, artist_id])
            print("{}:10".format(artist_full_name, " : 10"))

        if len(result) > 0:
            df = pd.DataFrame(result, columns=['name', 'score', 'id'])
            return df.groupby(['name', 'id']).sum().sort_values(by=['score'], ascending=False).reset_index()
        else:
            return None


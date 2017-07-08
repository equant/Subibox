#!/usr/bin/env python

import os, sys, re, time, random
import sqlite3
#import pandas as pd
from collections import Counter

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


    #@timing
    def artist_search(self,query_list):
        print("Searching artists, query_list has {} items in it".format(len(query_list)))
        result = []
        new_query_list = query_list

        for query in list(query_list):
            """
            (1) Look for any match     (%string%)
            (2) Look for leading match (string%)
            (3) Look for exact match   (string)
            If there are no matches found at any step, the string is removed from the
            query list (and the new truncated query_list is returned along with the
            query results)
            """

            time1 = time.time()
            # -(1)- Look for a like match (10 pts)
            cursor = conn.execute("""\
                    SELECT a.id, a.dial_compatible_artist_name, a.full_artist_name
                      FROM artist_search_strings as ass
                 LEFT JOIN artists a
                        ON ass.artist_id = a.id
                     WHERE ass.search_string
                      LIKE ?
                  --GROUP BY a.full_artist_name
                    """, ('%'+query+'%',))
            row = cursor.fetchall()
            n_rows = len(row)
            if n_rows == 0:
                new_query_list.remove(query)
                continue
            for i in range(n_rows):
                artist_id        = row[i][0]
                artist_full_name = row[i][2]
                result.append([artist_full_name, 10, artist_id])
            time2 = time.time()
            #print('Any (*) Matches took {:0.3f} ms'.format((time2-time1)*1000.0))

            time1 = time.time()
            # -(2)- Look for an close match (20 pts)...
            cursor = conn.execute("""\
                    SELECT id, dial_compatible_artist_name, full_artist_name
                      FROM artists
                     WHERE dial_compatible_artist_name LIKE ?
                  --GROUP BY full_artist_name
                     """, (query+'%',))
            row = cursor.fetchall()
            n_rows = len(row)
            for i in range(n_rows):
                artist_id        = row[i][0]
                artist_full_name = row[i][2]
                result.append([artist_full_name, 20, artist_id])
            time2 = time.time()
            #print('Close (^) Matches took {:0.3f} ms'.format((time2-time1)*1000.0))

            # -(3)- Look for an exact match (100 pts)...
            time1 = time.time()
            cursor = conn.execute("""\
                    SELECT id, dial_compatible_artist_name, full_artist_name
                      FROM artists
                     WHERE dial_compatible_artist_name = ?
                  --GROUP BY full_artist_name
                     """, (query,))
            row = cursor.fetchall()
            n_rows = len(row)
            for i in range(n_rows):
                artist_id        = row[i][0]
                artist_full_name = row[i][2]
                result.append([artist_full_name, 100, artist_id])
            time2 = time.time()
            #print('Exact Matches took {:0.3f} ms'.format((time2-time1)*1000.0))



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
            #print('Sorting took {:0.3f} ms'.format((time2-time1)*1000.0))
            sorted_grouped_results.sort(key=lambda x:(x['score'], random.random()), reverse=True)
            #print("Possible Matches:\n{}".format(sorted_grouped_results))
            #print("Old Query List:\n{}".format(query_list))
            #print("Query List:\n{}".format(new_query_list))
            return sorted_grouped_results, new_query_list
        else:
            return None, new_query_list

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
        return cursor.fetchall()



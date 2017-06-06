#!/usr/bin/env python

import os, sys, re, time
import sqlite3

database_file = 'dbTools/subibox.sqlite'
conn          = sqlite3.connect(database_file)

class ArtistSearch():

    def __init__(self, verbose=True):
        self.verbose = verbose

    def artist_search(self,query):
        if self.verbose:
            print("Searching artists for: {}".format(query))

    def exact_matches(self, query):
        result = []
        # Look for an exact match...
        #q = 'SELECT dial_compatible_artist_name, full_artist_name FROM artists WHERE dial_compatible_artist_name = "' + str(query) + '" GROUP BY full_artist_name'
        #print "Query: ", q
        #cursor.execute(q)
        cursor = conn.execute("""\
                SELECT id, dial_compatible_artist_name, full_artist_name
                  FROM artists
                 WHERE dial_compatible_artist_name = ?
              GROUP BY full_artist_name
                 """, (query,))
        row = cursor.fetchall()
        for i in range(len(row)):
            artist = row[i][1]
            result.append([artist, 100])
            print("{}:100".format(row[i]["full_artist_name"], " : 100")

        # Look for a like match
        q = 'SELECT keyword, full_artist_name FROM artist_keywords WHERE keyword LIKE "' + str(query) + '%" GROUP BY full_artist_name'
        cursor.execute(q)
        for line in cursor:
            result.append([line["full_artist_name"], 10])
            print(line["full_artist_name"], " : 10")
        return result

#    def search(self,query):
#        cnx = self.db()
#        analyzer = Analyzer()
#        clauses = []
#        for word in analyzer.analyze(query):
#            clauses.append("id3_id IN(SELECT id3_id FROM id3index WHERE keyword LIKE '" + str(word) + "%')")
#        cursor = cnx.cursor()
#        #q = 'SELECT COUNT(id3index.id) AS score, id3_id, id3.* from id3index join id3 on id3.id = id3index.id3_id  where ' + ' AND '.join(clauses) + ' GROUP BY artist ORDER BY score DESC'
#        q = 'SELECT id3.artist from id3index join id3 on id3.id = id3index.id3_id  where ' + ' AND '.join(clauses) + ' GROUP BY artist LIMIT 1'
#
#        #q = "SELECT id3.* FROM id3 WHERE artist LIKE '" + str(query) + "%' GROUP BY artist"
#
#        cursor.execute(q)
#        for line in cursor:
#            return line["artist"]
#            break

    def db(self):
        if getattr(self,"database", None) == None:
            self.database = sqlite3.connect(dsn)
            self.database.row_factory = sqlite3.Row
            self.database.text_factory = str
            cursor = self.database.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS id3index(id INTEGER PRIMARY KEY AUTOINCREMENT,id3_id, keyword, field)")
            cursor.execute("CREATE TABLE IF NOT EXISTS id3(id INTEGER PRIMARY KEY AUTOINCREMENT,location UNIQUE, artist, title, album, genre, comment, duration, length, size)")
            cursor.execute("CREATE INDEX IF NOT EXISTS keyword_idx ON id3index(keyword)")
        return self.database

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: tags.py index-build [your music dir]')
    else:
        index = MusicSearch()
        if sys.argv[1] == 'index-build':
            index.build(sys.argv[2])
        elif sys.argv[1] == 'search':
            index.search(sys.argv[2])

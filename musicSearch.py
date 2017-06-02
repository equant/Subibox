#!/usr/bin/env python
# http://www.desfrenes.com/blog/post/python-mp3-indexer-look-up

import os
import sys
import mutagen
from mutagen.easyid3 import EasyID3
import sqlite3
import unicodedata
import re
import time

# change this path to your sqlite database
#dsn = '/Users/mickael/python_sandbox/tags/id3.sqlite'
dsn = 'dbTools/id3.sqlite'

class Analyzer:
    """
    Analyze string and remove stop words
    """
    def __init__(self):
        self.stop_words = ['los','las','el','the','of','and','le','de','a','des','une','un','s','is','www','http','com','org']

    def analyze(self, text):
        words = []
        text = self.strip_accents(text)
        text = re.compile('[\'`?"]').sub(" ", text)
        text = re.compile('[^A-Za-z0-9]').sub(" ", text)
        for word in text.split(" "):
            word = word.strip()
            if word != "" and not word in self.stop_words:
                if not isinstance(word, unicode):
                    words.append(word.lower())
                else:
                    words.append(word.lower())
        return words

    def strip_accents(self,s):
        s = unicode(s)
        return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))


class ID3:
    def __init__(self,path):
        self._load(path)

    def _load(self, filename):
        short_tags = full_tags = mutagen.File(filename)
        comments = []
        if isinstance(full_tags, mutagen.mp3.MP3):
            for key in short_tags:
                if key[0:4] == 'COMM':
                    if(short_tags[key].desc == ''):
                        comments.append(short_tags[key].text[0])
            short_tags = mutagen.mp3.MP3(filename, ID3 = mutagen.easyid3.EasyID3)
        comments.append('');
        self.album = short_tags.get('album', [''])[0]
        self.artist = short_tags.get('artist', [''])[0]
        self.duration = "%u:%.2d" % (full_tags.info.length / 60, full_tags.info.length % 60)
        self.length = full_tags.info.length
        self.title = short_tags.get('title', [''])[0]
        self.comment = comments[0]
        self.genre = ''
        genres = short_tags.get('genre', [''])
        if len(genres) > 0:
            self.genre = genres[0]
        self.size = os.stat(filename).st_size


class MusicSearch:
    def build(self,start):
        errors = []
        analyzer = Analyzer()
        cnx = self.db()
        cursor = cnx.cursor()
        #cursor.execute("DELETE FROM id3index;")
        #cursor.execute("DELETE FROM id3;")
        for root, dir, files in os.walk(start):
            for name in files:
                #if name[-4:].lower() == '.mp3':
                #if name[-5:].lower() == '.flac':
                if 1:
                    path = os.path.join(root,name)
                    print("NAME: ", name)
                    try:
                        id3 = ID3(path)
                    except:
                        errors.append(path)
                        id3 = None
                    if id3 != None:
                        cursor.execute("INSERT INTO id3(location, artist, title, album, genre, comment, duration, length, size) VALUES(?,?,?,?,?,?,?,?,?)",
                                       (path,id3.artist,id3.title,id3.album,id3.genre,id3.comment,id3.duration,id3.length,id3.size))
                        last_id3_id = cursor.lastrowid
                        for field in ['artist', 'title', 'album', 'comment', 'genre']:
                            words = analyzer.analyze(getattr(id3, field))
                            for word in words:
                                cursor.execute("INSERT INTO id3index(id3_id,keyword,field) VALUES (?,?,?);", (str(last_id3_id), word, field))
        cursor.execute('SELECT COUNT(*) AS nbrows FROM id3index LIMIT 1;')
        for line in cursor:
            print('index size: ' + str(line["nbrows"]))
        cnx.commit()
        if len(errors) > 0:
            print("")
            print("---- Errors ----")
            print("")
            for error in errors:
                print(error)

    def search(self,query):
        #print "SEARCHING FOR: " + query
        cnx = self.db()
        analyzer = Analyzer()
        clauses = []
        #for word in analyzer.analyze(query):
            #clauses.append("id3_id IN(SELECT id3_id FROM id3index WHERE keyword LIKE '" + str(word) + "%')")
        cursor = cnx.cursor()
        #q = 'SELECT COUNT(id3index.id) AS score, id3_id, id3.* from id3index join id3 on id3.id = id3index.id3_id  WHERE keyword LIKE "' + str(query) + '%" GROUP BY artist ORDER BY score DESC'
        #q = "SELECT id3.* FROM id3 WHERE artist LIKE '" + str(word) + "%' GROUP BY artist"
        #q = 'SELECT artist, length(artist) as stringLength from id3index join id3 on id3.id = id3index.id3_id  WHERE keyword LIKE "' + str(query) + '%" GROUP BY artist ORDER BY RANDOM()'


        result = []     # artist, score

        # Look for an exact match...
        q = 'SELECT dial_compatible_artist_name, full_artist_name FROM artists WHERE dial_compatible_artist_name = "' + str(query) + '" GROUP BY full_artist_name'
        #print "Query: ", q
        cursor.execute(q)
        for line in cursor:
            result.append([line["full_artist_name"], 100])
            print(line["full_artist_name"], " : 100")

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

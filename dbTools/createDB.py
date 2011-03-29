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
dsn = '/home/equant/dev/jukebox/dbTools/id3.sqlite'

class Analyzer:
    """
    Analyze string and remove stop words
    """
    def __init__(self):
        self.stop_words = ['los','las','el','the','of','and','le','de','a','des','une','un','s','is','www','http','com','org','-']

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


class Index:
    def build(self,start):
        errors = []
        analyzer = Analyzer()
        cnx = self.db()
        cursor = cnx.cursor()
        cursor.execute("DELETE FROM artists;")
        cursor.execute("DELETE FROM artist_keywords;")
        #cursor.execute("DELETE FROM id3index;")
        #cursor.execute("DELETE FROM id3;")
        for root, dir, files in os.walk(start):
            for name in files:
                #if name[-4:].lower() == '.mp3':
                #if name[-5:].lower() == '.flac':
                if 1:
                    #print "NAME: ", name

                    path = os.path.join(root,name)
                    alphaNumPattern = re.compile('[\W_]+')

                    # Extract Tags From File
                    try:
                        id3 = ID3(path)
                    except:
                        errors.append(path)
                        id3 = None


                    # Insert each file into the id3 table
                    if id3 != None:
                        #cursor.execute("INSERT INTO id3(location, artist, title, album, genre, comment, duration, length, size) VALUES(?,?,?,?,?,?,?,?,?)", (path,id3.artist,id3.title,id3.album,id3.genre,id3.comment,id3.duration,id3.length,id3.size))
                        last_id3_id = cursor.lastrowid
                        #for field in ['artist', 'title', 'album', 'comment', 'genre']:


                        # Create the artist tables
                        for field in ['artist']:
                            #print "Field: ", getattr(id3, field)
                            full_artist_name = getattr(id3, field)
                            dial_compatible_artist_name = full_artist_name
                            dial_compatible_artist_name = alphaNumPattern.sub('', dial_compatible_artist_name)
                            dial_compatible_artist_name = dial_compatible_artist_name.lower()

                            # Break up artist name into keywords and put in artist_keywords table

                            words = analyzer.analyze(getattr(id3, field))
                            words.append(dial_compatible_artist_name)
                            for word in words:
                                #cursor.execute("INSERT INTO id3index(id3_id,keyword,field) VALUES (?,?,?);", (full_artist_name, word, field))
                                try:
                                    cursor.execute("INSERT INTO artist_keywords(keyword,full_artist_name) VALUES (?,?);", (word, full_artist_name))
                                except:
                                    pass

                            # Put artist in artists table

                            try:
                                cursor.execute("INSERT INTO artists(dial_compatible_artist_name,full_artist_name) VALUES (?,?);", (dial_compatible_artist_name, full_artist_name))
                            except:
                                pass

                            cnx.commit()
                # Display info about the whole process...

                #cursor.execute('SELECT COUNT(*) AS nbrows FROM id3index LIMIT 1;')
        #for line in cursor:
            #print 'index size: ' + str(line["nbrows"])
        #cnx.commit()
        #if len(errors) > 0:
            #print ""
            #print "---- Errors ----"
            #print ""
            #for error in errors:
                #print error



    def db(self):
        if getattr(self,"database", None) == None:
            self.database = sqlite3.connect(dsn)
            self.database.row_factory = sqlite3.Row
            self.database.text_factory = str
            cursor = self.database.cursor()

            # Create Tables
            cursor.execute("CREATE TABLE IF NOT EXISTS artists(dial_compatible_artist_name, full_artist_name, PRIMARY KEY(dial_compatible_artist_name, full_artist_name))")
            cursor.execute("CREATE TABLE IF NOT EXISTS artist_keywords(keyword, full_artist_name, PRIMARY KEY(keyword, full_artist_name))")
            #cursor.execute("CREATE INDEX IF NOT EXISTS artist_keywords_index ON artist_keywords(keyword)")

            #cursor.execute("CREATE TABLE IF NOT EXISTS id3index(id INTEGER PRIMARY KEY AUTOINCREMENT,id3_id, keyword, field)")
            #cursor.execute("CREATE TABLE IF NOT EXISTS id3(id INTEGER PRIMARY KEY AUTOINCREMENT,location UNIQUE, artist, title, album, genre, comment, duration, length, size)")
            #cursor.execute("CREATE INDEX IF NOT EXISTS keyword_idx ON id3index(keyword)")
        return self.database




if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: tags.py [your music dir]'
    else:
        index = Index()
        index.build(sys.argv[1])

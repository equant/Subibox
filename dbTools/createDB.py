#!/usr/bin/env python
# http://www.desfrenes.com/blog/post/python-mp3-indexer-look-up

import os, sys, re, time
import mutagen
from mutagen.easyid3 import EasyID3
import sqlite3
import unicodedata

# change this path to your sqlite database
#dsn = '/Users/mickael/python_sandbox/tags/id3.sqlite'
database_file = 'subibox.sqlite'
music_path = '/home/equant/beets'

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
        text = self.strip_accents(text)
        text = re.compile('[\'`?"]').sub(" ", text)
        text = re.compile('[^A-Za-z0-9]').sub(" ", text)
        for word in text.split(" "):
            word = word.strip().lower()
            #if word not in self.stop_words:
            if word not in self.stop_words:
                #print("|{}|".format(word))
                words.append(word.lower())
        return words

    def strip_accents(self,s):
        #s = unicode(s)
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


# -- Create database file by traversing music directory

class Index:

    dir_exceptions = ['Unknown', 'Soundtracks', 'Compilations']

    def build(self,root_path):

        conn     = sqlite3.connect(database_file)
        analyzer = StringAnalyzer()

        # -- Loop through artist directories

        for artist_dir in os.listdir(root_path):
            artist_root_path = os.path.join(root_path, artist_dir)
            if (os.path.isdir(artist_root_path)) and (artist_dir not in self.dir_exceptions):
                full_artist_name = artist_dir.replace("_", " ")
                dial_compatible_artist_name = artist_dir.replace("_", "").lower()

                print("name: {}".format(full_artist_name))
                #print("dcn:  {}".format(dial_compatible_artist_name))
                words = analyzer.analyze(full_artist_name)
                #print(words)

                # -- Get artist ID
                # -- Check to see if artist exists in artists table

                artist_id = None

                cursor = conn.execute("""\
                        SELECT id
                          FROM artists
                         WHERE dial_compatible_artist_name = ?
                         LIMIT 1""", (dial_compatible_artist_name,))
                row = cursor.fetchone()

                if row is not None:
                    artist_id = row[0]
                else:
                    # We need to save this artist to the artists table.
                    print("    ...Adding artist to database...")
                    cursor = conn.execute("""\
                            INSERT INTO artists
                            (dial_compatible_artist_name, full_artist_name)
                            VALUES (?, ?)""",
                            (dial_compatible_artist_name,full_artist_name))

                    conn.commit()
                    artist_id = cursor.lastrowid
                    print("New artist saved as id: {}".format(artist_id))


                # -- save all of the search_strings which have
                # -- been assembled from the artists name


                for w in words:
                    try:
                        cursor.execute("""\
                            INSERT INTO artist_search_strings
                                        (search_string, artist_id)
                                 VALUES (?,?);""", (w, artist_id))
                    except:
                        # ignoring errors from sqlite3 for duplicate entries.
                        pass
                conn.commit()

                ################################
                # -- Add Albums to the database

                for album_dir in os.listdir(artist_root_path):
                    album_name = None
                    album_year = "0000"
                    album_art_path = ""

                    album_root_path = os.path.join(artist_root_path, album_dir)
                    if (os.path.isdir(album_root_path)) and (album_dir not in self.dir_exceptions):
                        match_obj = re.match(r'^(\d\d\d\d)-(.*)', album_dir)
                        if match_obj.groups() is not None:
                            album_year = match_obj.group(1)
                            album_name = match_obj.group(2)
                        else:
                            album_name = album_dir


                    full_album_name = album_name.replace("_", " ")
                    dial_compatible_album_name = album_name.replace("_", "").lower()


                    if os.path.isfile(album_root_path + "/cover.jpg"):
                        album_art_path = album_root_path + "/cover.jpg"

                    #print("    album name: {}".format(full_album_name))
                    #words = analyzer.analyze(full_album_name)
                    #print("    words:      {}".format(words))

                    album_id = None

                    cursor = conn.execute("""\
                            SELECT id
                              FROM albums
                             WHERE dial_compatible_album_name = ?
                             LIMIT 1""", (dial_compatible_album_name,))
                    row = cursor.fetchone()

                    if row is not None:
                        print("[Warning] Album alread exists in database: {}".format(dial_compatible_album_name))
                        album_id = row[0]
                    else:
                        # We need to save this album to the albums table.
                        print("    ...Adding album to database...")
                        cursor = conn.execute("""\
                                INSERT INTO albums
                                            (artist_id,
                                            dial_compatible_album_name,
                                            full_album_name,
                                            album_path,
                                            album_year,
                                            album_art)
                                VALUES (?, ?, ?, ?, ?, ?)""",
                                (artist_id, dial_compatible_album_name, full_album_name, album_root_path, album_year, album_art_path))

                        conn.commit()
                        album_id = cursor.lastrowid
                        print("New album saved as id: {}".format(album_id))


            
        conn.close()

#            for name in files:
#                #if name[-4:].lower() == '.mp3':
#                #if name[-5:].lower() == '.flac':
#                if 1:
#                    #print "NAME: ", name
#
#                    path = os.path.join(root,name)
#                    alphaNumPattern = re.compile('[\W_]+')
#
#                    # Extract Tags From File
#                    try:
#                        id3 = ID3(path)
#                    except:
#                        errors.append(path)
#                        id3 = None
#
#
#                    # Insert each file into the id3 table
#                    if id3 != None:
#                        #cursor.execute("INSERT INTO id3(location, artist, title, album, genre, comment, duration, length, size) VALUES(?,?,?,?,?,?,?,?,?)", (path,id3.artist,id3.title,id3.album,id3.genre,id3.comment,id3.duration,id3.length,id3.size))
#                        last_id3_id = cursor.lastrowid
#                        #for field in ['artist', 'title', 'album', 'comment', 'genre']:
#
#
#                        # Create the artist tables
#                        for field in ['artist']:
#                            #print "Field: ", getattr(id3, field)
#                            full_artist_name = getattr(id3, field)
#                            dial_compatible_artist_name = full_artist_name
#                            dial_compatible_artist_name = alphaNumPattern.sub('', dial_compatible_artist_name)
#                            dial_compatible_artist_name = dial_compatible_artist_name.lower()
#
#                            # Break up artist name into search_strings and put in artist_search_strings table
#
#                            words = analyzer.analyze(getattr(id3, field))
#                            words.append(dial_compatible_artist_name)
#                            for word in words:
#                                #cursor.execute("INSERT INTO id3index(id3_id,search_string,field) VALUES (?,?,?);", (full_artist_name, word, field))
#                                try:
#                                    cursor.execute("INSERT INTO artist_search_strings(search_string,full_artist_name) VALUES (?,?);", (word, full_artist_name))
#                                except:
#                                    pass
#
#                            # Put artist in artists table
#
#                            try:
#                                cursor.execute("INSERT INTO artists(dial_compatible_artist_name,full_artist_name) VALUES (?,?);", (dial_compatible_artist_name, full_artist_name))
#                            except:
#                                pass
#
#                            cnx.commit()
#                # Display info about the whole process...
#
#                #cursor.execute('SELECT COUNT(*) AS nbrows FROM id3index LIMIT 1;')
#        #for line in cursor:
#            #print 'index size: ' + str(line["nbrows"])
#        #cnx.commit()
#        #if len(errors) > 0:
#            #print ""
#            #print "---- Errors ----"
#            #print ""
#            #for error in errors:
#                #print error




if __name__ == '__main__':
    #if len(sys.argv) < 2:
        #print 'Usage: tags.py [your music dir]'
    #else:
        #index = Index()
        #index.build(sys.argv[1])

    index = Index()
    index.build(music_path)

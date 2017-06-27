#!/usr/bin/env python
# http://www.desfrenes.com/blog/post/python-mp3-indexer-look-up

import os, sys, re, time
import mutagen
import sqlite3
import unicodedata
from colorz import colorz

# change this path to your sqlite database
#dsn = '/Users/mickael/python_sandbox/tags/id3.sqlite'
database_file = 'subibox.sqlite'
music_path = '/home/equant/beets'
#music_path = '/mnt/toshiba/beets/'

DO_LAST_FM = True

art_path_hack = [
        '/mnt/toshiba/',
        '/mnt/jukebox/',
]

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


if DO_LAST_FM:
    try:
        from lastfm import SubiLastFm
        LastFM = SubiLastFm()
    except ModuleNotFoundError:
        print("You need to install pylast or set DO_LAST_FM = False.")
        sys.exit(0)

def get_lastfm_tags(artist_name):

    if DO_LAST_FM:
        foo = LastFM.last.get_artist(artist_name).get_top_tags()
        tags = []
        for thing in foo:
            if int(thing.weight) > 80:
                print("{} : {}".format(thing.item.name, thing.weight))
                tags.append(thing.item.name)
        return tags
    return None

# -- Create database file by traversing music directory

class Index:

    #dir_exceptions = ['Unknown', 'Soundtracks', 'Compilations']
    dir_exceptions = []

    def build(self,root_path):

        conn     = sqlite3.connect(database_file)
        analyzer = StringAnalyzer()

        ####################################
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

                if row is None:
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
                else:
                    # Arstis already existed.
                    artist_id = row[0]

                ################
                # -- LastFM Tags

                tags = get_lastfm_tags(full_artist_name)
                if tags is not None:
                    for tag in tags:
                        try:
                            cursor.execute("""\
                                INSERT INTO artist_tags
                                            (artist_id, tag)
                                     VALUES (?,?);""", (artist_id, tag))
                        except:
                            # ignoring errors from sqlite3 for duplicate entries.
                            pass
                        conn.commit()
                sys.exit(0)

                ###############################
                # -- Add Albums to the database

                for album_dir in os.listdir(artist_root_path):
                    album_name = None
                    album_year = "0000"
                    album_art_path = ""

                    album_root_path = os.path.join(artist_root_path, album_dir)
                    if (os.path.isdir(album_root_path)) and (album_dir not in self.dir_exceptions):
                        match_obj = re.match(r'^(\d\d\d\d)-(.*)', album_dir)
                        if match_obj is not None: 
                            if match_obj.groups() is not None:
                                album_year = match_obj.group(1)
                                album_name = match_obj.group(2)
                            else:
                                album_name = album_dir
                        else:
                            album_name = album_dir

                    if album_name is None:
                        print("Skipping album_root_path: {}".format(album_root_path))
                        break

                    full_album_name = album_name.replace("_", " ")
                    dial_compatible_album_name = album_name.replace("_", "").lower()


                    if os.path.isfile(album_root_path + "/cover.jpg"):
                        album_art_path = album_root_path + "/cover.jpg"

                    album_path     = album_root_path.replace(music_path, "")
                    album_art_path = album_art_path.replace(art_path_hack[0], art_path_hack[1])

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
                                (artist_id, dial_compatible_album_name, full_album_name, album_path, album_year, album_art_path))

                        conn.commit()
                        album_id = cursor.lastrowid
                        print("New album saved as id: {}".format(album_id))
                    if len(album_art_path) > 0:
                        self.write_album_art_colors(album_id, album_art_path, conn)
            
        conn.close()


    def delete_album_colors(self, album_id, conn):
        print("DELETING COLORS: {}".format(album_id))
        album_id = str(album_id)
        cursor = conn.execute("""\
                DELETE FROM album_colors WHERE album_id = ?
                """, (album_id,))
        conn.commit()
        print("DONE DELETING COLORS: {}".format(album_id))


    def write_album_art_colors(self, album_id, album_path, conn):
        print("DEBUG: Write colors {} {}".format(album_id, album_path))
        try:
            colors = list(colorz(album_path))
        except OSError:
            print("Error with album_path: {}".format(album_path))
            return
        print("DEBUG: Colors: {}".format(colors))
        if len(colors) > 0:
            self.delete_album_colors(album_id, conn)
        else:
            print("No colors found for {}".format(album_path))
            return

        for c in colors:
            # Get sum of rgb 
            c = c[1:]  # get rid of leading "#"
            color_sum = sum([int(c[i:i+2],16) for i in range(0, len(c), 2)])
            print("Color: {} ({})".format(c, color_sum))
            cursor = conn.execute("""\
                    INSERT INTO album_colors
                                (album_id, color, color_sum)
                         VALUES (?, ?, ?)
                    """, (album_id, c, color_sum)
            )
            conn.commit()


if __name__ == '__main__':
    index = Index()
    index.build(music_path)



"""
DELETE FROM artists;
DELETE FROM albums;
DELETE FROM album_colors;
DELETE FROM artist_search_strings; 
"""

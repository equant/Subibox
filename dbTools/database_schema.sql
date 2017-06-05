CREATE TABLE artists(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dial_compatible_artist_name,
    full_artist_name
);

CREATE TABLE albums(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    artist_id,
    dial_compatible_album_name,
    full_album_name,
    album_path,
    album_year,
    album_art
);

CREATE TABLE artist_search_strings(
    search_string,
    artist_id,
    PRIMARY KEY(search_string, artist_id)
);

# The old system...
#CREATE TABLE artists(dial_compatible_artist_name, full_artist_name, PRIMARY KEY(dial_compatible_artist_name, full_artist_name));
#CREATE TABLE artist_searchstrings(search_string, full_artist_name, PRIMARY KEY(keyword, full_artist_name));
#CREATE TABLE id3index(id INTEGER PRIMARY KEY AUTOINCREMENT,id3_id, keyword, field);
#CREATE TABLE id3(id INTEGER PRIMARY KEY AUTOINCREMENT,location UNIQUE, artist, title, album, genre, comment, duration, length, size);
#CREATE INDEX keyword_idx ON id3index(keyword);


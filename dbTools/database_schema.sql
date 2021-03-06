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
CREATE TABLE album_colors(
    album_id,
    color
, color_sum);
CREATE TABLE artist_search_strings(
    search_string,
    artist_id,
    PRIMARY KEY(search_string, artist_id)
);
CREATE TABLE artist_tags(
    tag,
    artist_id,
    weight,
    PRIMARY KEY(tag, artist_id)
);

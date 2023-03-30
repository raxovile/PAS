import json
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import psycopg2


def get_configuration():
    root_dir = os.getcwd()
    file_path = root_dir+'/genre-playlist-generator/config.json'
    with open(file_path, 'r', encoding = 'utf-8') as file:
        config = json.load(file)

    return config

def authenticate_spotify(config):
    return spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=config["CLIENT_ID"],
                                               client_secret=config["CLIENT_SECRET"],
                                               redirect_uri=config["REDIRECT_URI"],
                                               scope=config["SCOPE"],
                                               username=config["USERNAME"]))

def fetch_all_tracks_from_spotify(sp):
    results = sp.current_user_saved_tracks()
    all_songs = []
    counter = 0
    while results:
        print(f"Processing  {counter * 20}")
        for item in results['items']:
            track = item['track']
            song_id = track['id']
            song_name = track['name']
            song_artist = track['artists'][0]['name']
            song_album = track['album']['name']

            song_genres = sp.artist(track['artists'][0]['id'])['genres']
            song = {
                "id": song_id,
                "name": song_name,
                "artist": song_artist,
                "album": song_album,
                "genres": song_genres
            }
            all_songs.append(song)
        if results['next']:
            results = sp.next(results)
        else:
            results = None
        
        counter =+ counter + 1
    return all_songs

def add_all_songs_into_database(config):
    sp = authenticate_spotify(config)
    all_songs = fetch_all_tracks_from_spotify(sp)

    conn = psycopg2.connect(
    host=config["HOST"],
    database=config["DATABASE"],
    user=config["USER"],
    password=config["PASSWORD"]
    )

      # databasesor erstellen
    database = conn.cursor()

    # Tabelle "artists" erstellen
    database.execute("CREATE TABLE IF NOT EXISTS artists (id SERIAL PRIMARY KEY, name VARCHAR(255))")

    # Tabelle "albums" erstellen
    database.execute("CREATE TABLE IF NOT EXISTS albums (id SERIAL PRIMARY KEY, name VARCHAR(255), artist_id INTEGER REFERENCES artists (id) ON DELETE CASCADE)")

    # Tabelle "genres" erstellen
    database.execute("CREATE TABLE IF NOT EXISTS genres (id SERIAL PRIMARY KEY, name VARCHAR(255))")

    # Tabelle "songs" erstellen
    database.execute("CREATE TABLE IF NOT EXISTS songs (id SERIAL PRIMARY KEY, name VARCHAR(255), artist_id INTEGER REFERENCES artists (id) ON DELETE CASCADE, album_id INTEGER REFERENCES albums (id) ON DELETE CASCADE, genre_id INTEGER REFERENCES genres (id) ON DELETE CASCADE)")

    for idx,song in enumerate(all_songs):
        # Artist einfügen oder falls schon vorhanden die ID abrufen
        print(f"Start processing song {idx} from {len(all_songs)}")
    
        database.execute("SELECT id FROM artists WHERE name = %s", (song['artist'],))
        result = database.fetchone()
        if result is None:
            database.execute("INSERT INTO artists (name) VALUES (%s) RETURNING id", (song['artist'],))
            artist_id = database.fetchone()[0]
        else:
            artist_id = result[0]
    
        # Album einfügen oder falls schon vorhanden die ID abrufen
        database.execute("SELECT id FROM albums WHERE name = %s AND artist_id = %s", (song['album'], artist_id))
        result = database.fetchone()
        if result is None:
            database.execute("INSERT INTO albums (name, artist_id) VALUES (%s, %s) RETURNING id", (song['album'], artist_id))
            album_id = database.fetchone()[0]
        else:
            album_id = result[0]
    
        # Genre(s) einfügen oder falls schon vorhanden die ID(s) abrufen
        for genre in song['genres']:
            database.execute("SELECT id FROM genres WHERE name = %s", (genre,))
            result = database.fetchone()
            if result is None:
                database.execute("INSERT INTO genres (name) VALUES (%s) RETURNING id", (genre,))
                genre_id = database.fetchone()[0]
            else:
                genre_id = result[0]
            # Song einfügen
            database.execute("INSERT INTO songs (name, artist_id, album_id, genre_id) VALUES (%s, %s, %s, %s)", (song['name'], artist_id, album_id, genre_id) )
    




def main():
    config = get_configuration()
    add_all_songs_into_database(config)

if __name__ == '__main__':
    main()
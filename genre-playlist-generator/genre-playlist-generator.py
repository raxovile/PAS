import os
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth


def get_configuration():
    root_dir = os.getcwd()
    file_path = root_dir+'/genre-playlist-generator/config.json'
    with open(file_path, 'r', encoding = 'utf-8') as file:
        config = json.load(file)

def authenticate_spotify(config):
    return spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=config["CLIENTID"],
                                               client_secret=config["CLIENTSECRET"],
                                               redirect_uri=config["REDIRECT_URI"],
                                               scope=config["SCOPE"],
                                               username=config["username"]))

def fetch_all_tracks_from_spotify(sp):
    results = sp.databaserent_user_saved_tracks()
    all_songs = []
    while results:
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
    return all_songs

def main():
    config = get_configuration()
    spotify = authenticate_spotify(config)

if __name__ == '__main__':
    main()
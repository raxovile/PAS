import json
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import psycopg2
from difflib import SequenceMatcher


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

def add_all_songs_into_json_file(config):
    sp = authenticate_spotify(config)
    all_songs = fetch_all_tracks_from_spotify(sp)

    with open('all_songs.json', 'w', encoding = 'utf-8') as f:
        json.dump(all_songs, f)

def get_all_genres_from_file():
    with open('all_songs.json', 'r') as f:
        all_songs = json.load(f)
    
    all_genres = {}
    for song in all_songs:
        for genre in song['genres']:
            if genre not in all_genres:
                all_genres[genre] = 1
            else:
                all_genres[genre] += 1
    
    # Sort the list of genres based on similarity in name
    all_genres_list = [{'name': k, 'count': v} for k, v in all_genres.items()]
    all_genres_list.sort(key=lambda x: SequenceMatcher(None, x['name'].lower(), 'genre').ratio(), reverse=True)
    
    with open('genre.json', 'w', encoding = 'utf-8') as f:
        json.dump(all_genres, f)

    return all_genres

def group_genres_by_keyword():
    with open('genre.json', 'r', encoding = 'utf-8') as f:
       genres = json.load(f)

    # Erstelle ein Wörterbuch, das jedem eindeutigen Wort im Genre-Namen eine Liste von Genres zuordnet, die das Wort enthalten
    keyword_dict = {}
    for genre in genres:
        words = genre.split()
        for word in words:
            if word not in keyword_dict:
                keyword_dict[word] = {'genres':[], 'count':0}
            keyword_dict[word]['genres'].append(genre)
            keyword_dict[word]['count'] += 1
    
    # Erstelle ein Wörterbuch, das jedem eindeutigen Wort im Genre-Namen eine Liste von Subgenres zuordnet, die das Wort enthalten
    grouped_dict = {}
    for word in keyword_dict:
        grouped_dict[word] = {'subgenres':[], 'count': keyword_dict[word]['count']}
        for genre in keyword_dict[word]['genres']:
            subgenres = genre.split("/")
            for subgenre in subgenres:
                if subgenre not in grouped_dict[word]['subgenres']:
                    grouped_dict[word]['subgenres'].append(subgenre)
    
    # Entferne Wörter, die nur in einem Subgenre vorkommen
    for word in list(grouped_dict.keys()):
        subgenres = grouped_dict[word]['subgenres']
        if len(subgenres) == 1:
            del grouped_dict[word]
    
    with open('genre_list.json', 'w', encoding = 'utf-8') as f:
        json.dump(grouped_dict, f)
    return grouped_dict

def create_genre_playlists():
    with open('genre_list.json', 'r', encoding='utf-8') as f:
        genres = json.load(f)

    with open('all_songs.json', 'r', encoding='utf-8') as f:
        all_songs = json.load(f)

    playlists = {}
    for genre in genres:
        if len(genres[genre]['subgenres']) < 2:
            continue
        playlist_name = genre

        playlist_songs = []
        for song in all_songs:
            if any(subgenre in genres[genre]['subgenres'] for subgenre in song['genres']):
                playlist_songs.append({
                    'id': song['id'],
                    'name': song['name'],
                    'genre': genre
                })

        if len(playlist_songs) >= 30:
            playlists[playlist_name] = {
                'songs': playlist_songs,
                'song_count': len(playlist_songs)
            }

    playlists['total_count'] = len(playlists)

    with open('playlists.json', 'w', encoding='utf-8') as f:
        json.dump(playlists, f)

def main():
    config = get_configuration()
    # add_all_songs_into_json_file(config)s
    get_all_genres_from_file()
    group_genres_by_keyword()
    create_genre_playlists()


if __name__ == '__main__':
    main()
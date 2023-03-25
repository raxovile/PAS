import os

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


def main():
    config = get_configuration()
    spotify = authenticate_spotify(config)

if __name__ == '__main__':
    main()
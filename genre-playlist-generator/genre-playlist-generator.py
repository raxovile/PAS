import os

def get_configuration():
    root_dir = os.getcwd()
    file_path = root_dir+'/genre-playlist-generator/config.json'
    with open(file_path, 'r', encoding = 'utf-8') as file:
        config = json.load(file)

def main():
    config = get_configuration()

if __name__ == '__main__':
    main()
import os
from src.display import colored_prompt, welcome_screen, menu
from src.explorer import MediaExplorer
from src.youtube import YouTubeManager
from src.config import ConfigManager
from rich.console import Console


console = Console()

class Jukebox(object):
    def __init__(self):
        self.config_manager = ConfigManager()
        self.init_paths()
        self.youtube_manager = YouTubeManager(self.music_path, self.movies_path)
        self.media_explorer = MediaExplorer(
            db_path='jukebox.db',
            music_path=self.music_path,
            movies_path=self.movies_path,
            playlists_path=self.playlists_path
        )
        self.user_name = self.config_manager.config['user_name']
        self.Radio = 'https://media-ice.musicradio.com/Heart80s'
        self.from_youtube = False
        self.currentMediaType = "Music"  # will be either Music or Video
        self.current_media = -1
        self.videoType = 'Youtube'  # will be Youtube or Movie
        self.downloadMovie = False
        self.checkForPlaylist = False
        self.welcome_screen = welcome_screen
        self.colored_prompt = colored_prompt
        self.menu = menu

    def init_paths(self):
        self.music_path = self.config_manager.config['music_path']
        self.movies_path = self.config_manager.config['movies_path']
        self.playlists_path = self.config_manager.config['playlists_path']

    def update_paths(self):
        self.music_path = self.config_manager.config['music_path']
        self.movies_path = self.config_manager.config['movies_path']
        self.playlists_path = self.config_manager.config['playlists_path']
        
        # Update the paths in media_explorer as well
        self.media_explorer.music_path = self.music_path
        self.media_explorer.movies_path = self.movies_path
        self.media_explorer.playlists_path = self.playlists_path

        self.youtube_manager.music_path = self.music_path
        self.youtube_manager.movies_path = self.movies_path

    def start(self):
        query = ''
        self.current_media = -1  # reset current media type
        self.welcome_screen(self.user_name)
        while query != 'q':
            self.current_media = -1
            prompt = colored_prompt(self.user_name)
            query = console.input(prompt)
            if query == 'help':
                self.menu()
            if query == 'r':
                print(query)
                self.currentMediaType == 'Music'
                self.current_media = self.Radio
            if query == 'u':
                self.user_name = self.config_manager.update_username(self.user_name)
            if query == 'd':
                self.update_directory()
            if query == 's':
                self.media_explorer.index_all()
            if query == 'e':
                self.media_explorer.explore(self.currentMediaType, self.current_media, self.videoType, self.Radio)

            elif 'youtube.com' in query:
                if ' -a' in query:
                    query = query.replace(' -a', '')
                    self.youtube_manager.download_song(query)
                else:
                    self.youtube_manager.download_video(query)

            elif ' -a' in query:
                self.currentMediaType = "Music"
                query = query.replace(' -a', '')
                if ' -p' in query:
                    self.checkForPlaylist = True
                    query = query.replace(' -p', '')
                print(query)
                self.current_media = self.search(query)
            elif ' -v' in query:
                self.currentMediaType = "Video"
                query = query.replace(' -v', '')
                if ' -p' in query:
                    self.checkForPlaylist = True
                    query = query.replace(' -p', '')
                if ' -m' in query:
                    query = query.replace(' -m', '')
                    self.videoType = "Movie"
                    if ' -d' in query:
                        query = query.replace(' -d', '')
                        self.downloadMovie = True
                elif ' -yt' in query:
                    query = query.replace(' -yt', '')
                    self.videoType = "Youtube"

                print(query)
                self.current_media = self.search(query)
                print("Current media set as: ", self.current_media)

            elif self.current_media == -1 and query != 'q' and query != 'help' and query != 'u' and query != 's' and query != 'd':
                print('Specify if you want audio/video by adding -a or -v after your query (type "help" for more info)')

            if self.current_media != -1:
                self.media_explorer.play(self.current_media, self.currentMediaType, self.videoType, self.Radio)

                if self.current_media != self.Radio and self.videoType != 'Movie':
                    to_download = input('\n\nSave to directory? (y/n)')
                    if to_download == 'y':
                        print(self.current_media)
                        self.youtube_manager.download(self.current_media, self.currentMediaType)
                        self.media_explorer.index_all()

    def update_directory(self):
        print("Which directory would you like to update?")
        print("1. Music Path")
        print("2. Movies Path")
        print("3. Playlists Path")
        choice = input("Enter the number of your choice: ").strip()
        if choice == '1':
            self.config_manager.update_directory('music_path')
        elif choice == '2':
            self.config_manager.update_directory('movies_path')
        elif choice == '3':
            self.config_manager.update_directory('playlists_path')
        else:
            print("Invalid choice. Directory update cancelled.")
        self.update_paths()

    def search(self, query):
        # Case 1: Check if media is already in playlist directory.
        media = self.media_explorer.search_db_directory(query, self.currentMediaType)  # if self.search_db_directory(query) != -1 else ''
        print("****", self.currentMediaType)
        if media:
            check_online = input(f"Found {media} in your local directory:\nWould you like to play this? (y/n)")
            print("You entered: ", check_online)
            if check_online == 'y':
                return media

        # Case 2: Search online for media
        media = -1
        if self.currentMediaType == 'Music':
            self.from_youtube, media = self.youtube_manager.search_youtube(query, self.checkForPlaylist)
        elif self.currentMediaType == 'Video':
            if self.videoType == 'Movie':
                if self.downloadMovie:
                    print("would be downloading")
                    os.system(f'mov-cli -s films {query} -d')
                    self.downloadMovie = False
                    return
                else:
                    os.system(f'mov-cli -s films {query}')
            elif self.videoType == 'Youtube':
                self.from_youtube, media = self.youtube_manager.search_youtube(query, self.checkForPlaylist)

            # default as youtube search for now
            else:
                self.from_youtube, media = self.youtube_manager.search_youtube(query, self.checkForPlaylist)

        return media

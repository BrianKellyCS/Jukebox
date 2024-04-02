import re,urllib.parse,urllib.request
import os
import colorama
import json
import sqlite3


colorama.init()

class Color:
    RESET = colorama.Style.RESET_ALL
    RED = colorama.Fore.LIGHTRED_EX    # Brighter Red
    GREEN = colorama.Fore.LIGHTGREEN_EX  # Neon Green
    YELLOW = colorama.Fore.LIGHTYELLOW_EX # Brighter Yellow
    BLUE = colorama.Fore.LIGHTBLUE_EX
    MAGENTA = colorama.Fore.LIGHTMAGENTA_EX
    CYAN = colorama.Fore.LIGHTCYAN_EX



class Jukebox(object):
    def __init__(self):
        with open('config.json', 'r') as config_file:
            self.config = json.load(config_file)
        
        self.music_path = self.config['directories']['music_path']
        self.movies_path = self.config['directories']['movies_path']
        self.playlists_path = self.config['directories']['playlists_path']
        self.user_name = self.config['user_name']
        self.Radio = 'https://media-ice.musicradio.com/Heart80s'
        self.from_youtube = False
        self.current_yt_song = ''
        self.currentMediaType = "Music"   #will be either Music or Video
        self.current_media = -1
        self.android = self.is_android()
        self.videoType = 'Youtube' #will be Youtube or Movie
        self.downloadMovie = False
        self.checkForPlaylist = False

        self.init_db()
        self.index_all()


    def is_android(self):
        # Check for a common Android environment variable
        if 'ANDROID_DATA' in os.environ:
            return True

            
        # Not detected as Android
        return False

    def init_db(self):
        conn = sqlite3.connect('jukebox.db')
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS directories (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            path TEXT NOT NULL UNIQUE,  
            parent_id INTEGER,
            is_folder BOOLEAN NOT NULL,
            FOREIGN KEY (parent_id) REFERENCES directories (id)
        )
        ''')
        conn.commit()
        conn.close()

    def index_directory(self,path, parent_id=None, conn=None, seen_paths=None):
        if conn is None:
            conn = sqlite3.connect('jukebox.db')
            created_new_connection = True
        else:
            created_new_connection = False

        if seen_paths is None:
            seen_paths = set()

        cursor = conn.cursor()

        for entry in os.scandir(path):
            seen_paths.add(entry.path)  # Track seen path
            is_folder = entry.is_dir()

            cursor.execute("SELECT id FROM directories WHERE path = ?", (entry.path,))
            db_entry = cursor.fetchone()

            if db_entry:
                # If exists but moved, update the parent_id and path
                cursor.execute('''
                UPDATE directories SET parent_id = ?, name = ?, is_folder = ?
                WHERE path = ?
                ''', (parent_id, entry.name, is_folder, entry.path))
            else:
                # Insert new entry
                cursor.execute('''
                INSERT INTO directories (name, path, parent_id, is_folder)
                VALUES (?, ?, ?, ?)
                ''', (entry.name, entry.path, parent_id, is_folder))
            
            if is_folder:
                # Recurse into the directory
                new_parent_id = cursor.lastrowid if not db_entry else db_entry[0]
                self.index_directory(entry.path, new_parent_id, conn, seen_paths)

        if created_new_connection:
            conn.commit()
            conn.close()

    def explore(self):
        media_options = {
            1: ("Media", self.movies_path),
            2: ("Music", self.music_path),
            3: ("Playlists", self.playlists_path)
        }
        
        while True:
            print("Select media type to explore:")
            for key, (name, _) in media_options.items():
                print(f"({key}) {name}")
            print("(q) Quit")
            
            choice = input("\nEnter your choice: ").strip().lower()

            
            if choice == 'q':
                break
            
            try:
                choice_idx = int(choice)
                if choice_idx in media_options:
                    if choice_idx == 1:
                        self.currentMediaType = "Video"
                    else:
                        self.currentMediaType = "Music"
                    _, start_path = media_options[choice_idx]
                    print(self.currentMediaType,")!!!!!!!!!!!!!!!!!!!!!!!!")
                    self.navigate_directory(start_path)
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def navigate_directory(self, current_path):
        history_stack = []

        while True:
            print(f"\nExploring: {current_path}\n")
            dirs_and_files = os.listdir(current_path)
            dirs_and_files.sort(key=lambda x: (not os.path.isdir(os.path.join(current_path, x)), x.lower()))

            for idx, entry in enumerate(dirs_and_files, start=1):
                entry_path = os.path.join(current_path, entry)
                print(f"({idx}) {'[D]' if os.path.isdir(entry_path) else '[F]'} {entry}")

            print("\n(0) Go Back")
            choice = input("\nEnter number to explore or 'q' to quit: ").strip()

            if choice.lower() == 'q':
                break
            elif choice == '0':
                if history_stack:
                    current_path = history_stack.pop()
                else:
                    print("No more parent directories.")
                    break  # Exit the navigation if there are no more parent directories
            else:
                try:
                    choice_idx = int(choice) - 1
                    if choice_idx >= 0 and choice_idx < len(dirs_and_files):
                        selected_path = os.path.join(current_path, dirs_and_files[choice_idx])
                        if os.path.isdir(selected_path):
                            history_stack.append(current_path)
                            current_path = selected_path
                        else:
                            print(f"Selected File: {selected_path}")
                            self.play(f'"{selected_path}"')
                            # Add logic here for file actions (e.g., playing a file)
                    else:
                        print("Invalid selection.")
                except ValueError:
                    print("Please enter a valid number.")

    def list_directory_contents(self,parent_id=None, level=0):
        conn = sqlite3.connect('jukebox.db')
        cursor = conn.cursor()
        if parent_id is None:
            cursor.execute("SELECT * FROM directories WHERE parent_id IS NULL")
        else:
            cursor.execute("SELECT * FROM directories WHERE parent_id = ?", (parent_id,))
        items = cursor.fetchall()

        for item in items:
            print("  " * level + f"- {item[1]} (ID: {item[0]}, Path: {item[2]})")
            if item[4]:  # Recurse into subdirectories
                self.list_directory_contents(item[0], level + 1)

        conn.close()

    def index_all(self,):
        seen_paths = set()  # Initialize seen_paths once for all indexing operations
        conn = sqlite3.connect('jukebox.db')  # Use a single connection for all operations

        self.index_directory(self.movies_path, None, conn, seen_paths)
        self.index_directory(self.music_path, None, conn, seen_paths)
        self.index_directory(self.playlists_path, None, conn, seen_paths)

        # Now perform the deletion of unseen paths after all indexing is done
        cursor = conn.cursor()
        cursor.execute("SELECT path FROM directories")
        all_paths = set(path for (path,) in cursor.fetchall())
        missing_paths = all_paths - seen_paths
        for missing_path in missing_paths:
            cursor.execute("DELETE FROM directories WHERE path = ?", (missing_path,))

        conn.commit()
        conn.close()

    def save_config(self):
        with open('config.json', 'w') as config_file:
            json.dump(self.config, config_file, indent=4)
        print(Color.GREEN + "Configuration saved." + Color.RESET)

    def welcome_screen(self):
        ascii_art = """
   ___       _        _               
  |_  |     | |      | |              
    | |_   _| | _____| |__   _____  __
    | | | | | |/ / _ \ '_ \ / _ \ \/ /
/\__/ / |_| |   <  __/ |_) | (_) >  < 
\____/ \__,_|_|\_\___|_.__/ \___/_/\_\                 
        """
        print(Color.CYAN + ascii_art + Color.RESET)
        if self.user_name != 'user':
            print(Color.YELLOW + f"Welcome back, {self.user_name}!" + Color.RESET)
        else:
            print(Color.YELLOW + f"Welcome to the Terminal Jukebox!" + Color.RESET)       
        print(Color.GREEN + "Type 'help' to see the command list and MPV controls\n" + Color.RESET)

    def colored_prompt(self):

        prompt = f"{Color.RED}{self.user_name}{Color.RESET}" \
                f"{Color.GREEN}{'@'}{Color.RESET}" \
                f"{Color.YELLOW}{'Jukebox'}{Color.RESET}" \
                f"{Color.BLUE}{':'}{Color.RESET}" \
                f"{Color.MAGENTA}{'~'}{Color.RESET}" \
                f"{Color.CYAN}{'>'}{Color.RESET} "
        
        return prompt

    def update_username(self):
        new_user_name = input(Color.GREEN + "Enter your new user name: " + Color.RESET).strip()
        if new_user_name:  # Check if the user actually entered something
            self.user_name = new_user_name
            self.config['user_name'] = new_user_name
            self.save_config()  # Save the updated configuration
            print(Color.YELLOW + f"Username updated to {new_user_name}." + Color.RESET)
        else:
            print(Color.RED + "Username update cancelled." + Color.RESET)

    def start(self):
        query = ''
        self.current_media = -1 #reset current media type
        self.welcome_screen()
        while query != 'q':
            self.current_media = -1
            query = input(self.colored_prompt())
            if query == 'help':
                self.menu()
            if query == 'r':
                print(query)
                self.currentMediaType == 'Music'
                self.current_media = self.Radio
            if query == 'u':
                self.update_username()
            if query == 's':
                self.index_all()
            if query == 'e':
                self.explore()

            elif 'www.youtube.com' in query:
                if ' -a' in query:
                    query = query.replace(' -a','')
                    self.download_song(query)
                else:
                    self.download_video(query)

            elif ' -a' in query:
                self.currentMediaType = "Music"
                self.checkForPlaylist = False
                query = query.replace(' -a','')
                if ' -p' in query:
                    self.checkForPlaylist = True
                    query = query.replace(' -p','')
                print(query)
                self.current_media = self.search(query)
            elif ' -v' in query:
                self.currentMediaType = "Video"
                self.videoType = "Youtube"
                self.checkForPlaylist = False
                self.downloadMovie = False
                query = query.replace(' -v','')
                if ' -p' in query:
                    self.checkForPlaylist = True
                    query = query.replace(' -p','')
                if ' -m' in query:
                    query = query.replace(' -m','')
                    self.videoType = "Movie"
                    if ' -d' in query:
                        query = query.replace(' -d','')
                        self.downloadMovie = True
                elif ' -yt' in query:
                    query = query.replace(' -yt','')
                    self.videoType = "Youtube"    

                print(query)
                self.current_media = self.search(query)
                print("Current media set as: ", self.current_media)


            elif self.current_media == -1 and query != 'q' and query != 'help':
                print('Specify if you want audio/video by adding -a or -v after your query (type "help" for more info)')
                

            if self.current_media != -1:
                self.play(self.current_media)

                if self.current_media != self.Radio and self.from_youtube:
                    to_download = input('\n\nSave to directory? (y/n)')
                    if to_download == 'y':
                        self.download()

    def download_song(self,query):
        os.system(f'yt-dlp -x -f m4a -o "{self.music_path}/%(title)s.%(ext)s" {query}')

    def download_video(self,query):
        os.system(f'yt-dlp -o "{self.movies_path}/%(title)s.%(ext)s" {query}')

    def menu(self):
        print('\n\n\tCommand\t\tDesc.\t\t\t\tUsage\n')
        print('\te\t\tExplore Directories\t\te\n')
        print('\ts\t\tRe-scan Directories\t\ts\n')
        print('\tq\t\tQuit Jukebox\t\t\tq\n')
        print('\tu\t\tUpdate Username\t\t\tu\n')
        print('\tr\t\tRadio\t\t\t\tr\n')
        print('\t-a\t\tAudio\t\t\t\t{search query} -a\n')
        print('\t-v\t\tVideo\t\t\t\t{search query} -v\n')

        # Added explanation for YouTube link downloading feature
        print('\tYouTube Link\tDownload from YouTube\t\tPaste a YouTube link directly to download video.\n'
            '\t\t\t\t\t\t\tAdd "-a" after the link to download audio only.\n'
            '\t\t\t\t\t\t\tVideos are saved to the Movies directory;\n'
            '\t\t\t\t\t\t\taudio files are saved to the Music directory.\n')

        print('\n\tMPV Playback Controls:\n')
        print('\tSPACE\t\tPlay/Pause\n')
        print('\tq\t\tStop Playback & Quit MPV\n')
        print('\t>\t\tNext in Playlist\n')
        print('\t<\t\tPrevious in Playlist\n')
        print('\t←/→\t\tSeek Backwards/Forwards\n')
        print('\tm\t\tMute\n')
        print('\tf\t\tToggle Fullscreen\n')
        print('\t9/0\t\tDecrease/Increase Volume\n')

        print('\nNote: These controls are active when MPV is the focused window.\n')

    def play(self,media_list):
        try:
            if self.currentMediaType == "Music" or self.current_media == self.Radio:
                print(f"Playing: {media_list}")
                os.system(f'mpv --no-video {media_list}')
            else:
                print(f"Playing: {media_list}")
                if self.android and self.videoType == 'Movie':
                    os.system(f'am start -n is.xyz.mpv/is.xyz.mpv.MPVActivity -e filepath /storage/emulated/0/Jukebox/{media_list}')
                elif self.android and self.videoType == 'Video':
                    os.system(f'am start -n is.xyz.mpv/is.xyz.mpv.MPVActivity -e filepath {media_list}')
                else:
                    os.system(f'mpv {media_list}')
        except Exception as e:
            print(e)



    def search(self,query):

        #Case 1: Check if media is already in playlist directory. 
        media = self.search_db_directory(query)# if self.search_db_directory(query) != -1 else ''
        print("****",self.currentMediaType)
        if media:
            check_online = input(f"Found {media} in your local directory:\nWould you like to play this? (y/n)")
            print("You entered: ",check_online)
            if check_online == 'y':
                return media

        #Case 2: Search online for media
        media = -1
        if self.currentMediaType == 'Music':
            media = self.search_youtube(query)
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
                media = self.search_youtube(query)
            
            #default as youtube search for now
            else:
                media = self.search_youtube(query)


        return media

    #Helper for search for local media
    def search_db_directory(self, query):
        media = ""
        try:
            conn = sqlite3.connect('jukebox.db')
            cursor = conn.cursor()
            
            # Normalize the search query by replacing periods with spaces
            normalized_query = query.replace('.', ' ')
            
            # Determine the base path to search in based on the current media type
            base_path = self.music_path if self.currentMediaType == "Music" else self.movies_path
            
            # Use the normalized query for a case-insensitive search, restricted to the base path
            cursor.execute("""
                SELECT id, name, path, is_folder 
                FROM directories 
                WHERE REPLACE(name, '.', ' ') LIKE ? 
                AND path LIKE ? 
                ORDER BY name
                """, ('%' + normalized_query + '%', base_path + '%',))
            
            results = cursor.fetchall()
            paths = []
             # Check if any results are TV shows
            tv_shows = [result for result in results if "T.V. Shows" in result[2] and result[3]]

            if tv_shows:
                conn.close()
                return f'"{self.list_tv_show_seasons(tv_shows)}"'
            
            else:
                if results:
                    for result in results:
                        if not result[3]:  # If the result is a file, it's added to the list
                            paths.append(f'"{result[2]}"')  # Quote the path to handle spaces

            conn.close()
            
            # Join the sorted paths with spaces for MPV command
            media = ' '.join(sorted(paths))
            #Reset variables from youtube search
            self.from_youtube = False
            self.current_yt_song = ''
        except Exception as e:
            print("Add playlist audio/video directories to search locally")
            media = -1
        return media

    def list_tv_show_seasons(self, tv_shows):


        # Now, list seasons for the selected TV show
        conn = sqlite3.connect('jukebox.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, path, is_folder FROM directories WHERE parent_id = ? AND is_folder = 1 ORDER BY name", (tv_shows[0][0],))
        seasons = cursor.fetchall()
        conn.close()

        if seasons:
            print("Select a season:")
            for idx, season in enumerate(seasons, start=1):
                print(f"({idx}) {season[1]}")
            
            season_selection = input("Enter number to choose season: ")
            try:
                selected_season = seasons[int(season_selection)-1]
            except (ValueError, IndexError):
                print("Invalid selection.")
                return
            
            # Now you have the selected season, you can list the episodes or play the entire season
            return selected_season[2] # return path


    #Helper for search
    def search_youtube(self,input):
        #if not found in playlist directory, searches youtube
        audio = -1
        print(f'Searching for {input}')
        query_string = urllib.parse.urlencode({"search_query": input})
        formatUrl = urllib.request.urlopen("https://www.youtube.com/results?" + query_string)

        try:
            #for albums or playlists
            if self.checkForPlaylist:
                search_results = re.findall(r"list=([\w-]+)", formatUrl.read().decode())
                playlist_id = search_results[0]
                audio = "https://www.youtube.com/playlist?list=" + playlist_id
            #for single song
            else:
                search_results = re.findall(r"watch\?v=(\S{11})", formatUrl.read().decode())
                audio = self.current_yt_song = "https://www.youtube.com/watch?v=" + "{}".format(search_results[0])
            
            print(audio)
            
            

        except Exception as e:
            print(e)

        #Update variable
        self.from_youtube = True
        print("YOUTUBE SEARCH RETURNING: ", audio)
        return(audio)

    def download(self):
        '''gets current youtube song (current_yt_song) playing and downloads it to playlist directory as proper media type'''
        if self.currentMediaType == "Music":
            os.system(f'yt-dlp -x -f m4a -o "Music/%(title)s.%(ext)s" {self.current_yt_song}')
        else:
            os.system(f'yt-dlp -o "Movies/%(title)s.%(ext)s" {self.current_yt_song}')
        
        if self.currentMediaType == "Music":
            self.index_directory(self.music_path)
        else:
            self.index_directory(self.movies_path)
        print('Song saved in playlist')





if __name__ == "__main__":
    Jukebox = Jukebox()
    Jukebox.start()



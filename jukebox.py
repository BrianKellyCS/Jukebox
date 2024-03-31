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
        self.currentMediaType = "Music"   #will be either Music or Movie
        self.current_media = -1

        self.init_db()
        self.index_all()


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
            # After indexing, remove entries that were not seen
            #cursor.execute("SELECT path FROM directories")
            #all_paths = set(path for (path,) in cursor.fetchall())
            #missing_paths = all_paths - seen_paths
            #for missing_path in missing_paths:
                #cursor.execute("DELETE FROM directories WHERE path = ?", (missing_path,))
            
            conn.commit()
            conn.close()



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


    def search_db_directory(self, query):
        conn = sqlite3.connect('jukebox.db')
        cursor = conn.cursor()
        
        # Ensure results are ordered by name for a natural sorting
        cursor.execute("SELECT id, name, path, is_folder FROM directories WHERE name LIKE ? ORDER BY name", ('%' + query + '%',))
        
        results = cursor.fetchall()
        paths = []
        
        if results:
            for result in results:
                if not result[3]:  # If the result is a file, it's added to the list
                    paths.append(f'"{result[2]}"')  # Quote the path to handle spaces

        conn.close()
        
        # Join the sorted paths with spaces for MPV command
        return ' '.join(sorted(paths))


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
        self.welcome_screen()
        while query != 'q':
            self.current_media = -1
            query = input(self.colored_prompt()).lower()
            if query == 'help':
                self.menu()
            if query == 'r':
                self.current_media = self.Radio
            if query == 'u':
                self.update_username()
            elif ' -a' in query:
                self.currentMediaType = "Music"
                query = query[0:-3]
                print(query)
                self.current_media = self.search(query)
            elif ' -v' in query:
                self.currentMediaType = "Movie"
                query = query[0:-3]
                print(query)
                self.current_media = self.search(query)
            elif self.current_media == -1 and query != 'q' and query != 'help':
                print('Specify if you want audio/video by adding -a or -v after your query (type "help" for more info)')
                

            if self.current_media != -1:
                self.play(self.current_media)

                if self.current_media != self.Radio and self.from_youtube:
                    to_download = input('\n\nSave to directory? (y/n)')
                    if to_download == 'y':
                        self.download()
        
    def menu(self):
        print('\n\n\tCommand\t\tDesc.\t\t\tUseage\n')
        print('\tq\t\tQuit Jukebox\t\tq\n')
        print('\tu\t\tUpdate Username\t\tu\n')
        print('\tr\t\tRadio\t\t\tr\n')
        print('\t-a\t\tAudio\t\t\t{search query} -a\n')
        print('\t-v\t\tVideo\t\t\t{search query} -v\n')

        print('\n\tMPV Playback Controls:\n')
        print('\tSPACE\t\tPlay/Pause\n')
        print('\tq\t\tStop Playback & Quit MPV\n')
        print('\t>\t\tNext in Playlist\n')
        print('\t<\t\tPrevious in Playlist\n')
        print('\t←/→\t\tSeek Backwards/Forwards\n')
        print('\tm\t\tMute\n')
        print('\tf\t\tToggle Fullscreen\n')
        print('\t9/0\t\tDecrease/Increase Volumen')

        print('\nNote: These controls are active when MPV is the focused window.\n')


    def play(self,media_list):
        print(media_list)

        try:
            if self.currentMediaType == "Music":
                print(f"Playing: {media_list}")
                os.system(f'mpv --no-video {media_list}')
            else:
                print(f"Playing: {media_list}")
                os.system(f'mpv {media_list}')
        except Exception as e:
            print(e)


    def search(self,input):

        #Case 1: Check if media is already in playlist directory. 
        media = self.search_db_directory(input) if self.search_db_directory(input) != -1 else ''


        #Case 2: Search youtube for media
        if media == '':
            media = self.search_youtube(input)

        return media

    #Helper for search
    def search_directory(self,input):
        '''checks if the input (song or artist) is in playlist directory'''
        try:
            input = input.lower()
            input = input.split(' ')

            path = self.movies_path if self.currentMediaType == "Movie" else self.music_path
            print(path)
            list = os.listdir(path)
            media = "" #Initialize as -1 in case not found
            
            for song in list:
                print("LOOKING IN PATH")
                song = song.lower()
                temp_name = song #to avoid making changes to song names
                temp_name = temp_name.split('.') #Get rid of extension in name
                temp_name = temp_name[0] #searches for word in title
                temp_name = temp_name.split(' ')
                print('first song in list temp_name : ', temp_name)

                counter = 0
                for word_in_input in input:
                    for word_in_song_name in temp_name:
                        if word_in_input == word_in_song_name:
                            counter+=1
                if counter == len(input):
                    media+=(f'"{path}{song}" ')



            #Reset variables from youtube search
            self.from_youtube = False
            self.current_yt_song = ''
        except Exception as e:
            print("Add playlist audio/video directories to search locally")
            media = -1
        return media 

    #Helper for search
    def search_youtube(self,input):
        #if not found in playlist directory, searches youtube
        print(f'Searching for {input}')
        query_string = urllib.parse.urlencode({"search_query": input})
        formatUrl = urllib.request.urlopen("https://www.youtube.com/results?" + query_string)

        try:
            search_results = re.findall(r"watch\?v=(\S{11})", formatUrl.read().decode())
            audio = self.current_yt_song = "https://www.youtube.com/watch?v=" + "{}".format(search_results[0])

        except Exception as e:
            print(e)

        #Update variable
        self.from_youtube = True
        
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

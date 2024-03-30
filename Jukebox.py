import re,urllib.parse,urllib.request
import os
import colorama

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
        self.music_path = 'playlists/music/'
        self.video_path = 'playlists/videos/'
        self.Radio = 'https://media-ice.musicradio.com/Heart80s'
        self.from_youtube = False
        self.current_yt_song = ''
        self.currentMediaType = "audio"   #will be either audio or video
        self.current_media = -1

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
        print(Color.YELLOW + "Welcome to the Terminal Jukebox!" + Color.RESET)
        print(Color.GREEN + "Type 'help' to see the command list and to see MPV controls\n" + Color.RESET)


    def colored_prompt(self, user='user', at='@', jukebox='Jukebox', colon=':', tilde='~', greater_than='>', now_playing=''):

        prompt = f"{Color.RED}{user}{Color.RESET}" \
                f"{Color.GREEN}{at}{Color.RESET}" \
                f"{Color.YELLOW}{jukebox}{Color.RESET}" \
                f"{Color.BLUE}{colon}{Color.RESET}" \
                f"{Color.MAGENTA}{tilde}{Color.RESET}" \
                f"{Color.CYAN}{greater_than}{Color.RESET} "
        
        return prompt


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
            elif ' -a' in query:
                self.currentMediaType = "audio"
                query = query[0:-3]
                print(query)
                self.current_media = self.search(query)
            elif ' -v' in query:
                self.currentMediaType = "video"
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
        print('\n\n\tCommand\t\tDesc.\t\tUseage\n')
        print('\tq\t\tQuit Jukebox\tq\n')
        print('\tr\t\tRadio\t\tr\n')
        print('\t-a\t\tAudio\t\t{search query} -a\n')
        print('\t-v\t\tVideo\t\t{search query} -v\n')

        print('\n\tMPV Playback Controls:\n')
        print('\tSPACE\t\tPlay/Pause\tSpace\n')
        print('\tq\t\tStop Playback & Quit MPV\tq (while in MPV)\n')
        print('\t>\t\tNext in Playlist\tShift + .\n')
        print('\t<\t\tPrevious in Playlist\tShift + ,\n')
        print('\t←/→\t\tSeek Backwards/Forwards\tArrow Left / Arrow Right\n')
        print('\tm\t\tMute\t\tm\n')
        print('\tf\t\tToggle Fullscreen\tf\n')
        print('\t9/0\t\tDecrease/Increase Volume\t9 / 0\n')

        print('\nNote: These controls are active when MPV is the focused window.\n')


    def play(self,media_list):
        print(media_list)

        try:
            if self.currentMediaType == "audio":
                print(f"Playing: {media_list}")
                os.system(f'mpv --no-video {media_list}')
            else:
                print(f"Playing: {media_list}")
                os.system(f'mpv {media_list}')
        except Exception as e:
            print(e)


    def search(self,input):

        #Case 1: Check if media is already in playlist directory. 
        media = self.search_directory(input) if self.search_directory(input) != -1 else ''


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

            path = self.video_path if self.currentMediaType == "video" else self.music_path
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
        if self.currentMediaType == "audio":
            os.system(f'yt-dlp -x -f m4a -o "playlists/music/%(title)s.%(ext)s" {self.current_yt_song}')
        else:
            os.system(f'yt-dlp -o "playlists/videos/%(title)s.%(ext)s" {self.current_yt_song}')
        
        print('Song saved in playlist')





if __name__ == "__main__":
    Jukebox = Jukebox()
    Jukebox.start()
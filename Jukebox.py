
import re,urllib.parse,urllib.request
import os




class Jukebox(object):
    def __init__(self):
        self.music_path = 'playlists/music/'
        self.video_path = 'playlists/videos/'
        self.Radio = 'https://media-ice.musicradio.com/Heart80sMP3'
        self.from_youtube = False
        self.current_yt_song = ''
        self.audio = False
        self.video = False
        self.current_media = -1


        

    def start(self):
        query = ''

        while query != 'q':
            self.current_media = -1
            query = input("user@JukeBox:~> ").lower()
            if query == 'help':
                self.menu()
            if query == 'r':
                self.current_media = self.Radio
            elif ' -a' in query:
                self.audio = True
                self.video = False
                query = query[0:-3]
                print(query)
                self.current_media = self.search(query)
            elif ' -v' in query:
                self.video = True
                self.audio = False
                query = query[0:-3]
                print(query)
                self.current_media = self.search(query)
            elif self.current_media == -1 and query != 'q' and query != 'help':
                print('Specify if you want just audio/video by adding -a or -v after your query (type "help" for more info)')
                

            if self.current_media != -1:
                self.play(self.current_media)

                if self.current_media != self.Radio and self.from_youtube:
                    to_download = input('\n\nSave to directory? (y/n)')
                    if to_download == 'y':
                        self.download()
        
    def menu(self):
        print('\n\n\tCommand\t\tDesc.\t\tUseage\n')
        print('\tq\t\tQuit\t\tq\n')
        print('\tr\t\tRadio\t\tr\n')
        print('\t-a\t\tAudio\t\t{search query} -a\n')
        print('\t-v\t\tVideo\t\t{search query} -v\n')

    def play(self,media):
        try:
            if self.audio == True:
                os.system(f'mpv --no-video "{media}"')
            else:
                os.system(f'mpv "{media}"')
        except Exception as e:
            print(e)

    def search(self,input):

        #Case 1: Check if song is already in playlist directory. 
        song = self.search_directory(input) if self.search_directory(input) != -1 else ''


        #Case 2: Search youtube for song
        if song == '':
            song = self.search_youtube(input)

        return song

    #Helper for search
    def search_directory(self,input):
        '''checks if the input (song or artist) is in playlist directory'''
        
        input = input.lower()

        path = self.video_path if self.video == True else self.music_path
        list = os.listdir(path)
        media = -1 #Initialize as -1 in case not found
        
        for song in list:
            song = song.lower()
            temp_name = song #to avoid making changes to song names
            temp_name = temp_name.split('.') #Get rid of extension in name
            temp_name = temp_name[0]#.split(' ') #split name to search for word in title
            print('first temp_name : ', temp_name)

            if input in temp_name:
                print('iterating:', temp_name)
                media = f'{path}{song}'

        #Reset variables from youtube search
        self.from_youtube = False
        self.current_yt_song = ''
        
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
        '''gets current youtube song (current_yt_song) playing and downloads it to playlist directory'''
        os.system(f'yt-dlp -x -f m4a {self.current_yt_song}')
        
        print('Song saved in playlist')





if __name__ == "__main__":
    Jukebox = Jukebox()
    Jukebox.start()










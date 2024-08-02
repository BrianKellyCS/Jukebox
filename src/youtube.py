import re
import urllib.parse
import urllib.request
import threading
import subprocess

class YouTubeManager:
    def __init__(self, music_path, movies_path):
        self.music_path = music_path
        self.movies_path = movies_path

    def search_youtube(self, query, checkForPlaylist):
        # if not found in playlist directory, searches youtube
        print(f'Searching for {query}')
        query_string = urllib.parse.urlencode({"search_query": query})
        formatUrl = urllib.request.urlopen("https://www.youtube.com/results?" + query_string)

        try:
            # for albums or playlists
            if checkForPlaylist:
                search_results = re.findall(r"list=([\w-]+)", formatUrl.read().decode())
                playlist_id = search_results[0]
                audio = "https://www.youtube.com/playlist?list=" + playlist_id
            # for single song
            else:
                search_results = re.findall(r"watch\?v=(\S{11})", formatUrl.read().decode())
                audio = self.current_media = "https://www.youtube.com/watch?v=" + "{}".format(search_results[0])

            print(audio)

        except Exception as e:
            print(e)

        # Update jukebox's from_youtube variable
        from_youtube = True

        return from_youtube, audio

    def download(self, current_media, currentMediaType):
        '''gets current youtube song (current_yt_song) playing and downloads it to playlist directory as proper media type'''
        if currentMediaType == "Music":
            threading.Thread(target=self.download_song, args=(current_media,)).start()
        else:
            threading.Thread(target=self.download_video, args=(current_media,)).start()
        print('Download started in background')

    def download_song(self, current_media):
        print("SAVING IN", self.music_path)
        result = subprocess.run(
            ['yt-dlp', '-x', '-f', 'm4a', '-o', f'{self.music_path}/%(title)s.%(ext)s', current_media],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"Download of song completed: {current_media}")
        else:
            print(f"Error downloading song: {current_media}")
            print(result.stderr)

    def download_video(self, current_media):
        print("SAVING IN", self.movies_path)
        result = subprocess.run(
            ['yt-dlp', '-o', f'{self.movies_path}/%(title)s.%(ext)s', current_media],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"Download of video completed: {current_media}")
        else:
            print(f"Error downloading video: {current_media}")
            print(result.stderr)

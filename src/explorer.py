import os
from src.database import DatabaseManager

class MediaExplorer(DatabaseManager):
    def __init__(self, db_path, music_path, movies_path, playlists_path):
        # Initialize the DatabaseManager part of this class
        super().__init__(music_path, movies_path, playlists_path)

        self.music_path = music_path
        self.movies_path = movies_path
        self.playlists_path = playlists_path


    def is_android(self):
        '''termux on android plays videos differently'''
        if 'ANDROID_DATA' in os.environ:
            return True
        return False

    def explore(self, currentMediaType, current_media, videoType, Radio):
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
                        currentMediaType = "Video"
                    else:
                        currentMediaType = "Music"
                    _, start_path = media_options[choice_idx]
                    #print(self.currentMediaType)
                    self.navigate_directory(start_path, currentMediaType, current_media, videoType, Radio)
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def navigate_directory(self, current_path, currentMediaType, current_media, videoType, Radio):
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
                            self.play(f'"{selected_path}"', currentMediaType, videoType, Radio)
                    else:
                        print("Invalid selection.")
                except ValueError:
                    print("Please enter a valid number.")

    def play(self,current_media, currentMediaType, videoType, Radio):
        #print(current_mediaa)
        #print(current_media)
        try:
            if currentMediaType == "Music" or current_media == Radio:
                print(f"Playing: {current_media}")
                os.system(f'mpv --no-video {current_media}')
            else:
                print(f"Playing: {current_media}")
                if self.is_android() and videoType == 'Movie':
                    os.system(f'am start -n is.xyz.mpv/is.xyz.mpv.MPVActivity -e filepath /storage/emulated/0/Jukebox/{current_media}')
                else:
                    os.system(f'mpv {current_media}')
        except Exception as e:
            print(e)

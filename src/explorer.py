import os
import readchar
import threading
import subprocess
from rich.console import Console
from rich.table import Table
from rich.text import Text
from src.database import DatabaseManager

class MediaExplorer(DatabaseManager):
    def __init__(self, db_path, music_path, movies_path, playlists_path):
        super().__init__(music_path, movies_path, playlists_path)
        self.music_path = music_path
        self.movies_path = movies_path
        self.playlists_path = playlists_path
        self.console = Console()
        self.current_media_thread = None  # Track the current media thread
        self.current_media_process = None  # Track the current media process

    def is_android(self):
        '''termux on android plays videos differently'''
        return 'ANDROID_DATA' in os.environ

    def explore(self, currentMediaType, current_media, videoType, Radio):
        media_options = {
            1: ("Movies", self.movies_path),
            2: ("Music", self.music_path),
            3: ("Playlists", self.playlists_path)
        }

        while True:
            self.console.clear()
            self.console.print(Text("Select media type to explore:", style="bold cyan"))

            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Option", style="dim", width=6)
            table.add_column("Media Type", style="cyan")

            for key, (name, _) in media_options.items():
                table.add_row(f"({key})", name)
            table.add_row("(q)", "Quit")

            self.console.print(table)
            
            self.console.print(Text("Use the number keys to select a media type or 'q' to quit.", style="bold yellow"))
            
            choice = input("\nEnter your choice: ").strip().lower()

            if choice == 'q':
                break

            try:
                choice_idx = int(choice)
                if choice_idx in media_options:
                    currentMediaType = "Video" if choice_idx == 1 else "Music"
                    _, start_path = media_options[choice_idx]
                    self.navigate_directory(start_path, currentMediaType, current_media, videoType, Radio)
                else:
                    self.console.print("Invalid selection. Please try again.", style="bold red")
            except ValueError:
                self.console.print("Invalid input. Please enter a number.", style="bold red")

    def navigate_directory(self, current_path, currentMediaType, current_media, videoType, Radio):
        history_stack = []
        index = 0
        page_size = 10

        while True:
            self.console.clear()
            self.console.print(Text(f"Exploring: {current_path}", style="bold cyan"))

            dirs_and_files = sorted(os.listdir(current_path), key=lambda x: (not os.path.isdir(os.path.join(current_path, x)), x.lower()))
            total_items = len(dirs_and_files)
            page_start = index * page_size
            page_end = min(page_start + page_size, total_items)

            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Index", style="dim", width=6)
            table.add_column("Type", style="cyan", width=6)
            table.add_column("Name", style="cyan")

            for idx, entry in enumerate(dirs_and_files[page_start:page_end], start=page_start + 1):
                entry_path = os.path.join(current_path, entry)
                table.add_row(f"({idx})", "[D]" if os.path.isdir(entry_path) else "[F]", entry)

            self.console.print(table)

            if page_start > 0:
                self.console.print(Text("(↑) Scroll Up", style="bold magenta"))
            if page_end < total_items:
                self.console.print(Text("(↓) Scroll Down", style="bold magenta"))
            self.console.print(Text("(0) Go Back", style="bold magenta"))
            self.console.print(Text("Enter the number for selection and press enter to explore or play the selection", style="bold yellow"))

            input_buffer = ""

            while True:
                key = readchar.readkey()
                if key == readchar.key.UP and page_start > 0:
                    index -= 1
                    break
                elif key == readchar.key.DOWN and page_end < total_items:
                    index += 1
                    break
                elif key == readchar.key.ENTER:
                    break
                elif key.isdigit() or key in ('q', '0'):
                    input_buffer += key
                    self.console.print(Text(input_buffer, style="bold green"), end="\r")
                elif key == readchar.key.BACKSPACE and input_buffer:
                    input_buffer = input_buffer[:-1]
                    self.console.print(Text(input_buffer + ' ', style="bold green"), end="\r")
            
            self.console.clear()
            
            if input_buffer:
                choice = input_buffer.strip().lower()
            else:
                continue

            if choice == 'q':
                break
            elif choice == '0':
                if history_stack:
                    current_path = history_stack.pop()
                else:
                    self.console.print("No more parent directories.", style="bold red")
                    break
            else:
                try:
                    choice_idx = int(choice) - 1
                    if 0 <= choice_idx < total_items:
                        selected_path = os.path.join(current_path, dirs_and_files[choice_idx])
                        if os.path.isdir(selected_path):
                            history_stack.append(current_path)
                            current_path = selected_path
                            index = 0
                        else:
                            self.console.print(f"Selected File: {selected_path}", style="bold green")
                            self.play(selected_path, currentMediaType, videoType, Radio)
                    else:
                        self.console.print("Invalid selection.", style="bold red")
                except ValueError:
                    self.console.print("Please enter a valid number.", style="bold red")
            input_buffer = ""

    def play(self, current_media, currentMediaType, videoType, Radio):
        # Stop any currently running media thread
        self.stop_current_media()

        def run_player():
            try:
                if currentMediaType == "Music" or current_media == Radio:
                    self.console.print(f"Playing: {current_media}", style="bold green")
                    self.current_media_process = subprocess.Popen(
                        ['mpv', '--no-video', '--really-quiet', current_media],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                else:
                    self.console.print(f"Playing: {current_media}", style="bold green")
                    if self.is_android() and videoType == 'Movie':
                        self.current_media_process = subprocess.Popen(
                            ['am', 'start', '-n', 'is.xyz.mpv/is.xyz.mpv.MPVActivity', '-e', 'filepath', f'/storage/emulated/0/Jukebox/{current_media}'],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                    else:
                        self.current_media_process = subprocess.Popen(
                            ['mpv', '--really-quiet', current_media],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                self.current_media_process.wait()
            except Exception as e:
                self.console.print(f"Error: {e}", style="bold red")

        self.current_media_thread = threading.Thread(target=run_player)
        self.current_media_thread.start()

    def stop_current_media(self):
        if self.current_media_process and self.current_media_process.poll() is None:
            self.current_media_process.terminate()
            self.current_media_thread.join()
            self.current_media_thread = None
            self.current_media_process = None

from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.panel import Panel

console = Console()

def colored_prompt(user_name):
    prompt = (Text(user_name, style="bold red")
              + Text("@", style="bold green")
              + Text("Jukebox", style="bold yellow")
              + Text(":", style="bold blue")
              + Text("~", style="bold magenta")
              + Text(">", style="bold cyan") + " ")
    return prompt

def welcome_screen(user_name):
    ascii_art = r"""
   ___       _        _               
  |_  |     | |      | |              
    | |_   _| | _____| |__   _____  __
    | | | | | |/ / _ \ '_ \ / _ \ \/ /
/\__/ / |_| |   <  __/ |_) | (_) >  < 
\____/ \__,_|_|\_\___|_.__/ \___/_/\_\                 
    """
    console.print(Text(ascii_art, style="bold cyan"))
    welcome_back_message = f"Welcome back, {user_name}!" if user_name != 'user' else "Welcome to the Terminal Jukebox!"
    console.print(Text(welcome_back_message, style="bold yellow"))
    console.print(Text("Type 'help' to see the command list and MPV controls", style="bold green"))
    console.print("\n")

def menu():
    console.print("\n")
    console.print(Panel(Text("Command List", justify="center"), style="bold magenta", expand=False))

    table = Table(show_header=True, header_style="bold magenta", style="bold blue")
    table.add_column("Command", style="bold cyan")
    table.add_column("Description", style="bold yellow")
    table.add_column("Usage", style="bold green")

    commands = [
        ("e", "Explore Directories", "e"),
        ("s", "Re-scan Directories", "s"),
        ("q", "Quit Jukebox", "q"),
        ("u", "Update Username", "u"),
        ("r", "Radio", "r"),
        ("-a", "Audio", "{search query} -a"),
        ("-a -p", "Audio with Playlist", "{search query} -a -p"),
        ("-v", "Video (search on YouTube by default)", "{search query} -v"),
        ("-v -p", "Video with Playlist", "{search query} -v -p"),
        ("-v -yt", "Specify YouTube Video", "{search query} -v -yt"),
        ("-v -m", "Search for Movie (mov-cli)", "{search query} -v -m"),
        ("-v -m -d", "Search & Download Movie (mov-cli)", "{search query} -v -m -d"),
        ("YouTube Link", "Download from YouTube", "Paste a YouTube link directly to download video.\nAdd \"-a\" after the link to download audio only.\nVideos are saved to the Movies directory;\naudio files are saved to the Music directory.")
    ]
    
    for command, desc, usage in commands:
        table.add_row(command, desc, usage)

    console.print(table)

    console.print(Panel(Text("MPV Playback Controls", justify="center"), style="bold magenta", expand=False))

    control_table = Table(show_header=False, style="bold blue")
    control_table.add_column("Control", style="bold cyan")
    control_table.add_column("Function", style="bold yellow")

    controls = [
        ("SPACE", "Play/Pause"),
        ("q", "Stop Playback & Quit MPV"),
        (">", "Next in Playlist"),
        ("<", "Previous in Playlist"),
        ("←/→", "Seek Backwards/Forwards"),
        ("m", "Mute"),
        ("f", "Toggle Fullscreen"),
        ("9/0", "Decrease/Increase Volume")
    ]
    
    for control, function in controls:
        control_table.add_row(control, function)

    console.print(control_table)

    console.print("\n[bold magenta]Note:[/bold magenta] These controls are active when MPV is the focused window.\n")


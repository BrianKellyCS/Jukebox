import colorama

# Initialize colorama to enhance cross-platform compatibility of colored output
colorama.init(autoreset=True)

def colored_prompt(user_name):
    prompt = (f"{colorama.Fore.LIGHTRED_EX}{user_name}{colorama.Style.RESET_ALL}"
              f"{colorama.Fore.LIGHTGREEN_EX}@{colorama.Style.RESET_ALL}"
              f"{colorama.Fore.LIGHTYELLOW_EX}Jukebox{colorama.Style.RESET_ALL}"
              f"{colorama.Fore.LIGHTBLUE_EX}:{colorama.Style.RESET_ALL}"
              f"{colorama.Fore.LIGHTMAGENTA_EX}~{colorama.Style.RESET_ALL}"
              f"{colorama.Fore.LIGHTCYAN_EX}>{colorama.Style.RESET_ALL} ")
    return prompt




def welcome_screen(user_name):
    ascii_art = """
   ___       _        _               
  |_  |     | |      | |              
    | |_   _| | _____| |__   _____  __
    | | | | | |/ / _ \ '_ \ / _ \ \/ /
/\__/ / |_| |   <  __/ |_) | (_) >  < 
\____/ \__,_|_|\_\___|_.__/ \___/_/\_\                 
    """
    print(f"{colorama.Fore.LIGHTCYAN_EX}{ascii_art}{colorama.Style.RESET_ALL}")
    welcome_back_message = f"Welcome back, {user_name}!" if user_name != 'user' else "Welcome to the Terminal Jukebox!"
    print(f"{colorama.Fore.LIGHTYELLOW_EX}{welcome_back_message}{colorama.Style.RESET_ALL}")
    print(f"{colorama.Fore.LIGHTGREEN_EX}Type 'help' to see the command list and MPV controls{colorama.Style.RESET_ALL}\n")


def menu():
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
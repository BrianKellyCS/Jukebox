import subprocess
import sys

def install(packages):
    import importlib
    for package in packages:
        try:
            importlib.import_module(package)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
install(['rich', 'readchar', 'yt-dlp'])
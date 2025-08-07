import sqlite3
import os

class ConfigManager:
    def __init__(self, db_path='jukebox.db'):
        self.db_path = db_path
        self.auto_create_dirs = True
        self.init_config_table()
        self.config = self.load_config()
        self.validate_directories()

    def init_config_table(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        ''')
        default_config = {
            'user_name': 'user',
            'music_path': 'Music/',
            'movies_path': 'Movies/',
            'playlists_path': 'Playlists/'
        }
        for key, value in default_config.items():
            cursor.execute('INSERT OR IGNORE INTO config (key, value) VALUES (?, ?)', (key, value))
        conn.commit()
        conn.close()

    def load_config(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT key, value FROM config')
        config = {row[0]: row[1] for row in cursor.fetchall()}
        conn.close()
        return config

    def save_config(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        for key, value in self.config.items():
            cursor.execute('REPLACE INTO config (key, value) VALUES (?, ?)', (key, value))
        conn.commit()
        conn.close()
        print("Configuration saved.")

    def validate_directories(self):
        directory_keys = ['music_path', 'movies_path', 'playlists_path']
        for key in directory_keys:
            path = self.config.get(key, '')
            if not os.path.exists(path):
                if self.auto_create_dirs:
                    os.makedirs(path, exist_ok=True)
                    print(f"Created default directory for {key.replace('_', ' ')} at: {path}")
                else:
                    print(f"The {key.replace('_', ' ')} directory does not exist: {path}")
                    self.update_directory(key)

    def update_username(self, current_user_name):
        new_user_name = input("Enter your new user name: ").strip()
        if new_user_name:  # Check if the user actually entered something
            self.config['user_name'] = new_user_name
            self.save_config()  # Save the updated configuration
            print(f"Username updated to {new_user_name}.")
            return new_user_name
        else:
            print("Username update cancelled.")
            return current_user_name

    def update_directory(self, directory_key):
        while True:
            new_path = input(f"Enter the new path for {directory_key.replace('_', ' ')}: ").strip()
            if new_path:
                if os.path.exists(new_path):
                    self.config[directory_key] = new_path
                    self.save_config()
                    print(f"{directory_key.replace('_', ' ')} updated to {new_path}.")
                    break
                else:
                    print(f"The specified path does not exist. Please enter a valid path.")
            else:
                print(f"{directory_key.replace('_', ' ')} update cancelled.")
                break

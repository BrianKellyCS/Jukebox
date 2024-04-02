import sqlite3
import os

class DatabaseManager:
    def __init__(self, music_path, movies_path, playlists_path, db_path='jukebox.db'):
        self.db_path = db_path
        self.music_path = music_path
        self.movies_path = movies_path
        self.playlists_path = playlists_path
        
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

    def search_db_directory(self, query, currentMediaType):
        media = ""
        try:
            conn = sqlite3.connect('jukebox.db')
            cursor = conn.cursor()
            
            # Normalize the search query by replacing periods with spaces
            normalized_query = query.replace('.', ' ')
            
            # Determine the base path to search in based on the current media type
            base_path = self.music_path if currentMediaType == "Music" else self.movies_path
            
            # Use the normalized query for a case-insensitive search, restricted to the base path
            cursor.execute("""
                SELECT id, name, path, is_folder 
                FROM directories 
                WHERE REPLACE(name, '.', ' ') LIKE ? 
                AND path LIKE ? 
                ORDER BY name
                """, ('%' + normalized_query + '%', base_path + '%',))
            
            results = cursor.fetchall()
            paths = []
             # Check if any results are TV shows
            tv_shows = [result for result in results if "T.V. Shows" in result[2] and result[3]]

            if tv_shows:
                conn.close()
                return f'"{self.list_tv_show_seasons(tv_shows)}"'
            
            else:
                if results:
                    for result in results:
                        if not result[3]:  # If the result is a file, it's added to the list
                            paths.append(f'"{result[2]}"')  # Quote the path to handle spaces

            conn.close()
            
            # Join the sorted paths with spaces for MPV command
            media = ' '.join(sorted(paths))
            #Reset variables from youtube search
            self.from_youtube = False

        except Exception as e:
            print("Add playlist audio/video directories to search locally")
            media = -1
        return media
    
    def list_tv_show_seasons(self, tv_shows):


        # Now, list seasons for the selected TV show
        conn = sqlite3.connect('jukebox.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, path, is_folder FROM directories WHERE parent_id = ? AND is_folder = 1 ORDER BY name", (tv_shows[0][0],))
        seasons = cursor.fetchall()
        conn.close()

        if seasons:
            print("Select a season:")
            for idx, season in enumerate(seasons, start=1):
                print(f"({idx}) {season[1]}")
            
            season_selection = input("Enter number to choose season: ")
            try:
                selected_season = seasons[int(season_selection)-1]
            except (ValueError, IndexError):
                print("Invalid selection.")
                return
            
            # Now you have the selected season, you can list the episodes or play the entire season
            return selected_season[2] # return path
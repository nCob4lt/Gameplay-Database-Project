"""

File: database.py

Description: Contains a collection of methods which allows the application to interact with the database

This module handles all interactions with the SQLite database for the Gameplay Database bot.
It provides:

- Initialization of tables (official + request tables)
- Registration functions for creators, layouts, collabs, music, and artists
- Retrieval functions for single or multiple records
- Database synchronization functions to keep IDs and counts updated
- An asynchronous worker for queued database operations with locking

Author: cobalt

"""

# --- Standard imports ---
import sqlite3
from datetime import datetime
import asyncio
import json

from pathlib import Path

# --- Local imports ---
from utilities import tools
from utilities.applogger import AppLogger
from exceptions.custom_exceptions import DataNotFound

# --- Async database queue and lock ---
database_queue = asyncio.Queue()
database_lock = asyncio.Lock()

# --- Application logger ---
applogger = AppLogger()

async def database_worker():

    """

    Background worker for executing database operations asynchronously.

    Pulls tasks from the `database_queue` and executes them in a thread-safe
    manner using `database_lock` to prevent concurrent writes.

    Each task is a tuple of (function, args, kwargs). Supports both
    coroutine functions and regular functions.

    """

    while True:
        function, args, kwargs = await database_queue.get()
        try:
            async with database_lock:
                if asyncio.iscoroutinefunction(function):
                    await function(*args, **kwargs)
                else:
                    function(*args, **kwargs)
        except Exception as e:
            applogger.error(f"Database error : {e}")
        finally:
            database_queue.task_done()


# --- Database connection ---
connection = sqlite3.connect("data/gpdb.db")
connection.row_factory = sqlite3.Row
cursor = connection.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

# -------------------- DATABASE INITIALIZATION --------------------

def initialize():

    """

    Initializes the database by creating all required tables if they do not exist.

    Includes both official tables (creator, layout, collab, music, artist) and
    request tables (requestcreator, requestlayout, requestcollab, requestmusic, requestartist).

    """

    # --- Official tables ---
    cursor.execute(''' CREATE TABLE IF NOT EXISTS creator (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   username TEXT NOT NULL,
                   nationality TEXT,
                   discord TEXT UNIQUE,
                   discord_uid TEXT UNIQUE,
                   yt TEXT,
                   layouts_registered INTEGER DEFAULT 0,
                   collab_participations INTEGER DEFAULT 0,
                   total_time_built INTEGER DEFAULT 0,
                   registration_date TEXT,
                   recorder_name TEXT); ''')
    
    cursor.execute(''' CREATE TABLE IF NOT EXISTS layout (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   creator_id INTEGER,
                   creator_name TEXT,
                   type TEXT,
                   name TEXT NOT NULL,
                   length TEXT,
                   yt TEXT,
                   music_id INTEGER,
                   music_ngid INTEGER,
                   music_name TEXT,
                   music_artist TEXT,
                   igid INTEGER,
                   registration_date TEXT,
                   recorder_name TEXT,
                   recorder_notes TEXT,
                   artist_id INTEGER,
                   masterlevel TEXT DEFAULT NULL,                             
                   FOREIGN KEY (creator_id) REFERENCES creator(id),
                   FOREIGN KEY (artist_id) REFERENCES artist(id),
                   FOREIGN KEY (music_id) REFERENCES music(id));''')
    
    cursor.execute(''' CREATE TABLE IF NOT EXISTS collab (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   host_id INTEGER,
                   host_name TEXT,
                   name TEXT,
                   builders_number TEXT,
                   length TEXT,
                   yt TEXT,
                   music_id INTEGER,
                   music_ngid INTEGER,
                   music_name TEXT,
                   music_artist TEXT,
                   igid INTEGER,
                   registration_date TEXT,
                   recorder_name TEXT,
                   recorder_notes TEXT,
                   artist_id INTEGER,
                   FOREIGN KEY (host_id) REFERENCES creator(id),
                   FOREIGN KEY (artist_id) REFERENCES artist(id),
                   FOREIGN KEY (music_id) REFERENCES music(id));''')
    
    cursor.execute(''' CREATE TABLE IF NOT EXISTS music (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT NOT NULL,
                   artist TEXT,
                   length TEXT,
                   type TEXT,
                   yt TEXT,
                   soundcloud TEXT,
                   uses INTEGER DEFAULT 0,
                   ngid INTEGER,
                   registration_date TEXT,
                   recorder_name TEXT,
                   recorder_notes TEXT,
                   artist_id INTEGER,
                   FOREIGN KEY (artist_id) REFERENCES artist(id));''')
    
    cursor.execute(''' CREATE TABLE IF NOT EXISTS artist (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT NOT NULL UNIQUE,
                   yt TEXT,
                   soundcloud TEXT,
                   songs_registered INTEGER DEFAULT 0,
                   total_song_uses INTEGER DEFAULT 0,
                   registration_date TEXT,
                   recorder_name TEXT,
                   recorder_notes TEXT)''')
    
    # REQUESTS TABLES

    cursor.execute(''' CREATE TABLE IF NOT EXISTS requestcreator (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   username TEXT NOT NULL,
                   nationality TEXT,
                   discord TEXT UNIQUE,
                   discord_uid TEXT UNIQUE,
                   yt TEXT,
                   registration_date TEXT,
                   recorder_name TEXT);''')
    
    cursor.execute(''' CREATE TABLE IF NOT EXISTS requestlayout (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   creator_name TEXT,
                   type TEXT,
                   name TEXT NOT NULL,
                   length TEXT,
                   yt TEXT,            
                   music_ngid INTEGER,
                   music_name TEXT,
                   music_artist TEXT,
                   igid INTEGER,
                   registration_date TEXT,
                   recorder_name TEXT,
                   recorder_notes TEXT,
                   masterlevel TEXT DEFAULT NULL);''')
    
    cursor.execute(''' CREATE TABLE IF NOT EXISTS requestcollab (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   host_name TEXT,
                   name TEXT,
                   builders_number TEXT,
                   length TEXT,
                   yt TEXT,
                   music_ngid INTEGER,
                   music_name TEXT,
                   music_artist TEXT,
                   igid INTEGER,
                   registration_date TEXT,
                   recorder_name TEXT,
                   recorder_notes TEXT);''')
    
    cursor.execute(''' CREATE TABLE IF NOT EXISTS requestmusic (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT NOT NULL,
                   artist TEXT,
                   length TEXT,
                   type TEXT,
                   yt TEXT,
                   soundcloud TEXT,
                   ngid INTEGER,
                   registration_date TEXT,
                   recorder_name TEXT,
                   recorder_notes TEXT);''')
    
    cursor.execute(''' CREATE TABLE IF NOT EXISTS requestartist (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT NOT NULL UNIQUE,
                   yt TEXT,
                   soundcloud TEXT,
                   registration_date TEXT,
                   recorder_name TEXT,
                   recorder_notes TEXT)''')
    
    connection.commit()

def clear():

    """

    Drops all official tables and resets the SQLite autoincrement sequence.

    This is useful for resetting the database during development or testing.
    Foreign key checks are temporarily disabled during the drop operation.

    """

    cursor.execute("PRAGMA foreign_keys = OFF;")
    
    cursor.execute("DROP TABLE IF EXISTS creator;")
    cursor.execute("DROP TABLE IF EXISTS layout;")
    cursor.execute("DROP TABLE IF EXISTS collab;")
    cursor.execute("DROP TABLE IF EXISTS music;")
    cursor.execute("DROP TABLE IF EXISTS artist;")
    cursor.execute("DROP TABLE IF EXISTS requestcreator")
    cursor.execute("DROP TABLE IF EXISTS requestlayout")
    cursor.execute("DROP TABLE IF EXISTS requestcollab")
    cursor.execute("DROP TABLE IF EXISTS requestmusic")
    cursor.execute("DROP TABLE IF EXISTS requestartist")

    cursor.execute("DELETE FROM sqlite_sequence;")

    connection.commit()
    cursor.execute("PRAGMA foreign_keys = ON;")

# -------------------- REGISTRATION FUNCTIONS --------------------
   
def register_creator(username, nationality, discord_uname, discord_uid, yt, registrator):

    """

    Registers a new creator in the database.

    Parameters
    ----------
    username : str
        Name of the creator.
    nationality : str
        Nationality of the creator.
    discord_uname : str
        Discord username of the creator.
    discord_uid : str
        Discord user ID.
    yt : str
        YouTube link.
    registrator : str
        Name of the person recording the entry.

    """

    dt = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute(''' INSERT INTO creator (username,
                    nationality,
                    discord,
                    discord_uid,
                    yt,
                    registration_date,
                    recorder_name) VALUES (?,?,?,?,?,?,?);''',
                    (username, nationality, discord_uname, discord_uid, yt, dt, registrator))
    
    connection.commit()

# --- Similarly, other registration functions (register_layout, register_collab, etc.) follow
# Each function inserts a record into its respective table and commits the transaction.

def register_layout(creator, name, length, yt, music_name, music_artist, music_ngid, type, igid, masterlevel, recorder_notes, registrator):

    dt = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute(''' INSERT INTO layout (creator_name,
                   type,
                   name,
                   length,
                   yt,
                   music_ngid,
                   music_name,
                   music_artist,
                   igid,
                   registration_date,
                   recorder_name,
                   recorder_notes,
                   masterlevel
                   ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?);''',
                   (creator, type, name, length, yt, music_ngid, music_name, music_artist, igid, dt, registrator, recorder_notes, masterlevel))
    
    connection.commit()


def register_collab(hostname, name, builders_number, length, yt, music_name, music_artist, music_ngid, igid, recorder_name, recorder_notes):

    dt = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute(''' INSERT INTO collab (host_name,
                   name,
                   builders_number,
                   length,
                   yt,
                   music_ngid,
                   music_name,
                   music_artist,
                   igid,
                   registration_date,
                   recorder_name,
                   recorder_notes
                   ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?);''',
                   (hostname, name, builders_number, length, yt, music_ngid, music_name, music_artist, igid, dt, recorder_name, recorder_notes))
    
    connection.commit()


def register_music(name, artist, length, type_, yt, soundcloud, ngid, registrator, recorder_notes):

    dt = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute('''INSERT INTO music (
                        name,
                        artist,
                        length,
                        type,
                        yt,
                        soundcloud,
                        ngid,
                        registration_date,
                        recorder_name,
                        recorder_notes
                      ) VALUES (?,?,?,?,?,?,?,?,?,?);''',
                   (name, artist, length, type_, yt, soundcloud, ngid, dt, registrator, recorder_notes))
    
    connection.commit()


def register_artist(name, yt, soundcloud, registrator, recorder_notes):

    dt = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute('''INSERT INTO artist (
                        name,
                        yt,
                        soundcloud,
                        registration_date,
                        recorder_name,
                        recorder_notes
                      ) VALUES (?,?,?,?,?,?);''',
                   (name, yt, soundcloud, dt, registrator, recorder_notes))
    
    connection.commit()

def register_request_creator(username, nationality, discord_uname, discord_uid, yt, registrator):

    dt = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute('''INSERT INTO requestcreator (
                        username,
                        nationality,
                        discord,
                        discord_uid,
                        yt,
                        registration_date,
                        recorder_name
                      ) VALUES (?,?,?,?,?,?,?);''',
                   (username, nationality, discord_uname, discord_uid, yt, dt, registrator))
    
    connection.commit()


def register_request_layout(creator_name, type_, name, length, yt, music_ngid, music_name, music_artist, igid, masterlevel, recorder_notes, registrator):
    
    dt = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute('''INSERT INTO requestlayout (
                        creator_name,
                        type,
                        name,
                        length,
                        yt,
                        music_ngid,
                        music_name,
                        music_artist,
                        igid,
                        registration_date,
                        recorder_name,
                        recorder_notes,
                        masterlevel
                      ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?);''',
                   (creator_name, type_, name, length, yt, music_ngid, music_name, music_artist, igid, dt, registrator, recorder_notes, masterlevel))
    
    connection.commit()


def register_request_collab(host_name, name, builders_number, length, yt, music_ngid, music_name, music_artist, igid, recorder_notes, registrator):

    dt = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute('''INSERT INTO requestcollab (
                        host_name,
                        name,
                        builders_number,
                        length,
                        yt,
                        music_ngid,
                        music_name,
                        music_artist,
                        igid,
                        registration_date,
                        recorder_name,
                        recorder_notes
                      ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?);''',
                   (host_name, name, builders_number, length, yt, music_ngid, music_name, music_artist, igid, dt, registrator, recorder_notes))
    
    connection.commit()


def register_request_music(name, artist, length, type_, yt, soundcloud, ngid, recorder_notes, registrator):

    dt = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute('''INSERT INTO requestmusic (
                        name,
                        artist,
                        length,
                        type,
                        yt,
                        soundcloud,
                        ngid,
                        registration_date,
                        recorder_name,
                        recorder_notes
                      ) VALUES (?,?,?,?,?,?,?,?,?,?);''',
                   (name, artist, length, type_, yt, soundcloud, ngid, dt, registrator, recorder_notes))
    
    connection.commit()


def register_request_artist(name, yt, soundcloud, recorder_notes, registrator):

    dt = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute('''INSERT INTO requestartist (
                        name,
                        yt,
                        soundcloud,
                        registration_date,
                        recorder_name,
                        recorder_notes
                      ) VALUES (?,?,?,?,?,?);''',
                   (name, yt, soundcloud, dt, registrator, recorder_notes))
    
    connection.commit()

# -------------------- RETRIEVAL FUNCTIONS --------------------

def get_creator_by_name(username):

    """

    Retrieves a creator by username.

    Raises
    ------
    DataNotFound
        If no creator exists with the given username.

    """

    cursor.execute('''SELECT * FROM creator WHERE username = ?;''', (username,))
    result = cursor.fetchall()
    if not result:
        raise DataNotFound(f"No creator found with username '{username}'")
    return result

# --- Similarly, get_layout_by_name, get_collab_by_name, get_music_by_name, get_artist_by_name ---
# All raise DataNotFound if no result is found.

def get_layout_by_name(layout_name):
    cursor.execute('''SELECT * FROM layout WHERE name = ?;''', (layout_name,))
    result = cursor.fetchall()
    if not result:
        raise DataNotFound(f"No layout found with name '{layout_name}'")
    return result


def get_collab_by_name(collab_name):
    cursor.execute('''SELECT * FROM collab WHERE name = ?;''', (collab_name,))
    result = cursor.fetchall()
    if not result:
        raise DataNotFound(f"No collab found with name '{collab_name}'")
    return result


def get_music_by_name(music_name):
    cursor.execute('''SELECT * FROM music WHERE name = ?;''', (music_name,))
    result = cursor.fetchall()
    if not result:
        raise DataNotFound(f"No music found with name '{music_name}'")
    return result


def get_artist_by_name(artist_name):
    cursor.execute('''SELECT * FROM artist WHERE name = ?;''', (artist_name,))
    result = cursor.fetchall()
    if not result:
        raise DataNotFound(f"No artist found with name '{artist_name}'")
    return result

def get_layouts_from(creator):
    cursor.execute(''' SELECT name, yt FROM layout WHERE creator_name = ?;''', (creator,))
    result = cursor.fetchall()
    if not result:
        raise DataNotFound(f"No levels from '{creator}'")
    return result

def get_collabs_from(creator):
    cursor.execute(''' SELECT name, yt FROM collab WHERE host_name = ?;''', (creator,))
    result = cursor.fetchall()
    if not result:
        raise DataNotFound(f"No collabs from '{creator}'")
    return result

def get_levels_from(creator):
    cursor.execute('''
        SELECT name, yt, 'layout' AS type FROM layout WHERE creator_name = ?
        UNION ALL
        SELECT name, yt, 'collab' AS type FROM collab WHERE host_name = ?;
    ''', (creator, creator))
    result = cursor.fetchall()
    if not result:
        raise DataNotFound(f"No levels from '{creator}'")
    return result

def get_musics_from(artist):
    cursor.execute(''' SELECT name, yt, soundcloud FROM music WHERE artist = ?''', (artist,))
    result = cursor.fetchall()
    if not result:
        raise DataNotFound(f"No musics from '{artist}'")
    return result

def get_layouts_with_music(music):
    cursor.execute(''' SELECT name, yt, creator_name FROM layout WHERE music_name = ?''', (music,))
    result = cursor.fetchall()
    if not result:
        raise DataNotFound(f"No layouts with following song : {music}")
    return result

def get_layouts_with_artist(artist):
    cursor.execute(''' SELECT name, yt, creator_name FROM layout WHERE music_artist = ?''', (artist,))
    result = cursor.fetchall()
    if not result:
        raise DataNotFound(f"No layouts with song from following artist : {artist}")
    return result

def get_collabs_with_music(music):
    cursor.execute(''' SELECT name, yt, host_name FROM collab WHERE music_name = ?''', (music,))
    result = cursor.fetchall()
    if not result:
        raise DataNotFound(f"No collabs with following song : {music}")
    return result

def get_collabs_with_artist(artist):
    cursor.execute(''' SELECT name, yt, host_name FROM collab WHERE music_artist = ?''', (artist,))
    result = cursor.fetchall()
    if not result:
        raise DataNotFound(f"No collabs with song from following artist : {artist}")
    return result

def get_levels_with_music(music):
    """
    Retrieves all levels (layouts + collabs) that use a given music.

    Parameters
    ----------
    music : str
        The name of the music to search for.

    Returns
    -------
    list[tuple]
        List of (name, yt) pairs for all layouts and collabs using the given music.

    Raises
    ------
    DataNotFound
        If no level uses the specified music.
    """
    cursor.execute(
        '''
        SELECT name, yt, creator_name FROM layout WHERE music_name = ?
        UNION ALL
        SELECT name, yt, host_name FROM collab WHERE music_name = ?;
        ''',
        (music, music)
    )
    result = cursor.fetchall()
    if not result:
        raise DataNotFound(f"No levels with following song: {music}")
    return result


def get_levels_with_artist(artist):
    """
    Retrieves all levels (layouts + collabs) that use a song from a given artist.

    Parameters
    ----------
    artist : str
        The name of the artist to search for.

    Returns
    -------
    list[tuple]
        List of (name, yt) pairs for all layouts and collabs using a song from the given artist.

    Raises
    ------
    DataNotFound
        If no level uses a song from the specified artist.
    """
    cursor.execute(
        '''
        SELECT name, yt, creator_name FROM layout WHERE music_artist = ?
        UNION ALL
        SELECT name, yt, host_name FROM collab WHERE music_artist = ?;
        ''',
        (artist, artist)
    )
    result = cursor.fetchall()
    if not result:
        raise DataNotFound(f"No levels with songs from following artist: {artist}")
    return result

def get_parts_from(creator_name):
    """
    Retrieves all collaboration parts (layouts) built by a specific creator.

    A "part" is defined as a layout entry that belongs to a collaboration,
    i.e., where the 'masterlevel' field is NOT NULL.

    Parameters
    ----------
    creator_name : str
        The name of the creator to search for.

    Returns
    -------
    list[dict]
        List of layouts representing the creator's parts in collaborations.
        Each entry includes:
            - name (str): The layout's name
            - yt (str): YouTube link
            - masterlevel (str): The main collaboration name

    Raises
    ------
    DataNotFound
        If the creator has no recorded parts in collaborations.
    """
    cursor.execute(
        '''
        SELECT name, yt, masterlevel
        FROM layout
        WHERE creator_name = ? AND masterlevel IS NOT NULL;
        ''',
        (creator_name,)
    )
    result = cursor.fetchall()

    if not result:
        raise DataNotFound(f"No collab parts found for {creator_name}")

    return result

def get_parts_of(collab_name):
    """
    Retrieves all parts (layouts) belonging to a specific collab.

    Parameters
    ----------
    collab_name : str
        The name of the collab.

    Returns
    -------
    tuple[list[tuple[str, str, str]], int]
        - A list of tuples (name, yt, creator_name) representing each part.
        - The total expected number of builders for the collab (builders_number).

    Raises
    ------
    DataNotFound
        If the collab does not exist or no parts are found.
    """

    cursor.execute("SELECT builders_number FROM collab WHERE name = ?", (collab_name,))
    collab_data = cursor.fetchone()
    if not collab_data:
        raise DataNotFound(f"No collab found with name '{collab_name}'")

    builders_number = int(collab_data[0]) if collab_data[0] else 0


    cursor.execute(
        "SELECT name, yt, creator_name FROM layout WHERE masterlevel = ?",
        (collab_name,)
    )
    result = cursor.fetchall()

    if not result:
        raise DataNotFound(f"No parts found for collab '{collab_name}'")

    return result, builders_number


def get_creators():

    """Returns all creators as a list of rows."""

    cursor.execute(''' SELECT * FROM creator; ''')
    return cursor.fetchall()

# --- Similarly, get_layouts, get_collabs, get_musics, get_artists ---

def get_layouts():
    cursor.execute(''' SELECT * FROM layout; ''')
    return cursor.fetchall()


def get_collabs():
    cursor.execute(''' SELECT * FROM collab; ''')
    return cursor.fetchall()


def get_musics():
    cursor.execute(''' SELECT * FROM music; ''')
    return cursor.fetchall()


def get_artists():
    cursor.execute(''' SELECT * FROM artist; ''')
    return cursor.fetchall()


def synchronize_data():

    """

    Updates IDs and counts across tables:

    - Sets proper creator_id, artist_id, and music_id in layouts and collabs
    - Updates layouts_registered, collab_participations, total_time_built for creators
    - Updates 'uses' count for music
    - Updates songs_registered and total_song_uses for artists

    """

    missing_data = {
        "layout": [],
        "collab": [],
        "music": [],
        "creator": [],
        "artist": []
    }

    json_path = Path(__file__).parent.parent / "missing" / "missing_entries.json"
        
    # --- Update layout, collab, and music IDs ---

    cursor.execute(''' SELECT id, creator_name, music_name, music_artist FROM layout WHERE creator_id IS NULL OR artist_id IS NULL OR music_id is NULL; ''')
    layouts = cursor.fetchall()

    for id, creator_name, music_name, music_artist in layouts:

        try:
            context_creator = get_creator_by_name(creator_name)
            if context_creator:
                cursor.execute(''' UPDATE layout SET creator_id = ? WHERE id = ?; ''', (context_creator[0][0], id,))
        except Exception as e:
            applogger.warning(f"[LAYOUT:{id}] Failed to update creator_id: {e}")
            missing_data["layout"].append({"id": id, "missing": "creator_id", "error": str(e)})

        try:
            context_artist = get_artist_by_name(music_artist)
            if context_artist:
                cursor.execute(''' UPDATE layout SET artist_id = ? WHERE id = ?; ''', (context_artist[0][0], id,))
        except Exception as e:
            applogger.warning(f"[LAYOUT:{id}] Failed to update artist_id: {e}")
            missing_data["layout"].append({"id": id, "missing": "artist_id", "error": str(e)})

        try:
            context_music = get_music_by_name(music_name)
            if context_music:
                cursor.execute(''' UPDATE layout SET music_id = ? WHERE id = ?; ''', (context_music[0][0], id,))
        except Exception as e:
            applogger.warning(f"[LAYOUT:{id}] Failed to update music_id: {e}")
            missing_data["layout"].append({"id": id, "missing": "music_id", "error": str(e)})

    # --- Update collab table IDs similarly ---

    cursor.execute(''' SELECT id, host_name, music_name, music_artist FROM collab WHERE host_id IS NULL OR artist_id IS NULL OR music_id is NULL; ''')
    collabs = cursor.fetchall()

    for id, host_name, music_name, music_artist in collabs:

        try:

            context_host = get_creator_by_name(host_name)
            if context_host:
                cursor.execute(''' UPDATE collab SET host_id = ? WHERE id = ?; ''', (context_host[0][0], id,))

        except Exception as e:
            applogger.warning(f"[COLLAB:{id}] Failed to update host_id: {e}")
            missing_data["collab"].append({"id": id, "missing": "host_id", "error": str(e)})

        try:

            context_artist = get_artist_by_name(music_artist)
            if context_artist:
                cursor.execute(''' UPDATE collab SET artist_id = ? WHERE id = ?; ''', (context_artist[0][0], id,))
        
        except Exception as e:
            applogger.warning(f"[COLLAB:{id}] Failed to update artist_id: {e}")
            missing_data["collab"].append({"id": id, "missing": "artist_id", "error": str(e)})

        try:

            context_music = get_music_by_name(music_name)
            if context_music:
                cursor.execute(''' UPDATE collab SET music_id = ? WHERE id = ?; ''', (context_music[0][0], id,))

        except Exception as e:
            applogger.warning(f"[COLLAB:{id}] Failed to update music_id: {e}")
            missing_data["collab"].append({"id": id, "missing": "music_id", "error": str(e)})


    cursor.execute(''' SELECT id, artist FROM music WHERE artist_id IS NULL; ''')
    musics = cursor.fetchall()

    for id, artist in musics:

        try:
            context_artist = get_artist_by_name(artist)
            if context_artist:
                cursor.execute(''' UPDATE music SET artist_id = ? WHERE id = ?; ''', (context_artist[0][0], id,))
        except Exception as e:
            applogger.warning(f"[MUSIC:{id}] Failed to update artist_id: {e}")
            missing_data["music"].append({"id": id, "missing": "artist_id", "error": str(e)})

    # --- Update creator stats (layouts_registered, collab_participations, total_time_built) ---

    creators = get_creators()

    for creator in creators:

        try:

            cursor.execute(''' SELECT * FROM layout WHERE creator_id = ?; ''', (creator[0],))
            creators_layouts = cursor.fetchall()

            cursor.execute('''UPDATE creator SET layouts_registered = ? WHERE id = ?; ''', (len(creators_layouts), creator[0],))

            cursor.execute(''' SELECT * FROM layout WHERE masterlevel IS NOT NULL AND creator_id = ?; ''', (creator[0],))
            clbuser = cursor.fetchall()

            cursor.execute('''UPDATE creator SET collab_participations = ? WHERE id = ?; ''', (len(clbuser), creator[0],))

            total_time = tools.time_adder(*(layout[5] for layout in creators_layouts))
            cursor.execute(''' UPDATE creator SET total_time_built = ? WHERE id = ?; ''', (total_time, creator[0],))
        
        except Exception as e:
            applogger.warning(f"[CREATOR:{creator[0]}] Failed to update stats: {e}")

    # --- Updates music uses ---

    cursor.execute(''' SELECT id FROM music; ''')
    musics = cursor.fetchall()

    for row in musics:

        try:

            id = row[0]
            cursor.execute(''' SELECT * FROM layout WHERE music_id = ?''', (id,))
            layouts_with_ctx_song = cursor.fetchall()
            cursor.execute(''' UPDATE music SET uses = ? WHERE id = ?; ''', (len(layouts_with_ctx_song), id,))
        except Exception as e:
            applogger.warning(f"[MUSIC:{id}] Failed to update uses count: {e}")

    # --- Updates songs registered count and total song uses ---

    cursor.execute(''' SELECT id, name FROM artist; ''')
    artists = cursor.fetchall()

    for row in artists:

        try:

            id = row[0]
            cursor.execute(''' SELECT * FROM music WHERE artist_id = ?; ''', (id,))
            songs_by_ctx_artist = cursor.fetchall()
            cursor.execute(''' UPDATE artist SET songs_registered = ? WHERE id = ?; ''', (len(songs_by_ctx_artist), id,))

            cursor.execute(''' SELECT (SELECT count(*) FROM layout WHERE artist_id = ?) AS layout_count, (SELECT count(*) FROM collab WHERE artist_id = ?) AS collab_count; ''',
                            (id, id,))
            layout_count, collab_count = cursor.fetchone()
            tt = layout_count + collab_count
            cursor.execute(''' UPDATE artist SET total_song_uses = ? WHERE id = ?; ''', (tt, id,))
        
        except Exception as e:
            applogger.warning(f"[ARTIST:{id}] Failed to update stats: {e}")
    
    connection.commit()

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(missing_data, f, indent=4, ensure_ascii=False)
        

    applogger.info("Database successfully synced and missing data logged")


def execute_queries(script: str):
    """

    Executes a full SQL script.
    
    """
    cursor.executescript(script)
    connection.commit()

def get_oldest_request():

    
    cursor.execute('''
                   
    SELECT 'creator' AS type, rowid AS id, registration_date FROM requestcreator
    UNION ALL
    SELECT 'layout', rowid, registration_date FROM requestlayout
    UNION ALL
    SELECT 'collab', rowid, registration_date FROM requestcollab
    UNION ALL
    SELECT 'music', rowid, registration_date FROM requestmusic
    UNION ALL
    SELECT 'artist', rowid, registration_date FROM requestartist
    ORDER BY registration_date ASC
    LIMIT 1;'''
                   )

    result = cursor.fetchone()
    if not result:
        raise DataNotFound(f"No request found")
    return result

def get_request_details(type_, id_):

    table = f"request{type_}"
    cursor.execute(f"SELECT * FROM {table} WHERE rowid = ?", (id_,))
    result = cursor.fetchone()
    if not result:
        raise DataNotFound(f"No request found")
    return result

def delete_request(type_, id_):

    table = f"request{type_}"
    cursor.execute(f"DELETE FROM {table} WHERE rowid = ?", (id_,))
    connection.commit()

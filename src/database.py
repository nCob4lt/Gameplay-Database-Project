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
                   gdusername TEXT,
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
                   masterlevel_id INTEGER,
                   masterlevel TEXT DEFAULT NULL,
                   FOREIGN KEY (masterlevel_id) REFERENCES collab(id),                             
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
                   gdusername TEXT,
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
                   recorder_notes TEXT);''')
    
    # REQUEST UPDATE TABLES

    cursor.execute('''CREATE TABLE IF NOT EXISTS request_update_creator (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target_id INTEGER NOT NULL,
                    column_name TEXT NOT NULL,
                    old_value TEXT,
                    new_value TEXT,
                    recorder_name TEXT NOT NULL,
                    registration_date TEXT
                    );''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS request_update_layout (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target_id INTEGER NOT NULL,
                    column_name TEXT NOT NULL,
                    old_value TEXT,
                    new_value TEXT,
                    recorder_name TEXT NOT NULL,
                    registration_date TEXT
                    );''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS request_update_collab (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target_id INTEGER NOT NULL,
                    column_name TEXT NOT NULL,
                    old_value TEXT,
                    new_value TEXT,
                    recorder_name TEXT NOT NULL,
                    registration_date TEXT
                    );''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS request_update_music (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target_id INTEGER NOT NULL,
                    column_name TEXT NOT NULL,
                    old_value TEXT,
                    new_value TEXT,
                    recorder_name TEXT NOT NULL,
                    registration_date TEXT
                    );''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS request_update_artist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target_id INTEGER NOT NULL,
                    column_name TEXT NOT NULL,
                    old_value TEXT,
                    new_value TEXT,
                    recorder_name TEXT NOT NULL,
                    registration_date TEXT
                    );''')
    
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
   
def register_creator(username, nationality, discord_uname, discord_uid, yt, gdusername, registrator):

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
                    gdusername,
                    registration_date,
                    recorder_name) VALUES (?,?,?,?,?,?,?,?);''',
                    (username, nationality, discord_uname, discord_uid, yt, gdusername, dt, registrator))
    
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

def register_request_creator(username, nationality, discord_uname, discord_uid, yt, gdusername, registrator):

    dt = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute('''INSERT INTO requestcreator (
                        username,
                        nationality,
                        discord,
                        discord_uid,
                        yt,
                        gdusername,
                        registration_date,
                        recorder_name
                      ) VALUES (?,?,?,?,?,?,?,?);''',
                   (username, nationality, discord_uname, discord_uid, yt, gdusername, dt, registrator))
    
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

def register_update_creator(target_id, column_name, old_value, new_value, registrator):

    dt = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute('''INSERT INTO request_update_creator (
                        target_id,
                        column_name,
                        old_value,
                        new_value,
                        recorder_name,
                        registration_date
                      ) VALUES (?,?,?,?,?,?);''',
                   (target_id, column_name, old_value, new_value, registrator, dt))
    
    connection.commit()


def register_update_layout(target_id, column_name, old_value, new_value, registrator):

    dt = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute('''INSERT INTO request_update_layout (
                        target_id,
                        column_name,
                        old_value,
                        new_value,
                        recorder_name,
                        registration_date
                      ) VALUES (?,?,?,?,?,?);''',
                   (target_id, column_name, old_value, new_value, registrator, dt))
    
    connection.commit()


def register_update_collab(target_id, column_name, old_value, new_value, registrator):

    dt = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute('''INSERT INTO request_update_collab (
                        target_id,
                        column_name,
                        old_value,
                        new_value,
                        recorder_name,
                        registration_date
                      ) VALUES (?,?,?,?,?,?);''',
                   (target_id, column_name, old_value, new_value, registrator, dt))
    
    connection.commit()


def register_update_music(target_id, column_name, old_value, new_value, registrator):

    dt = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute('''INSERT INTO request_update_music (
                        target_id,
                        column_name,
                        old_value,
                        new_value,
                        recorder_name,
                        registration_date
                      ) VALUES (?,?,?,?,?,?);''',
                   (target_id, column_name, old_value, new_value, registrator, dt))
    
    connection.commit()


def register_update_artist(target_id, column_name, old_value, new_value, registrator):

    dt = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute('''INSERT INTO request_update_artist (
                        target_id,
                        column_name,
                        old_value,
                        new_value,
                        recorder_name,
                        registration_date
                      ) VALUES (?,?,?,?,?,?);''',
                   (target_id, column_name, old_value, new_value, registrator, dt))
    
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

def get_creator_by_id(uid):

    """

    Retrieves a creator by id.

    Raises
    ------
    DataNotFound
        If no creator exists with the given id.

    """

    cursor.execute('''SELECT * FROM creator WHERE id = ?;''', (uid,))
    result = cursor.fetchall()
    if not result:
        raise DataNotFound(f"No creator found with id '{uid}'")
    return result

def get_layout_by_id(layout_id):
    cursor.execute('''SELECT * FROM layout WHERE id = ?;''', (layout_id,))
    result = cursor.fetchall()
    if not result:
        raise DataNotFound(f"No layout found with id '{layout_id}'")
    return result


def get_collab_by_id(collab_id):
    cursor.execute('''SELECT * FROM collab WHERE id = ?;''', (collab_id,))
    result = cursor.fetchall()
    if not result:
        raise DataNotFound(f"No collab found with id '{collab_id}'")
    return result


def get_music_by_id(music_id):
    cursor.execute('''SELECT * FROM music WHERE id = ?;''', (music_id,))
    result = cursor.fetchall()
    if not result:
        raise DataNotFound(f"No music found with id '{music_id}'")
    return result


def get_artist_by_id(artist_id):
    cursor.execute('''SELECT * FROM artist WHERE id = ?;''', (artist_id,))
    result = cursor.fetchall()
    if not result:
        raise DataNotFound(f"No artist found with id '{artist_id}'")
    return result

def get_random_layout():
    cursor.execute(''' SELECT * FROM layout ORDER BY RANDOM() LIMIT 1''')
    result = cursor.fetchone()
    if not result:
        raise DataNotFound("Internal error or no layouts registered in the database")
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

def update(table: str, entry_id: int, attr: str, value):

    """
    Update one attribute of a row in a table.

    table: name of the table
    entry_id: id of the row to update
    attr: column name to update
    value: new value
    """

    allowed_tables = {"creator", "layout", "collab", "music", "artist"}

    if table not in allowed_tables:
        raise ValueError(f"Invalid table name '{table}'")

    cursor.execute(f"PRAGMA table_info({table})")
    cols = {row[1] for row in cursor.fetchall()}

    if attr not in cols:
        raise ValueError(f"Invalid column '{attr}' in table '{table}'")

    sql = f"UPDATE {table} SET {attr} = ? WHERE id = ?"
    cursor.execute(sql, (value, entry_id))
    connection.commit()


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

    cursor.execute(''' SELECT id, name, creator_name, music_name, music_artist, masterlevel FROM layout WHERE creator_id IS NULL OR artist_id IS NULL OR music_id IS NULL OR masterlevel_id IS NULL; ''')
    layouts = cursor.fetchall()

    for id, name, creator_name, music_name, music_artist, masterlevel in layouts:

        try:
            context_creator = get_creator_by_name(creator_name)
            if context_creator:
                cursor.execute(''' UPDATE layout SET creator_id = ? WHERE id = ?; ''', (context_creator[0][0], id,))
        except Exception as e:
            applogger.warning(f"[LAYOUT:{id}] Failed to update creator_id: {e}")
            missing_data["layout"].append({"id": id, "name": name, "missing": "creator_id", "error": str(e)})

        try:
            context_artist = get_artist_by_name(music_artist)
            if context_artist:
                cursor.execute(''' UPDATE layout SET artist_id = ? WHERE id = ?; ''', (context_artist[0][0], id,))
        except Exception as e:
            applogger.warning(f"[LAYOUT:{id}] Failed to update artist_id: {e}")
            missing_data["layout"].append({"id": id, "name": name, "missing": "artist_id", "error": str(e)})

        try:
            context_music = get_music_by_name(music_name)
            if context_music:
                cursor.execute(''' UPDATE layout SET music_id = ? WHERE id = ?; ''', (context_music[0][0], id,))
        except Exception as e:
            applogger.warning(f"[LAYOUT:{id}] Failed to update music_id: {e}")
            missing_data["layout"].append({"id": id, "name": name, "missing": "music_id", "error": str(e)})

        try:
            if masterlevel:
                context_masterlevel = get_collab_by_name(masterlevel)
                if context_masterlevel:
                    cursor.execute(
                        "UPDATE layout SET masterlevel_id = ? WHERE id = ?",
                        (context_masterlevel[0][0], id)
                    )
                else:
                    pass
        except Exception as e:
            applogger.warning(f"[LAYOUT:{id}] Failed to update masterlevel_id: {e}")
            missing_data["layout"].append({"id": id, "name": name, "missing": "masterlevel_id", "error": str(e)})

    # --- Update collab table IDs similarly ---

    cursor.execute(''' SELECT id, name, host_name, music_name, music_artist FROM collab WHERE host_id IS NULL OR artist_id IS NULL OR music_id is NULL; ''')
    collabs = cursor.fetchall()

    for id, name, host_name, music_name, music_artist in collabs:

        try:

            context_host = get_creator_by_name(host_name)
            if context_host:
                cursor.execute(''' UPDATE collab SET host_id = ? WHERE id = ?; ''', (context_host[0][0], id,))

        except Exception as e:
            applogger.warning(f"[COLLAB:{id}] Failed to update host_id: {e}")
            missing_data["collab"].append({"id": id, "name": name, "missing": "host_id", "error": str(e)})

        try:

            context_artist = get_artist_by_name(music_artist)
            if context_artist:
                cursor.execute(''' UPDATE collab SET artist_id = ? WHERE id = ?; ''', (context_artist[0][0], id,))
        
        except Exception as e:
            applogger.warning(f"[COLLAB:{id}] Failed to update artist_id: {e}")
            missing_data["collab"].append({"id": id, "name": name, "missing": "artist_id", "error": str(e)})

        try:

            context_music = get_music_by_name(music_name)
            if context_music:
                cursor.execute(''' UPDATE collab SET music_id = ? WHERE id = ?; ''', (context_music[0][0], id,))

        except Exception as e:
            applogger.warning(f"[COLLAB:{id}] Failed to update music_id: {e}")
            missing_data["collab"].append({"id": id, "name": name, "missing": "music_id", "error": str(e)})


    cursor.execute(''' SELECT id, name, artist FROM music WHERE artist_id IS NULL; ''')
    musics = cursor.fetchall()

    for id, name, artist in musics:

        try:
            context_artist = get_artist_by_name(artist)
            if context_artist:
                cursor.execute(''' UPDATE music SET artist_id = ? WHERE id = ?; ''', (context_artist[0][0], id,))
        except Exception as e:
            applogger.warning(f"[MUSIC:{id}] Failed to update artist_id: {e}")
            missing_data["music"].append({"id": id, "name": name, "missing": "artist_id", "error": str(e)})

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

    """
    Returns the oldest pending registration or update request from all tables.
    """

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
        UNION ALL
        SELECT 'update_creator', rowid, registration_date FROM request_update_creator
        UNION ALL
        SELECT 'update_layout', rowid, registration_date FROM request_update_layout
        UNION ALL
        SELECT 'update_collab', rowid, registration_date FROM request_update_collab
        UNION ALL
        SELECT 'update_music', rowid, registration_date FROM request_update_music
        UNION ALL
        SELECT 'update_artist', rowid, registration_date FROM request_update_artist
        ORDER BY registration_date ASC
        LIMIT 1;
    ''')

    result = cursor.fetchone()
    if not result:
        raise DataNotFound("No request found")
    return result


def get_request_details(request_type: str, request_id: int):

    """
    Fetch the details of a pending request from the correct request table.
    """

    table_map = {

        "creator": "requestcreator",
        "layout": "requestlayout",
        "collab": "requestcollab",
        "music": "requestmusic",
        "artist": "requestartist",
        "update_creator": "request_update_creator",
        "update_layout": "request_update_layout",
        "update_collab": "request_update_collab",
        "update_music": "request_update_music",
        "update_artist": "request_update_artist",
    }

    if request_type not in table_map:
        raise DataNotFound(f"Unknown request type: {request_type}")

    table = table_map[request_type]

    cursor.execute(f"SELECT * FROM {table} WHERE rowid = ?;", (request_id,))
    result = cursor.fetchone()

    if not result:
        raise DataNotFound(f"No request with ID {request_id} in {table}")

    return dict(result)

def delete_request(request_type: str, request_id: int):
    """
    Deletes a pending request from the correct table.
    """

    table_map = {
        "creator": "requestcreator",
        "layout": "requestlayout",
        "collab": "requestcollab",
        "music": "requestmusic",
        "artist": "requestartist",
        "update_creator": "request_update_creator",
        "update_layout": "request_update_layout",
        "update_collab": "request_update_collab",
        "update_music": "request_update_music",
        "update_artist": "request_update_artist",
    }

    if request_type not in table_map:
        raise DataNotFound(f"Unknown request type: {request_type}")

    table = table_map[request_type]

    cursor.execute(f"DELETE FROM {table} WHERE rowid = ?;", (request_id,))
    connection.commit()

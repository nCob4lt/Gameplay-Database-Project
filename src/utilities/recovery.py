"""

File: recovery.py

Description: This module handles database backup and restore operations for the Gameplay Database project.

It provides:
- Automatic database save creation (as SQL dumps)
- Loading a saved database backup into the active database

Backups are stored in the /saves directory (created automatically if missing).

Author: cobalt

"""

# --- Standard imports ---
from pathlib import Path
import sqlite3
import io
import database
from datetime import datetime

# --- Local imports ---
from utilities.applogger import AppLogger

# --- Application logger ---
applogger = AppLogger()

def create_save():

    """

    Creates a full SQL backup of the current database.

    This function exports the entire content and structure of the
    'gpdb.db' SQLite database to a timestamped `.sql` file
    located in the 'saves/' directory.

    The backup file is created using SQLite's `iterdump()` method,
    ensuring a complete and restorable snapshot.

    File naming convention:
        gpdb-backupYYYY-MM-DDHHMMSS.sql

    Example:
        gpdb-backup2025-10-14213045.sql

    Side Effects
    ------------
    - Creates the 'saves/' directory if it doesn't exist.
    - Writes a new SQL backup file.
    - Logs the creation event.

    Raises
    ------
    sqlite3.Error
        If an issue occurs during the database dump.

    """
    save_dir = Path(__file__).parent.parent.parent / "saves"
    save_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.today().strftime("%Y-%m-%d%H%M%S")
    backup_file = save_dir / f"gpdb-backup{timestamp}.sql"

    connection = sqlite3.connect("gpdb.db")
    with io.open(backup_file, "w", encoding="utf-8") as p:
        for line in connection.iterdump():
            p.write('%s\n' % line)

    connection.close()
    applogger.info(f"Save created at {backup_file}")

def load_save(filename):

    """

    Loads a saved database backup (.sql) into the current database.

    This function reads a backup SQL file from the 'saves/' directory,
    clears the current database, and restores all data and schema
    from the provided backup file.

    Parameters
    ----------
    filename : str
        The name of the SQL backup file (e.g. 'gpdb-backup2025-10-14T213045.sql').

    Behavior
    --------
    - Reads SQL commands from the backup file.
    - Clears existing database tables using `database.clear()`.
    - Executes the backup SQL script to restore all data.

    Side Effects
    ------------
    - Modifies the current database.
    - Logs restoration status and errors.

    Raises
    ------
    FileNotFoundError
        If the specified backup file does not exist.

    """

    save_dir = Path(__file__).parent.parent.parent / "saves"
    file_path = save_dir / filename

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            queries = f.read()

        database.clear()
        database.execute_queries(queries)
        applogger.debug(f"Retrieved data from {filename}")
            
    except FileNotFoundError:
        applogger.error("Failed to retrieve data: the savefile was not found")

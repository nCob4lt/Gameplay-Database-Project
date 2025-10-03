from pathlib import Path
import sqlite3
import io
import database
from datetime import datetime
from utilities.applogger import AppLogger

applogger = AppLogger()

class Recovery:

    @staticmethod
    def create_save():
        save_dir = Path(__file__).parent.parent / "saves"
        save_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.today().strftime("%Y-%m-%d%H%M%S")
        backup_file = save_dir / f"gpdb-backup{timestamp}.sql"

        connection = sqlite3.connect("gpdb.db")
        with io.open(backup_file, "w", encoding="utf-8") as p:
            for line in connection.iterdump():
                p.write('%s\n' % line)

        connection.close()
        applogger.info(f"Save created at {backup_file}")


    @staticmethod
    def load_save(filename):

        save_dir = Path(__file__).parent.parent / "saves"
        file_path = save_dir / filename

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                queries = f.read()

            database.clear()
            database.execute_queries(queries)
            applogger.debug(f"Retrieved data from {filename}")
                
        except FileNotFoundError:
            applogger.error("Failed to retrieve data: the savefile was not found")

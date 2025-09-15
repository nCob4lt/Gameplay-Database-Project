from datetime import datetime
from pathlib import Path

class AppLogger:

    def __init__(self, log_file: str = None):

        if log_file is None:
            # __file__ = chemin de ce fichier logger
            log_file = Path(__file__).parent.parent / "logs" / "latest.log"

        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)  # crée le dossier si nécessaire
        log_file.touch(exist_ok=True)  # crée le fichier s'il n'existe pas

        self.log_file = log_file

    def _write(self, type: str, message: str):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{now}] [{type.upper()}] {message}\n"
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(line)

    def info(self, message: str):
        self._write("INFO", message)

    def warning(self, message: str):
        self._write("WARNING", message)

    def error(self, message: str):
        self._write("ERROR", message)

    def debug(self, message: str):
        self._write("DEBUG", message)

        

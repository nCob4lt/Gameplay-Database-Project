from datetime import datetime
from pathlib import Path
import discord

class AppLogger:

    def __init__(self, log_file: str = None):

        if log_file is None:
            log_file = Path(__file__).parent.parent / "logs" / "latest.log"

        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)  
        log_file.touch(exist_ok=True)  

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

    def debug_command(self, interaction: discord.Interaction):
        args_list = [f"{opt['name']}={opt['value']}" for opt in interaction.data.get("options", [])]
        self.debug(f"{interaction.user.name} used {interaction.command.name} within the following args: {args_list}")

        

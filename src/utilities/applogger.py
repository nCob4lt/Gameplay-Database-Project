from pathlib import Path
import discord

import logging, sys
import asyncio

class AppLogger:

    def __init__(self, log_file: str = None):

        if log_file is None:
            log_file = Path(__file__).parent.parent / "logs" / "latest.log"

        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)  
        log_file.touch(exist_ok=True)  

        self.logger = logging.getLogger("gpdb")
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.hasHandlers():
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)

            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)

            formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
            console_handler.setFormatter(formatter)
            file_handler.setFormatter(formatter)

            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)

        sys.excepthook = self.handle_exception

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        self.logger.error("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))

    def setup_asyncio_handler(self, loop: asyncio.AbstractEventLoop):
        def handle_async_exception(loop, context):
            exc = context.get("exception")
            msg = context.get("message")
            if exc:
                self.logger.error(f"Unhandled asyncio exception : {exc}", exc_info=exc)
            elif msg:
                self.logger.error(f"Unhandled asyncio exception : {msg}")
        loop.set_exception_handler(handle_async_exception)

    def info(self, message: str): self.logger.info(message)
    def debug(self, message: str): self.logger.debug(message)
    def warning(self, message: str): self.logger.warning(message)
    def error(self, message: str): self.logger.error(message)

    def debug_command(self, interaction: discord.Interaction):
        args_list = [f"{opt['name']}={opt['value']}" for opt in interaction.data.get("options", [])]
        self.debug(f"{interaction.user.name} used {interaction.command.name} within the following args: {args_list}")

        

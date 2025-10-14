"""

File: applogger.py

Description: This module defines the `AppLogger` class, a unified and application-wide logging
utility for the Gameplay Database project.

It provides:
- Automatic console and file logging with timestamps and levels.
- Global exception handling (for both synchronous and asynchronous errors).
- Integrated logging for Discord bot commands (via `discord.Interaction`).
- Centralized logging configuration, ensuring consistent formatting and behavior.

All logs are stored in the `/logs/latest.log` file by default.

Author: cobalt

"""

# --- Standard imports ---
from pathlib import Path
import discord
import logging, sys
import asyncio

class AppLogger:

    """

    Application-level logger with built-in support for both console and file logging.

    This class encapsulates Python's standard `logging` module and adds:
    - A default log file (`logs/latest.log`).
    - Unified console and file output with identical formatting.
    - Global exception handling via `sys.excepthook`.
    - Async exception handling for asyncio event loops.
    - Convenience methods (`info`, `debug`, `warning`, `error`).
    - A helper for logging Discord commands usage (`debug_command`).

    Parameters
    ----------
    log_file : str | Path, optional
        Custom path for the log file. Defaults to 'logs/latest.log' at the project root.

    Example
    -------
    >>> applogger = AppLogger()
    >>> applogger.info("Server started successfully.")
    >>> applogger.debug("Connected to database.")

    """

    def __init__(self, log_file: str = None):

        """Initialize the logger, configure file and console handlers, and setup global exception hook."""

        if log_file is None:
            log_file = Path(__file__).parent.parent.parent / "logs" / "latest.log"

        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)  
        log_file.touch(exist_ok=True)  
        
        # Create or retrieve the logger instance
        self.logger = logging.getLogger("gpdb")
        self.logger.setLevel(logging.DEBUG)

        # Avoid adding multiple handlers when multiple instances are created
        if not self.logger.hasHandlers():
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)

            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)

            # Common log format: [timestamp] [LEVEL] message
            formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
            console_handler.setFormatter(formatter)
            file_handler.setFormatter(formatter)

            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)

        # Attach a global exception handler for uncaught errors
        sys.excepthook = self.handle_exception

    # -------------------- EXCEPTION HANDLING --------------------

    def handle_exception(self, exc_type, exc_value, exc_traceback):

        """

        Handle unhandled exceptions globally.

        This replaces Python's default `sys.excepthook` to ensure that all uncaught
        exceptions are logged automatically to both the console and the log file.

        Parameters
        ----------
        exc_type : type
            Exception class (e.g., ValueError).
        exc_value : Exception
            The actual exception instance.
        exc_traceback : traceback
            Traceback object for debugging.

        """

        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        self.logger.error("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))

    def setup_asyncio_handler(self, loop: asyncio.AbstractEventLoop):

        """

        Set a global handler for uncaught asyncio exceptions.

        This ensures that asynchronous exceptions (e.g., from `asyncio.create_task`)
        are caught and logged instead of being silently ignored.

        Parameters
        ----------
        loop : asyncio.AbstractEventLoop
            The asyncio event loop for which to set the exception handler.

        """
        def handle_async_exception(loop, context):
            exc = context.get("exception")
            msg = context.get("message")
            if exc:
                self.logger.error(f"Unhandled asyncio exception : {exc}", exc_info=exc)
            elif msg:
                self.logger.error(f"Unhandled asyncio exception : {msg}")
        loop.set_exception_handler(handle_async_exception)

    # -------------------- LOGGING METHODS -------------------

    def info(self, message: str): self.logger.info(message)
    def debug(self, message: str): self.logger.debug(message)
    def warning(self, message: str): self.logger.warning(message)
    def error(self, message: str): self.logger.error(message)

    def debug_command(self, interaction: discord.Interaction):

        """

        Log detailed information about a Discord command execution.

        Useful for tracing user activity and command usage during bot operation.

        Parameters
        ----------
        interaction : discord.Interaction
            The Discord interaction object containing command metadata.

        Example
        -------
        [2025-10-14 21:45:03] [DEBUG] user1 used get_creator_by_name with args: ['user=JohnDoe']

        """
        args_list = [f"{opt['name']}={opt['value']}" for opt in interaction.data.get("options", [])]
        self.debug(f"{interaction.user.name} used {interaction.command.name} within the following args: {args_list}")

        

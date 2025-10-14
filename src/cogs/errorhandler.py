"""

File: errorhandler.py

This module defines the ErrorHandlerCog, a Discord cog responsible for
handling and logging errors throughout the bot. It captures exceptions raised
during application command execution and general bot events, providing
user-friendly feedback for known exceptions and logging detailed information
for debugging unknown errors.

Key Features:
- Global handling of Discord application command errors.
- Specific handling for custom exceptions such as DataNotFound and
  MissingModPermissions.
- Logs detailed information about unhandled command and event errors.
- Sends ephemeral messages to users for known exceptions to prevent exposing
  sensitive details.

Classes:
- ErrorHandlerCog: Cog for centralized error handling and logging.

"""

# --- Standard imports ---
from discord.ext import commands
import discord

# --- Local imports
from utilities.applogger import AppLogger
from exceptions.custom_exceptions import *

class ErrorHandlerCog(commands.Cog):

    """

    Cog dedicated to handling errors globally within the Discord bot.

    This cog captures and logs exceptions raised during the execution of Discord
    application commands and general bot events. It provides user-friendly messages
    for known exceptions while logging unhandled errors for debugging purposes.

    Key Features:
    - Handles `AppCommandError` for Discord app commands.
    - Differentiates between known custom exceptions (like `DataNotFound` or
      `MissingModPermissions`) and general errors.
    - Logs detailed exception info including the originating command or event.
    - Ensures ephemeral messages are sent to users for errors without exposing
      sensitive information.

    Attributes
    ----------
    bot : commands.Bot
        The bot instance the cog is attached to.
    applogger : AppLogger
        Logger instance used to log error messages and debug information.

    """

    def __init__(self, bot, applogger: AppLogger):

        """

        Initializes the ErrorHandlerCog.

        Registers the app command error listener to handle global errors.

        Parameters
        ----------
        bot : commands.Bot
            The Discord bot instance.
        applogger : AppLogger
            Logger instance for logging errors and debug information.

        """
        self.bot = bot
        self.applogger = applogger

        self.bot.tree.error(self.on_app_command_error)

    @commands.Cog.listener("on_app_command_error")
    async def on_app_command_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):

        """

        Handles errors raised during the execution of Discord application commands.

        Logs all errors and provides user-friendly messages for known exceptions
        defined in `custom_exceptions`.

        Custom exception handling:
        - `DataNotFound`: Sends ephemeral message "**User** not found!".
        - `MissingModPermissions`: Sends ephemeral message "**You** are not authorized!".

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object that triggered the command.
        error : discord.app_commands.AppCommandError
            The exception object raised during the command execution.
        """

        self.applogger.error(
            f"Raised unhandled app command error: {interaction.command.name if interaction.command else 'unknown'} - {error}"
        )
        
        if isinstance(error, discord.app_commands.CommandInvokeError):
            original = error.original

            match original:
                case DataNotFound():
                    await interaction.response.send_message("**User** not found !", ephemeral=True)

                case MissingModPermissions():
                    await interaction.response.send_message("**You** are not authorized !", ephemeral=True)
        
    @commands.Cog.listener()
    async def on_error(self, event_name, *args, **kwargs):

        """

        Handles unhandled errors from general bot events.

        Logs detailed exception information for debugging purposes.

        Parameters
        ----------
        event_name : str
            Name of the event that caused the error.
        *args : tuple
            Positional arguments passed to the event handler.
        **kwargs : dict
            Keyword arguments passed to the event handler.

        """
        
        self.applogger.error(f"Unhandled event error: {event_name}", exc_info=True)

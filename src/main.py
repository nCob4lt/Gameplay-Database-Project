"""

File: main.py

Description: Contains the initial instantiation of the bot class and run the Discord application

Author: cobalt

"""

# --- Standard imports ---
import discord
from discord.ext import commands
import os

# --- Local imports ---
from cogs.maincog import MainCog
from cogs.query import QueryCog
from cogs.registration import RegistrationCog
from cogs.errorhandler import ErrorHandlerCog
from utilities.applogger import AppLogger

# --- Logger instantiation ---
applogger = AppLogger()

class GameplayDatabase(commands.Bot):

    """

    Custom class for the Gameplay Database Discord bot.

    Inherits from `commands.Bot` and sets up:
        - Command prefix for traditional commands (not used)
        - All intents to access members, messages, reactions, etc.
        - Custom cogs for main functionality, registration, queries, and error handling
        - Synchronization of application commands (slash commands) with Discord

    """

    def __init__(self) -> None:

        """

        Initialize the bot instance.

        Sets the command prefix and enables all intents.

        """

        super().__init__(command_prefix="db!", intents=discord.Intents.all())

    async def setup_hook(self):

        """

        Called by discord.py before the bot connects to Discord.

        Responsible for:
            - Adding all Cogs
            - Syncing application commands (slash commands)
            - Logging the synced commands

        """

        await bot.add_cog(MainCog(bot))
        await bot.add_cog(RegistrationCog(bot))
        await bot.add_cog(QueryCog(bot))
        await bot.add_cog(ErrorHandlerCog(bot, applogger))

        synced = await self.tree.sync()
        applogger.info(f"Synchronized commands : {[cmd.name for cmd in synced]}")

# Instantiate the bot
bot = GameplayDatabase()

# Remove default 'help' command since custom help will be used
bot.remove_command("help")

# Retrieve Discord bot token from environment variable
TOKEN = os.getenv("DISCORD_GDDB_TOKEN")

# Start the bot
bot.run(TOKEN)
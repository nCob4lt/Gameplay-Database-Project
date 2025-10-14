"""

File: maincog.py

This module defines the `MainCog` class — the core cog responsible for managing
the lifecycle, background tasks, and maintenance operations of the Gameplay Database bot.

It performs the following key roles:
    - Handles the bot's startup routine (`on_ready`)
    - Manages periodic tasks for data synchronization and auto-saving
    - Provides a command to manually load database backups

All activity and errors are logged through the `AppLogger` utility for easier debugging
and maintenance.

Author: cobalt  

"""

# --- Standard imports ---
import discord
from discord.ext import commands, tasks

# --- Local imports
import database
from utilities.applogger import AppLogger
from utilities import recovery
from utilities import tools

# --- Setup logging and intents ---
intents = discord.Intents.all()
intents.guilds = True
applogger = AppLogger()


class MainCog(commands.Cog):

    """

    Core management cog for the Gameplay Database Discord bot.

    This cog initializes the bot, starts background synchronization and save tasks,
    and provides recovery-related utilities such as loading backups.

    Attributes
    ----------
    bot : commands.Bot
        The main Discord bot instance associated with this cog.

    """
    def __init__(self, bot: commands.Bot) -> None:

        """Initialize the MainCog with a reference to the bot instance."""

        self.bot = bot

    @commands.Cog.listener(name="on_ready")
    async def starting(self):

        """

        Event listener triggered when the bot is ready.

        This method:
            - Logs that the bot is online
            - Updates the bot's Discord presence
            - Starts the periodic sync and save background tasks
            - Launches the asynchronous database worker

        """

        applogger.info("Ready to use")
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Gameplay Database"))

        if not self.sync.is_running():
            self.sync.start()
            applogger.info("Sync task started")

        if not self.save.is_running():
            self.save.start()
            applogger.info("Save task started")

        self.bot.loop.create_task(database.database_worker())

    # --- BACKGROUND TASKS ---

    @tasks.loop(seconds=5)
    async def sync(self):

        """

        Periodic synchronization task.

        Runs every 5 seconds to enqueue the `synchronize_data` function into
        the database's asynchronous task queue, ensuring all live data is kept in sync.

        """
        await database.database_queue.put((database.synchronize_data, (), {}))

    @tasks.loop(minutes=5)
    async def save(self):

        """

        Periodic save task.

        Runs every 5 minutes to trigger an automatic database backup using the
        recovery module. Logs its activity for traceability.

        """
        applogger.debug("Starting database save...")
        recovery.create_save()

    @discord.app_commands.command(name="load_backup", description="Loads a file from save folder")
    @discord.app_commands.describe(filename="Name of the file")
    async def loadsave(self, interaction: discord.Interaction, filename: str):

        """

        Loads a database backup file from the local save directory.

        This command allows moderators to manually restore the database
        from a previously saved backup file. It ensures that only authorized
        users can perform the operation, preventing unauthorized data restoration.

        Parameters
        ----------
        interaction : discord.Interaction
            The Discord interaction context where the command is executed.
        filename : str
            The exact name of the backup file to load from the save folder.

        Behavior
        --------
        - Verifies that the user has moderator permissions using `tools.check_mod()`.
        - Logs the command usage via `AppLogger.debug_command()`.
        - Calls `recovery.load_save()` to restore database content from the given file.

        Notes
        -----
        - Only available to moderators.
        - Loading a backup will overwrite the current database contents.
        - Ensure the specified file exists in the save folder before execution.
        - Recommended to back up current data before restoring an older version.
        
        """

        await tools.check_mod(interaction)
        applogger.debug_command(interaction)
        recovery.load_save(filename)


    

            
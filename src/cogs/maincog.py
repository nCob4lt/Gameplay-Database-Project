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
        await interaction.response.send_message("Backup **successfully** loaded.")

    @discord.app_commands.command(
        name="database_stats",
        description="Display a database dashboard with stats"
    )
    async def database_stats(self, interaction: discord.Interaction):
        await interaction.response.defer()
        cursor = database.cursor

        try:
            # --- Creators ---
            cursor.execute("SELECT COUNT(*) FROM creator")
            total_creators = cursor.fetchone()[0] or 0

            cursor.execute("SELECT SUM(layouts_registered) FROM creator")
            total_layouts_by_creators = cursor.fetchone()[0] or 0

            cursor.execute("SELECT SUM(collab_participations) FROM creator")
            total_collabs_by_creators = cursor.fetchone()[0] or 0

            cursor.execute("""
                SELECT username, (layouts_registered + collab_participations) AS total 
                FROM creator ORDER BY total DESC LIMIT 5
            """)
            top_creators = cursor.fetchall()

            # --- Musics & Artists ---
            cursor.execute("SELECT COUNT(*) FROM music")
            total_musics = cursor.fetchone()[0] or 0

            cursor.execute("SELECT COUNT(*) FROM artist")
            total_artists = cursor.fetchone()[0] or 0

            cursor.execute("SELECT name, uses FROM music ORDER BY uses DESC LIMIT 5")
            top_musics = cursor.fetchall()

            cursor.execute("SELECT name, total_song_uses FROM artist ORDER BY total_song_uses DESC LIMIT 5")
            top_artists = cursor.fetchall()

            cursor.execute("SELECT COUNT(*) FROM music WHERE (yt IS NULL OR yt='') AND (soundcloud IS NULL OR soundcloud='')")
            missing_links = cursor.fetchone()[0] or 0

            # --- Layouts & Collabs ---
            cursor.execute("SELECT COUNT(*) FROM layout")
            total_layouts = cursor.fetchone()[0] or 0

            cursor.execute("SELECT COUNT(*) FROM collab")
            total_collabs = cursor.fetchone()[0] or 0

            cursor.execute("SELECT COUNT(*) FROM layout WHERE masterlevel IS NOT NULL")
            total_parts = cursor.fetchone()[0] or 0

            cursor.execute("SELECT AVG(CAST(builders_number AS INTEGER)) FROM collab")
            avg_builders = round(cursor.fetchone()[0] or 0, 1)

            cursor.execute("SELECT SUM(CAST(builders_number AS INTEGER)) FROM collab")
            total_expected_parts = cursor.fetchone()[0] or 0

            incomplete_parts = total_expected_parts - total_parts

            cursor.execute("SELECT COUNT(*) FROM layout WHERE type='Experimental'")
            experimental_layouts = cursor.fetchone()[0] or 0

            normal_layouts = total_layouts - experimental_layouts

            cursor.execute("SELECT MAX(registration_date) FROM layout")
            last_update = cursor.fetchone()[0] or "Unknown"

        except Exception as e:
            await interaction.followup.send(f"⚠️ Failed to fetch database stats: `{e}`")
            return

        # --- Build embed with sections ---
        embed = discord.Embed(
            title="📊 Gameplay Database Statistics",
            color=discord.Color.dark_blue(),
            description="Advanced dashboard of the database with nerdy stats"
        )

        # --- Creators Section ---
        embed.add_field(name="💠 Creators", value="────────────────────", inline=False)
        embed.add_field(name="Total creators", value=str(total_creators), inline=False)
        embed.add_field(name="Layouts by creators", value=str(total_layouts_by_creators), inline=False)
        embed.add_field(name="Collab participations", value=str(total_collabs_by_creators), inline=False)
        embed.add_field(
            name="Top 5 active creators",
            value="\n".join([f"{c[0]} ({c[1]} levels)" for c in top_creators]) or "N/A",
            inline=False
        )

        # --- Musics & Artists Section ---
        embed.add_field(name="🎵 Musics & Artists", value="────────────────────", inline=False)
        embed.add_field(name="Total musics", value=str(total_musics), inline=False)
        embed.add_field(name="Total artists", value=str(total_artists), inline=False)
        embed.add_field(
            name="Top 5 musics by uses",
            value="\n".join([f"{m[0]} ({m[1]} uses)" for m in top_musics]) or "N/A",
            inline=False
        )
        embed.add_field(
            name="Top 5 artists by song usage",
            value="\n".join([f"{a[0]} ({a[1]} total uses)" for a in top_artists]) or "N/A",
            inline=False
        )
        embed.add_field(name="Musics missing links", value=str(missing_links), inline=False)

        # --- Layouts & Collabs Section ---
        embed.add_field(name="🧩 Layouts & Collabs", value="────────────────────", inline=False)
        embed.add_field(name="Total layouts", value=str(total_layouts), inline=False)
        embed.add_field(name="Total collabs", value=str(total_collabs), inline=False)
        embed.add_field(
            name="Layout types",
            value=f"Experimental: {experimental_layouts}\nNormal: {normal_layouts}",
            inline=False
        )
        embed.add_field(
            name="Parts info",
            value=f"Registered: {total_parts}/{total_expected_parts}\n"
                + (f"⚠️ Some parts are missing from the database!" if incomplete_parts > 0 else "All parts are recorded ✅"),
            inline=False
        )
        embed.add_field(name="Average builders per collab", value=str(avg_builders), inline=False)

        # --- General Section ---
        embed.add_field(name="📂 General", value="────────────────────", inline=False)
        embed.add_field(
            name="Total entries (all tables)",
            value=str(total_creators + total_layouts + total_collabs + total_musics + total_artists),
            inline=True
        )
        embed.add_field(name="Last update", value=last_update, inline=False)

        embed.set_footer(text="Gameplay Database • All stats")
        embed.set_thumbnail(url=self.bot.user.avatar)

        await interaction.followup.send(embed=embed)






    

            
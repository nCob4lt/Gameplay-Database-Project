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
import json
import os, sys
from pathlib import Path

# --- Local imports
import database
from utilities.applogger import AppLogger
from utilities import recovery
from utilities import tools
from views.paginator import PaginatorView

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from meta.constants import *

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

    @tasks.loop(hours=1)
    async def sync(self):

        """

        Periodic synchronization task.

        Runs every hour to enqueue the `synchronize_data` function into
        the database's asynchronous task queue, ensuring all live data is kept in sync.

        """
        await database.database_queue.put((database.synchronize_data, (), {}))

    @discord.app_commands.command(name="sync", description="Synchronize all data across the database (debug only)")
    async def manual_sync(self, interaction: discord.Interaction):

        await interaction.response.defer()

        await tools.check_mod(interaction)
        await database.database_queue.put((database.synchronize_data, (), {}))
        applogger.debug_command(interaction)
        await interaction.followup.send("**References** synchronized, and **stats** updated.")


    @tasks.loop(hours=6)
    async def save(self):

        """

        Periodic save task.

        Runs every 6 hours to trigger an automatic database backup using the
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
        if interaction.user.id != 724565148655681587:
            return await interaction.response.send_message("Bro tf are you doing rn")
        applogger.debug_command(interaction)
        recovery.load_save(filename)
        await interaction.response.send_message("Backup **successfully** loaded.")

    @discord.app_commands.command(
        name="database_stats",
        description="Display a database dashboard with stats"
    )
    async def database_stats(self, interaction: discord.Interaction):

        """
        Display a comprehensive database dashboard with statistics.

        This command fetches and aggregates key metrics from the Gameplay Database,
        including creators, musics, artists, layouts, collabs, and parts. The results
        are presented in a structured Discord embed with categorized sections.

        Statistics provided:
            - Creators: total number, layouts registered, collab participations,
            and top 5 most active creators.
            - Musics & Artists: total counts, top 5 musics by uses, top 5 artists by song usage,
            and musics missing links.
            - Layouts & Collabs: total counts, layout types (Experimental/Normal),
            registered vs. expected parts, and average builders per collab.
            - General: total entries across all tables and the date of the last layout registration.

        The command handles database errors gracefully and logs all interactions
        via the application logger.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object representing the user's slash command invocation.

        Returns
        -------
        None
            Sends a Discord embed as a response containing the aggregated statistics.
        """

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

        embed = discord.Embed(
            title="📊 Gameplay Database Statistics",
            color=discord.Color.dark_blue(),
            description="Advanced dashboard of the database with nerdy stats"
        )

        embed.add_field(name="💠 Creators", value="────────────────────", inline=False)
        embed.add_field(name="Total creators", value=str(total_creators), inline=False)
        embed.add_field(name="Layouts by creators", value=str(total_layouts_by_creators), inline=False)
        embed.add_field(name="Collab participations", value=str(total_collabs_by_creators), inline=False)
        embed.add_field(
            name="Top 5 active creators",
            value="\n".join([f"{c[0]} ({c[1]} levels)" for c in top_creators]) or "N/A",
            inline=False
        )

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
        applogger.debug_command(interaction)

    @discord.app_commands.command(
        name="missing",
        description="Display all missing data detected during the last database synchronization."
    )
    async def missing(self, interaction: discord.Interaction):

        """
        Display a report of all missing database entries detected during the last synchronization.

        This command reads the `missing_entries.json` file generated during the
        most recent database synchronization and presents the missing data in a
        structured Discord embed. The report includes missing entries for layouts,
        collabs, musics, creators, and artists, along with error details for each
        entry. A summary field shows the total number of missing entries.

        If the JSON file is not found or cannot be read, the command informs
        the user appropriately.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object representing the user's slash command invocation.

        Returns
        -------
        None
            Sends a Discord embed listing missing entries and a summary of total missing items.
        """
        await interaction.response.defer(thinking=True)

        json_path = Path(__file__).parent.parent.parent / "missing" / "missing_entries.json"

        if not os.path.exists(json_path):
            await interaction.followup.send("No `missing_entries.json` file found. Wait for the synchronization to run first.")
            return

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            await interaction.followup.send(f"Failed to read JSON file: `{e}`")
            return

        embed = discord.Embed(
            title="📋 Missing Database Entries",
            description="Here are all missing entries detected during the last database synchronization.",
            color=discord.Color.dark_grey()
        )
        embed.set_thumbnail(url=self.bot.user.avatar)

        total_missing = 0


        def format_section(section_name, entries):
            nonlocal total_missing
            total_missing += len(entries)
            if not entries:
                return "No issues found."
            return "\n".join([
                f"• ID `{e.get('id', '?')}` | `{e.get('name', '?')}` — **{e.get('missing', 'Unknown')}** *(Error: {e.get('error', 'N/A')})*"
                for e in entries[:10]
            ]) + (f"\n…and {len(entries) - 10} more." if len(entries) > 10 else "")

        for section in ["layout", "collab", "music", "creator", "artist"]:
            formatted = format_section(section, data.get(section, []))
            embed.add_field(
                name=f"{section.capitalize()} ({len(data.get(section, []))})",
                value=formatted,
                inline=False
            )

        embed.add_field(
            name="Summary",
            value=f"**Total missing entries:** {total_missing}",
            inline=False
        )

        embed.set_footer(text="Gameplay Database • Missing Data Report")

        await interaction.followup.send(embed=embed)
        applogger.debug_command(interaction)


    @discord.app_commands.command(
        name="about",
        description="Shows general information about the Gameplay Database project"
    )
    async def about(self, interaction: discord.Interaction):

        """
        Display general information about the Gameplay Database bot.

        This command sends a rich Discord embed summarizing the project,
        including version information, Python version, developer name,
        Discord.py library version, bot latency, number of servers and users,
        GitHub repository link, and bot invite link.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object representing the user's slash command invocation.

        Returns
        -------
        None
            Sends a Discord embed with project information.
        """
        embed = discord.Embed(
            title=f"📘 About {PROJECT_NAME}",
            description="A structured database project for layouts, collabs, and musics in Geometry Dash.",
            color=DEFAULT_COLOR
        )

        embed.add_field(name="Version", value=VERSION)
        embed.add_field(name="Python version", value=PYTHON_VERSION)
        embed.add_field(name="Developer", value=AUTHOR)
        embed.add_field(name="Discord.py", value=discord.__version__)
        embed.add_field(name="Bot latency", value=f"{round(self.bot.latency * 1000)} ms")
        embed.add_field(name="Total servers", value=f"{len(self.bot.guilds)}", inline=True)
        embed.add_field(name="Registered users", value=len(self.bot.users), inline=True)
        embed.add_field(name="GitHub", value=f"[Repository]({GITHUB_URL})")
        embed.add_field(name="Invite me", value=f"[Add to your server]({BOT_INVITE})")

        embed.set_thumbnail(url=self.bot.user.avatar)
        embed.set_footer(text=f"{PROJECT_NAME} • Stable Build", icon_url=self.bot.user.avatar)

        await interaction.response.send_message(embed=embed)


    @discord.app_commands.command(
    name="help",
    description="Display all bot commands grouped by category"
    )
    async def help(self, interaction: discord.Interaction):

        """
        Display a categorized overview of all available bot commands.

        This command generates paginated Discord embeds grouping commands by category:
        - Retrieving individual objects
        - Retrieving lists of objects
        - Registration requests
        - General commands
        - Moderation actions

        Each embed lists commands with their descriptions, and pagination buttons allow
        users to navigate through different categories.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object representing the user's slash command invocation.

        Returns
        -------
        None
            Sends the first embed with a paginated view for browsing all commands.
        """

        embeds = []

        groups = {
            "📝 Retrieving object": [
                ("/get_artist_by_name", "Retrieve an artist by name"),
                ("/get_collab_by_name", "Retrieve a collab by name"),
                ("/get_creator_by_discord", "Retrieve a creator by discord username"),
                ("/get_creator_by_name", "Retrieve a creator by name"),
                ("/get_layout_by_name", "Retrieve a layout by name"),
                ("/get_music_by_name", "Retrieve a music by name"),
                ("/get_random_layout", "Retrieve a random layout from the database")
            ],
            "📋 Retrieving list of objects": [
                ("/layouts_from", "List layouts from a creator"),
                ("/layouts_with", "List layouts using a specific music or artist"),
                ("/levels_from", "List layouts and collabs from a creator"),
                ("/levels_with", "List all levels (layouts + collabs) using a music or artist"),
                ("/collabs_from", "List collabs from a creator"),
                ("/collabs_with", "List collabs using a specific music or artist"),
                ("/musics_from", "List musics registered from an artist"),
                ("/parts_from", "List parts created by a creator"),
                ("/parts_of", "List parts associated with a layout or collab")
            ],
            "🛠 Registration/update requests": [
                ("/request_artist", "Request the registration of an artist"),
                ("/request_collab", "Request the registration of a collab"),
                ("/request_creator", "Request the registration of a creator"),
                ("/request_layout", "Request the registration of a layout"),
                ("/request_music", "Request the registration of a music"),
                ("/request_update_creator", "Request the update of a creator entry"),
                ("/request_update_layout", "Request the update of a layout entry"),
                ("/request_update_collab", "Request the update of a collab entry"),
                ("/request_update_music", "Request the update of a music entry"),
                ("/request_update_artist", "Request the update of a artist entry")
            ],
            "ℹ️ General": [
                ("/about", "Information about the bot"),
                ("/missing", "Show missing references in the database"),
                ("/database_stats", "Show statistics about the database")
            ],
            "🔧 Mod actions": [
                ("/add_artist", "Add a new artist to the database"),
                ("/add_collab", "Add a new collab to the database"),
                ("/add_creator", "Add a new creator to the database"),
                ("/add_layout", "Add a new layout to the database"),
                ("/add_music", "Add a new music to the database"),
                ("/update_creator", "Update infos about a creator"),
                ("/update_layout", "Update infos about a layout"),
                ("/update_collab", "Update infos about a collab"),
                ("/update_music", "Update infos about a music"),
                ("/update_artist", "Update infos about a artist"),
                ("/review_next_request", "Review the next pending registration request")
            ]
        }

        total_pages = len(groups)
        for idx, (group_name, commands) in enumerate(groups.items(), start=1):
            embed = discord.Embed(
                title=group_name,
                description=f"**{len(commands)} command(s)** in this category",
                color=discord.Color.blurple()
            )

            for cmd_name, cmd_desc in commands:
                embed.add_field(
                    name=f"> {cmd_name}",
                    value=f"_{cmd_desc}_",
                    inline=False
                )

            embed.set_footer(
                text=f"{PROJECT_NAME} - Page {idx}/{total_pages} | Use buttons to navigate",
                icon_url=self.bot.user.avatar
            )
            embed.set_thumbnail(url=self.bot.user.avatar)
            embeds.append(embed)

        view = PaginatorView(embeds, interaction.user)
        applogger.debug_command(interaction)
        await interaction.response.send_message(embed=embeds[0], view=view)








    

            
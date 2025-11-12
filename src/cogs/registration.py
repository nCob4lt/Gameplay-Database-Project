"""

File: registration.py

Description: This module defines the `RegistrationCog` class, a Discord cog that allows authorized moderators
to directly insert new records (creators, layouts, collabs, music tracks, and artists) into the Gameplay Database.

Each command performs the following actions:
    - Checks moderator permissions using `tools.check_mod()`
    - Queues an async task to the `database.database_queue` for safe, thread-safe database insertion
    - Logs the command execution through `AppLogger`
    - Returns a confirmation embed to the moderator within Discord

All database operations are asynchronous and rely on the global worker queue defined in `database.py`.

Author: cobalt

"""

# --- Standard imports ---
import discord
from discord.ext import commands
import sqlite3

# --- Local imports ---
import database
from utilities.applogger import AppLogger
from utilities import tools
from exceptions.custom_exceptions import *

# --- Initialization section ---
connection = sqlite3.connect("data/gpdb.db")
c = connection.cursor()
database.initialize()
connection.commit()
connection.close()

applogger = AppLogger()

class RegistrationCog(commands.Cog):

    """

    A Discord Cog providing moderator-only commands to directly register new data entries.

    This cog allows moderators to add new creators, layouts, collaborations, music tracks, and artists
    into the database without needing a manual approval process.

    Attributes
    ----------
    bot : commands.Bot
        The Discord bot instance associated with this cog.

    """

    def __init__(self, bot: commands.Bot) -> None:

        """Initialize the RegistrationCog with a reference to the bot."""

        self.bot = bot

    @discord.app_commands.command(name="add_creator", description="Adds directly a creator and its info into the database (prior confirmation)")
    @discord.app_commands.describe(user="Creator username (String or discord mention expected (always prioritize discord mention))")
    @discord.app_commands.describe(nationality="Creator nationality (prior confirmation)")
    @discord.app_commands.describe(gdusername="Creator's in-game username")
    @discord.app_commands.describe(yt="Youtube link to their channel (leave blank if none)")
    async def add_creator(self, interaction: discord.Interaction, user: str, nationality: str, gdusername: str, yt: str = None):

        """

        Add a new creator entry to the database.

        Parameters
        ----------
        interaction : discord.Interaction
            The Discord interaction representing the slash command invocation.
        user : discord.User
            The creator's Discord user object.
        nationality : str
            The creator's nationality.
        yt : str, optional
            A YouTube channel link (if available).

        """

        await tools.check_mod(interaction)
            
        # Try to resolve mention into a discord.User
        resolved_user = await tools.resolve_user(user, interaction)

        if isinstance(resolved_user, (discord.User, discord.Member)):
            username = resolved_user.global_name
            discord_uname = resolved_user.name
            discord_uid = resolved_user.id
        else:
            username = resolved_user
            discord_uname = None
            discord_uid = None

        registrator = interaction.user.name

       
        await database.database_queue.put((
            database.register_creator,
            (username, nationality, discord_uname, discord_uid, yt, gdusername, registrator), {}
        ))


        embed = discord.Embed(
                title="Registration (mod action)",
                description="User successfully registered",
                color=discord.Color.dark_grey()
            )
        
        embed.add_field(name="Username", value=username, inline=False)
        embed.add_field(name="Nationality", value=nationality, inline=False)
        embed.add_field(name="Discord username", value=discord_uname, inline=False)
        embed.add_field(name="Youtube", value=f"[Open in browser]({yt})" if yt else None, inline=False)
        embed.add_field(name="GD Username", value=gdusername, inline=False)

        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text="Gameplay Database", icon_url=self.bot.user.avatar)
        embed.set_thumbnail(url=self.bot.user.avatar)

        applogger.debug_command(interaction)
        await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(
        name="add_layout",
        description="Adds directly a layout and its info into the database (prior confirmation)"
    )
    @discord.app_commands.describe(
        creator="Creator of the layout (mention (always prioritize discord mention) or name)",
        name="Name of the layout",
        length="Length of the layout",
        yt="YouTube link of the layout",
        music_name="Name of the music used",
        music_artist="Name of the artist that created the music",
        music_ngid="Newgrounds ID of the music (leave blank if unavailable)",
        type="Type of gameplay used/represented (speedcore, atmospheric, flow, etc.)",
        igid="In-game ID of the layout (leave blank if not on servers)",
        masterlevel="The collab this layout belongs to (leave blank if none)",
        recorder_notes="Write anything you want about this layout right here"
    )
    async def add_layout(
        self,
        interaction: discord.Interaction,
        creator: str,
        name: str,
        length: str,
        yt: str,
        music_name: str,
        music_artist: str,
        music_ngid: int = None,
        type: str = None,
        igid: int = None,
        masterlevel: str = None,
        recorder_notes: str = None
    ):
        """
        Adds a new layout entry to the database.

        This command registers a new gameplay layout and links it with its creator, 
        music, and metadata. It accepts either a Discord mention, an ID, or a plain 
        text name for the creator field.
        """

        await tools.check_mod(interaction)


        try:
            await tools.is_valid_duration(length)
        except InvalidDurationFormat:
            await interaction.response.send_message(
                "**Invalid** duration format. Correct format: __**x**h**y**min**z**s__"
            )
            applogger.error(
                f"Invalid duration format on {interaction.command.name} ran by {interaction.user.name} in {interaction.guild.name}"
            )
            return

        resolved_creator = await tools.resolve_user(creator, interaction)
        registrator = interaction.user.name

        if isinstance(resolved_creator, (discord.User, discord.Member)):
            creator_name = str(resolved_creator.global_name)
        else:
            creator_name = str(resolved_creator)

        await database.database_queue.put((
            database.register_layout,
            (
                creator_name,
                name,
                length,
                yt,
                music_name,
                music_artist,
                music_ngid,
                type,
                igid,
                masterlevel,
                recorder_notes,
                registrator,
            ),
            {}
        ))

        # Création de l’embed
        embed = discord.Embed(
            title="Registration (mod action)",
            description="Layout successfully registered",
            color=discord.Color.dark_grey()
        )

        embed.add_field(name="Creator", value=creator_name, inline=False)
        embed.add_field(name="Name", value=name, inline=False)
        embed.add_field(name="Length", value=length, inline=False)
        embed.add_field(name="YouTube link", value=f"[Open in browser]({yt})" if yt else "None", inline=False)
        embed.add_field(name="Music name", value=music_name, inline=False)
        embed.add_field(name="Music artist", value=music_artist, inline=False)
        embed.add_field(name="Music NG ID", value=music_ngid or "None", inline=False)
        embed.add_field(name="Type", value=type or "None", inline=False)
        embed.add_field(name="In-game ID", value=igid or "None", inline=False)
        embed.add_field(name="Masterlevel", value=masterlevel or "None", inline=False)
        embed.add_field(name="Recorder notes", value=recorder_notes or "None", inline=False)
        embed.add_field(name="Recorder name", value=registrator, inline=False)

        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text="Gameplay Database", icon_url=self.bot.user.avatar)
        embed.set_thumbnail(url=self.bot.user.avatar)

        applogger.debug_command(interaction)
        await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(
        name="add_collab",
        description="Adds directly a collab and its info into the database (prior confirmation)"
    )
    @discord.app_commands.describe(
        host="Collab host (mention (always prioritize discord mention) or name)",
        name="Name of the collab",
        builders_number="Number of builders that participated in the collab",
        length="Length of the collab",
        yt="YouTube link of the collab",
        music_name="Name of the music used",
        music_artist="Name of the artist that created the music",
        music_ngid="Newgrounds ID of the music (leave blank if unavailable)",
        igid="In-game ID of the collab (leave blank if not on servers)",
        recorder_notes="Write anything you want about this collab right here"
    )
    async def add_collab(
        self, 
        interaction: discord.Interaction, 
        host: str, 
        name: str, 
        builders_number: int, 
        length: str, 
        yt: str, 
        music_name: str, 
        music_artist: str, 
        music_ngid: int = None, 
        igid: int = None, 
        recorder_notes: str = None
    ):
        """
        Adds a new collaboration entry to the database.

        This command registers a collab (a multi-creator layout) and associates it
        with its host, music, and metadata. It accepts a Discord mention, ID, or plain
        string for the `host` field.
        """

        await tools.check_mod(interaction)

        # Validate the duration format
        try:
            await tools.is_valid_duration(length)
        except InvalidDurationFormat:
            await interaction.response.send_message(
                "**Invalid** duration format. Correct format: __**x**h**y**min**z**s__"
            )
            applogger.error(
                f"Invalid duration format on {interaction.command.name} run by {interaction.user.name} in {interaction.guild.name}"
            )
            return

        # Resolve host (mention / ID / string)
        resolved_host = await tools.resolve_user(host, interaction)
        registrator = interaction.user.name

        if isinstance(resolved_host, (discord.User, discord.Member)):
            host_name = str(resolved_host.global_name)
        else:
            host_name = str(resolved_host)

        # Add to database queue
        await database.database_queue.put((
            database.register_collab,
            (
                host_name,
                name,
                builders_number,
                length,
                yt,
                music_name,
                music_artist,
                music_ngid,
                igid,
                registrator,
                recorder_notes,
            ),
            {}
        ))

        # Build confirmation embed
        embed = discord.Embed(
            title="Registration (mod action)",
            description="Collab successfully registered",
            color=discord.Color.dark_grey()
        )

        embed.add_field(name="Host", value=host_name, inline=False)
        embed.add_field(name="Name", value=name, inline=False)
        embed.add_field(name="Builders number", value=builders_number, inline=False)
        embed.add_field(name="Length", value=length, inline=False)
        embed.add_field(name="YouTube link", value=f"[Open in browser]({yt})" if yt else "None", inline=False)
        embed.add_field(name="Music name", value=music_name, inline=False)
        embed.add_field(name="Music artist", value=music_artist, inline=False)
        embed.add_field(name="Music NG ID", value=music_ngid or "None", inline=False)
        embed.add_field(name="In-game ID", value=igid or "None", inline=False)
        embed.add_field(name="Recorder notes", value=recorder_notes or "None", inline=False)
        embed.add_field(name="Recorder name", value=registrator, inline=False)

        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text="Gameplay Database", icon_url=self.bot.user.avatar)
        embed.set_thumbnail(url=self.bot.user.avatar)

        applogger.debug_command(interaction)
        await interaction.response.send_message(embed=embed)


    @discord.app_commands.command(name="add_music", description="Adds directly a music track and its info into the database (prior confirmation)")
    @discord.app_commands.describe(name="Name of the music")
    @discord.app_commands.describe(artist="Artist who created the music")
    @discord.app_commands.describe(length="Length of the music")
    @discord.app_commands.describe(type="Type/genre of the music (leave blank if unsure)")
    @discord.app_commands.describe(yt="Youtube link of the music")
    @discord.app_commands.describe(soundcloud="SoundCloud link of the music (leave blank if unavailable)")
    @discord.app_commands.describe(ngid="Newgrounds ID of the music (leave blank if unavailable)")
    @discord.app_commands.describe(recorder_notes="Write anything you want about this music right here")
    async def add_music(
        self,
        interaction: discord.Interaction,
        name: str,
        artist: str,
        length: str,
        type: str = None,
        yt: str = None,
        soundcloud: str = None,
        ngid: int = None,
        recorder_notes: str = None):

        """

        Add a music track entry to the database.

        Stores information about a music track used in levels or collabs, including metadata and sources.

        """
        
        await tools.check_mod(interaction)
        try:
            await tools.is_valid_duration(length)
        except InvalidDurationFormat:
            await interaction.response.send_message("**Invalid** duration format. Corrrect format : __**x**h**y**min**z**s__")
            applogger.error(f"Invalid duration format on {interaction.command.name} ran by {interaction.user.name} in {interaction.guild.name}")
            return

        registrator = interaction.user.name
        await database.database_queue.put((database.register_music,
                                            (name, artist, length, type, yt, soundcloud, ngid, registrator, recorder_notes,),
                                              {}))

        embed = discord.Embed(
            title="Registration (mod action)",
            description="Music successfully registered",
            color=discord.Color.dark_grey()
        )

        embed.add_field(name="Name", value=name, inline=False)
        embed.add_field(name="Artist", value=artist, inline=False)
        embed.add_field(name="Length", value=length, inline=False)
        embed.add_field(name="Type", value=type, inline=False)
        embed.add_field(name="Youtube link", value=f"[Open in browser]({yt})" if yt else "None", inline=False)
        embed.add_field(name="SoundCloud link", value=f"[Open in browser]({soundcloud})" if soundcloud else "None", inline=False)
        embed.add_field(name="Newgrounds ID", value=ngid, inline=False)
        embed.add_field(name="Recorder notes", value=recorder_notes, inline=False)
        embed.add_field(name="Recorder name", value=registrator, inline=False)

        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text="Gameplay Database", icon_url=self.bot.user.avatar)
        embed.set_thumbnail(url=self.bot.user.avatar)

        applogger.debug_command(interaction)
        await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="add_artist", description="Adds directly an artist and its info into the database (prior confirmation)")
    @discord.app_commands.describe(name="Name of the artist")
    @discord.app_commands.describe(yt="Youtube link of the artist (leave blank if unavailable)")
    @discord.app_commands.describe(soundcloud="SoundCloud link of the artist (leave blank if unavailable)")
    @discord.app_commands.describe(recorder_notes="Write anything you want about this artist right here")
    async def add_artist(
        self,
        interaction: discord.Interaction,
        name: str,
        yt: str = None,
        soundcloud: str = None,
        recorder_notes: str = None):

        """

        Add an artist entry to the database.

        Registers a new artist profile, typically associated with one or more music tracks.

        """

        await tools.check_mod(interaction)
        
        registrator = interaction.user.name

        await database.database_queue.put((database.register_artist,
                                            (name, yt, soundcloud, registrator, recorder_notes,),
                                              {}))

        embed = discord.Embed(
            title="Registration (mod action)",
            description="Artist successfully registered",
            color=discord.Color.dark_grey()
        )

        embed.add_field(name="Name", value=name, inline=False)
        embed.add_field(name="Youtube link", value=f"[Open in browser]({yt})" if yt else "None", inline=False)
        embed.add_field(name="Soundcloud link", value=f"[Open in browser]({soundcloud})" if soundcloud else "None", inline=False)
        embed.add_field(name="Songs registered", value=0, inline=False)
        embed.add_field(name="Total song uses", value=0, inline=False)
        embed.add_field(name="Recorder notes", value=recorder_notes, inline=False)
        embed.add_field(name="Recorder name", value=registrator, inline=False)

        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text="Gameplay Database", icon_url=self.bot.user.avatar)
        embed.set_thumbnail(url=self.bot.user.avatar)

        applogger.debug_command(interaction)
        await interaction.response.send_message(embed=embed)







    
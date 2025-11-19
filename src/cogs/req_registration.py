import discord
from discord.ext import commands

import database
from utilities.applogger import AppLogger
from utilities import tools
from exceptions.custom_exceptions import *

applogger = AppLogger()

class RequestRegistrationCog(commands.Cog):

    """

    Cog responsible for handling user-submitted registration requests
    for new entries in the Gameplay Database (creators, layouts, collabs, music, artists).
    
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(
        name="request_creator",
        description="Registers a suggestion entry for the creator table in the Gameplay Database"
    )
    @discord.app_commands.describe(
        user="Discord user to request registration (mention (always prioritize discord mention) or plain name)",
        nationality="User's nationality",
        gdusername="Creator's in-game username",
        yt="Youtube link to their channel (optional)"
    )
    async def request_creator(
        self,
        interaction: discord.Interaction,
        user: str,
        nationality: str,
        gdusername: str,
        yt: str = None
    ):
        
        """
        Handles the registration request of a new creator into the database.
        Can take a Discord mention, a raw ID, or a plain text username.
        """

        await tools.check_mod(interaction)

        resolved_user = await tools.resolve_user(user, interaction)
        registrator = interaction.user.name

        if isinstance(resolved_user, (discord.User, discord.Member)):
            username = resolved_user.global_name or resolved_user.name
            discord_uname = resolved_user.name
            discord_uid = resolved_user.id
        else:
            username = resolved_user
            discord_uname = "N/A"
            discord_uid = None

        await database.database_queue.put((
            database.register_request_creator,
            (username, nationality, discord_uname, discord_uid, yt, gdusername, registrator),
            {}
        ))

        embed = discord.Embed(
            title="Registration request sent",
            description="Your request has been successfully sent.",
            color=discord.Color.dark_grey()
        )

        embed.add_field(name="Username", value=username, inline=False)
        embed.add_field(name="Nationality", value=nationality, inline=False)
        embed.add_field(name="Discord username", value=discord_uname, inline=False)
        embed.add_field(name="YouTube", value=f"[Open in browser]({yt})" if yt else "None", inline=False)
        embed.add_field(name="Recorder name", value=registrator, inline=False)

        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text="Gameplay Database", icon_url=self.bot.user.avatar)
        embed.set_thumbnail(url=self.bot.user.avatar)

        applogger.debug_command(interaction)
        await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(
        name="request_layout",
        description="Registers a suggestion entry for the layout table in the Gameplay Database"
    )
    @discord.app_commands.describe(
        creator="Creator of the layout (mention (always prioritize discord mention) or name)",
        type_="Layout type (e.g., experimental, speedcore, atmospheric, etc.)",
        name="Layout name",
        length="Length (XminYs e.g., 14s, 1min2s, 2min45s)",
        yt="YouTube link to the layout",
        music_ngid="Newgrounds ID of the song used",
        music_name="Name of the music",
        music_artist="Artist of the music",
        igid="In-game ID (if available)",
        masterlevel="The collab the part belongs to, if it is one, if not, leave blank",
        recorder_notes="Any notes about the recording"
    )
    async def request_layout(
        self,
        interaction: discord.Interaction,
        creator: str,
        name: str,
        length: str,
        yt: str,
        music_name: str,
        music_artist: str,
        music_ngid: str = None,
        type_: str = None,
        igid: str = None,
        masterlevel: str = None,
        recorder_notes: str = None
    ):
        """
        Registers a layout request into the database.

        This command lets any user suggest a layout entry. The `creator` field accepts
        a Discord mention, an ID, or a plain string.
        """
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

        # Resolve the creator field
        resolved_creator = await tools.resolve_user(creator, interaction)
        if isinstance(resolved_creator, (discord.User, discord.Member)):
            creator_name = str(resolved_creator.global_name)
        else:
            creator_name = str(resolved_creator)

        registrator = interaction.user.name

        # Register to database
        await database.database_queue.put((
            database.register_request_layout,
            (creator_name, type_, name, length, yt, music_ngid, music_name, music_artist, igid, masterlevel, recorder_notes, registrator),
            {}
        ))

        # Confirmation embed
        embed = discord.Embed(
            title="Registration request sent",
            description="Your layout request has been successfully submitted.",
            color=discord.Color.dark_grey()
        )
        embed.add_field(name="Name", value=name, inline=False)
        embed.add_field(name="Creator", value=creator_name, inline=False)
        embed.add_field(name="Type", value=type_ or "None", inline=False)
        embed.add_field(name="Length", value=length, inline=False)
        embed.add_field(name="YouTube", value=f"[Open in browser]({yt})" if yt else "None", inline=False)
        embed.add_field(name="Music", value=f"{music_name} by {music_artist}", inline=False)
        embed.add_field(name="NG ID", value=music_ngid or "None", inline=False)
        embed.add_field(name="In-game ID", value=igid or "None", inline=False)
        embed.add_field(name="Masterlevel", value=masterlevel or "None", inline=False)
        embed.add_field(name="Recorder name", value=registrator, inline=False)
        embed.add_field(name="Recorder notes", value=recorder_notes or "None", inline=False)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text="Gameplay Database", icon_url=self.bot.user.avatar)
        embed.set_thumbnail(url=self.bot.user.avatar)

        applogger.debug_command(interaction)
        await interaction.response.send_message(embed=embed)


    @discord.app_commands.command(
        name="request_collab",
        description="Registers a suggestion entry for the collab table in the Gameplay Database"
    )
    @discord.app_commands.describe(
        host="Host of the collab (mention (always prioritize discord mention) or name)",
        name="Collab name",
        builders_number="Number of builders",
        length="Length of the collab",
        yt="YouTube link of the collab",
        music_ngid="Newgrounds ID of the music used",
        music_name="Name of the music",
        music_artist="Artist of the music",
        igid="In-game ID",
        recorder_notes="Notes about the collab"
    )
    async def request_collab(
        self,
        interaction: discord.Interaction,
        host: str,
        name: str,
        builders_number: int,
        length: str,
        yt: str,
        music_name: str,
        music_artist: str,
        music_ngid: str = None,
        igid: str = None,
        recorder_notes: str = None
    ):
        """
        Registers a collab request into the database.

        Accepts a Discord mention, ID, or plain string for the `host` field.
        """
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

        # Resolve the host field
        resolved_host = await tools.resolve_user(host, interaction)
        if isinstance(resolved_host, (discord.User, discord.Member)):
            host_name = str(resolved_host.global_name)
        else:
            host_name = str(resolved_host)

        registrator = interaction.user.name

        # Register to database
        await database.database_queue.put((
            database.register_request_collab,
            (host_name, name, builders_number, length, yt, music_ngid, music_name, music_artist, igid, recorder_notes, registrator),
            {}
        ))

        # Confirmation embed
        embed = discord.Embed(
            title="Registration request sent",
            description="Your collab request has been successfully submitted.",
            color=discord.Color.dark_grey()
        )
        embed.add_field(name="Name", value=name, inline=False)
        embed.add_field(name="Host", value=host_name, inline=False)
        embed.add_field(name="Builders", value=builders_number, inline=False)
        embed.add_field(name="Length", value=length, inline=False)
        embed.add_field(name="YouTube", value=f"[Open in browser]({yt})" if yt else "None", inline=False)
        embed.add_field(name="Music", value=f"{music_name} by {music_artist}", inline=False)
        embed.add_field(name="NG ID", value=music_ngid or "None", inline=False)
        embed.add_field(name="In-game ID", value=igid or "None", inline=False)
        embed.add_field(name="Recorder name", value=registrator, inline=False)
        embed.add_field(name="Recorder notes", value=recorder_notes or "None", inline=False)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text="Gameplay Database", icon_url=self.bot.user.avatar)
        embed.set_thumbnail(url=self.bot.user.avatar)

        applogger.debug_command(interaction)
        await interaction.response.send_message(embed=embed)


    @discord.app_commands.command(
        name="request_music",
        description="Registers a suggestion entry for the music table in the Gameplay Database"
    )
    @discord.app_commands.describe(
        name="Music name",
        artist="Music artist",
        length="Duration or format",
        type_="Music type (e.g., NG, YT, SC)",
        yt="YouTube link",
        soundcloud="SoundCloud link",
        ngid="Newgrounds ID",
        recorder_notes="Additional notes"
    )
    async def request_music(
        self,
        interaction: discord.Interaction,
        name: str,
        artist: str,
        length: str,
        type_: str = None,
        yt: str = None,
        soundcloud: str = None,
        ngid: str = None,
        recorder_notes: str = None
    ):
        """

        Registers a music request.

        """

        try:
            await tools.is_valid_duration(length)
        except InvalidDurationFormat:
            await interaction.response.send_message("**Invalid** duration format. Corrrect format : __**x**h**y**min**z**s__")
            applogger.error(f"Invalid duration format on {interaction.command.name} ran by {interaction.user.name} in {interaction.guild.name}")
            return

        registrator = interaction.user.name

        await database.database_queue.put((
            database.register_request_music,
            (name, artist, length, type_, yt, soundcloud, ngid, recorder_notes, registrator),
            {}
        ))

        embed = discord.Embed(
            title="Registration request sent",
            description="Your music request has been successfully submitted.",
            color=discord.Color.dark_grey()
        )
        embed.add_field(name="Name", value=name, inline=False)
        embed.add_field(name="Artist", value=artist, inline=False)
        embed.add_field(name="Length", value=length, inline=False)
        embed.add_field(name="Type", value=type_, inline=False)
        embed.add_field(name="YouTube", value=f"[Open in browser]({yt})" if yt else "None", inline=False)
        embed.add_field(name="SoundCloud", value=f"[Open in browser]({soundcloud})" if soundcloud else "None", inline=False)
        embed.add_field(name="NG ID", value=ngid, inline=False)
        embed.add_field(name="Recorder notes", value=recorder_notes or "None", inline=False)
        embed.add_field(name="Recorder name", value=registrator, inline=False)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text="Gameplay Database", icon_url=self.bot.user.avatar)
        embed.set_thumbnail(url=self.bot.user.avatar)

        applogger.debug_command(interaction)
        await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(
        name="request_artist",
        description="Registers a suggestion entry for the artist table in the Gameplay Database"
    )
    @discord.app_commands.describe(
        name="Artist name",
        yt="YouTube link of the artist",
        soundcloud="SoundCloud link of the artist",
        recorder_notes="Additional notes about the artist"
    )
    async def request_artist(
        self,
        interaction: discord.Interaction,
        name: str,
        yt: str = None,
        soundcloud: str = None,
        recorder_notes: str = None
    ):
        """

        Registers an artist request.

        """

        registrator = interaction.user.name

        await database.database_queue.put((
            database.register_request_artist,
            (name, yt, soundcloud, recorder_notes, registrator),
            {}
        ))

        embed = discord.Embed(
            title="Registration request sent",
            description="Your artist request has been successfully submitted.",
            color=discord.Color.dark_grey()
        )
        embed.add_field(name="Name", value=name, inline=False)
        embed.add_field(name="YouTube", value=f"[Open in browser]({yt})" if yt else "None", inline=False)
        embed.add_field(name="SoundCloud", value=f"[Open in browser]({soundcloud})" if soundcloud else "None", inline=False)
        embed.add_field(name="Recorder notes", value=recorder_notes or "None", inline=False)
        embed.add_field(name="Recorder name", value=registrator, inline=False)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text="Gameplay Database", icon_url=self.bot.user.avatar)
        embed.set_thumbnail(url=self.bot.user.avatar)

        applogger.debug_command(interaction)
        await interaction.response.send_message(embed=embed)
            
        
"""
ListCog - Discord Bot Cog for Listing Gameplay Database Entries

This module contains the ListCog class, which provides a set of Discord
slash commands to retrieve and display various objects stored in the
Gameplay Database. The cog handles layouts, collabs, music, and parts,
supporting both individual retrieval and paginated listings.

Commands included:

- Layouts:
    /layouts_from      - List layouts created by a specific creator
    /layouts_with      - List layouts using a specific music or artist
    /levels_from       - List all layouts and collabs from a creator
    /levels_with       - List all layouts and collabs using a music or artist

- Collabs:
    /collabs_from      - List collabs hosted by a specific user
    /collabs_with      - List collabs using a specific music or artist

- Music:
    /musics_from       - List musics registered by a specific artist

- Parts:
    /parts_from        - List parts created by a specific user
    /parts_of          - List parts belonging to a specific collab

Features:
- Paginated embeds for large lists, using the PaginatorView class.
- Automatic formatting of names, creators/hosts, and YouTube links.
- Optional thumbnails for musics and collabs when YouTube links exist.
- Robust error handling with DataNotFound exceptions and logging via AppLogger.

Dependencies:
- discord.py (app_commands & ui components)
- database module for SQL queries
- utilities.tools for YouTube thumbnail/PP retrieval
- views.PaginatorView for paginated navigation

Author: Cobalt
"""

import discord
from discord.ext import commands

import database
from utilities.applogger import AppLogger
from exceptions.custom_exceptions import DataNotFound, InvalidYouTubeURL
from utilities import tools
from views.paginator import PaginatorView

applogger = AppLogger()

class ListCog(commands.Cog):

    """

    Cog responsible for retrieving and displaying layouts, collabs, musics, and parts
    from the Gameplay Database. Provides paginated views for large sets of results
    and handles error logging for missing or invalid data.

    """

    def __init__(self, bot: commands.Bot):

        """
        Initialize the cog with a reference to the bot.

        Parameters
        ----------
        bot : commands.Bot
            The Discord bot instance.
        """

        self.bot = bot

    @discord.app_commands.command(name="layouts_from", description="List the levels registered in the database from the given creator")
    async def layouts_from(self, interaction: discord.Interaction, user: discord.User):

        """
        List all layouts created by the specified creator.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object representing the command invocation.
        user : discord.User
            The creator whose layouts should be retrieved.

        Behavior
        --------
        - Retrieves layouts from the database using the creator's global name.
        - Paginates results with 10 items per page.
        - Sends the first page embed with a PaginatorView.

        Exceptions
        ----------
        DataNotFound
            Raised if no layouts exist for the given creator. Sends an ephemeral
            response and logs the event.
        """

        try:
            get = database.get_layouts_from(user.global_name)
        except DataNotFound:
            await interaction.response.send_message(f"No **levels** from {user.global_name}")
            applogger.error(f"Empty response on {interaction.command.name} used by {interaction.user.name} in {interaction.guild.name}")
            return

        embeds = []
        per_page = 10

        for i in range(0, len(get), per_page):
            chunk = get[i:i+per_page]
            fullstring = ""
            for level in chunk:
                fullstring += f"**{level['name']}** | [Open in browser]({level['yt']})\n"

            embed = discord.Embed(
                title=f"Levels created by {user.global_name}",
                description=f"Total : {len(get)} (Page {i//per_page + 1}/{(len(get) - 1)//per_page + 1})",
                color=discord.Color.dark_grey()
            )
            embed.add_field(name="List", value=fullstring, inline=False)
            embed.set_footer(text="Gameplay Database", icon_url=self.bot.user.avatar)
            embed.set_thumbnail(url=user.avatar)
            embeds.append(embed)

        view = PaginatorView(embeds, interaction.user)
        applogger.debug_command(interaction)
        await interaction.response.send_message(embed=embeds[0], view=view)


    @discord.app_commands.command(name="collabs_from", description="List the collabs registered in the database from the given host")
    async def collabs_from(self, interaction: discord.Interaction, user: discord.User):

        """
        List all collabs hosted by the given creator.

        Parameters
        ----------
        interaction : discord.Interaction
            The command interaction object.
        user : discord.User
            The creator whose collabs should be retrieved.

        Behavior
        --------
        - Retrieves collabs from the database by creator name.
        - Paginated embeds with 10 items per page.
        - Displays YouTube links if available.

        Exceptions
        ----------
        DataNotFound
            Raised if no collabs exist for the creator.
        """

        try:
            get = database.get_collabs_from(user.global_name)
        except DataNotFound:
            await interaction.response.send_message(f"No **collabs** from {user.global_name}")
            applogger.error(f"Empty response on {interaction.command.name}")
            return

        per_page = 10
        embeds = []
        for i in range(0, len(get), per_page):
            chunk = get[i:i+per_page]
            description = "\n".join(f"**{collab['name']}** | [Open in browser]({collab['yt']})" for collab in chunk)
            embed = discord.Embed(
                title=f"Collabs hosted by {user.global_name}",
                description=f"Total : {len(get)} (Page {i//per_page + 1}/{(len(get) - 1)//per_page + 1})",
                color=discord.Color.dark_grey()
            )
            embed.add_field(name="List", value=description, inline=False)
            embed.set_footer(text="Gameplay Database", icon_url=self.bot.user.avatar)
            embed.set_thumbnail(url=user.avatar)
            embeds.append(embed)

        applogger.debug_command(interaction)
        await interaction.response.send_message(embed=embeds[0], view=PaginatorView(embeds, interaction.user))

    @discord.app_commands.command(name="parts_from", description="List all collab parts built by the given creator")
    async def parts_from(self, interaction: discord.Interaction, user: discord.User):

        """
        List all parts of collabs built by the specified creator.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction representing the command invocation.
        user : discord.User
            The creator whose parts are being retrieved.

        Behavior
        --------
        - Retrieves collab parts from the database.
        - Shows the original collab for each part.
        - Paginated display with 10 items per page.

        Exceptions
        ----------
        DataNotFound
            Raised if the creator has no registered parts.
        """

        try:
            get = database.get_parts_from(user.global_name)
        except DataNotFound:
            await interaction.response.send_message(f"No **collab parts** from {user.global_name}")
            applogger.error(f"Empty response on {interaction.command.name}")
            return

        per_page = 10
        embeds = []
        for i in range(0, len(get), per_page):
            chunk = get[i:i+per_page]
            description = "\n".join(
                f"**{p['name']}** *(from {p['masterlevel'] or 'Unknown collab'})* | [Open in browser]({p['yt']})"
                for p in chunk
            )
            embed = discord.Embed(
                title=f"Collab parts built by {user.global_name}",
                description=f"Total : {len(get)} (Page {i//per_page + 1}/{(len(get) - 1)//per_page + 1})",
                color=discord.Color.dark_grey()
            )
            embed.add_field(name="List", value=description, inline=False)
            embed.set_footer(text="Gameplay Database", icon_url=self.bot.user.avatar)
            embed.set_thumbnail(url=user.avatar)
            embeds.append(embed)

        applogger.debug_command(interaction)
        await interaction.response.send_message(embed=embeds[0], view=PaginatorView(embeds, interaction.user))

            
    @discord.app_commands.command(
        name="musics_from",
        description="List the musics registered in the database from the given artist"
    )
    async def musics_from(self, interaction: discord.Interaction, artist: str):

        """
        List all music tracks registered under a given artist.

        Parameters
        ----------
        interaction : discord.Interaction
            The command interaction object.
        artist : str
            The artist's name to retrieve music from.

        Behavior
        --------
        - Retrieves music entries from the database.
        - Displays links to YouTube and SoundCloud when available.
        - Displays artist's YouTube profile picture as a thumbnail.
        - Paginated display with 10 items per page.

        Exceptions
        ----------
        DataNotFound
            Raised if no music exists for the specified artist.
        InvalidYouTubeURL
            Raised if the artist's YouTube link cannot be parsed to retrieve a thumbnail.
        """

        try:
            rows = database.get_musics_from(artist)
            musics = [dict(row) for row in rows]
        except DataNotFound:
            await interaction.response.send_message(f"No **musics** from {artist}")
            applogger.error(
                f"Empty response on {interaction.command.name} used by {interaction.user.name} in {interaction.guild.name}"
            )
            return

        per_page = 10
        embeds = []

        ytpp_url = None
        try:
            artist_rows = database.get_artist_by_name(artist)
            artist_data = dict(artist_rows[0])
            channel_api_id = tools.get_yt_channel_id(artist_data['yt'])
            ytpp_url = tools.get_youtube_pp(channel_api_id)
        except (DataNotFound, InvalidYouTubeURL, UnboundLocalError):
            applogger.warning(
                f"Failed to retrieve YouTube PP for {artist} on {interaction.command.name} ran by {interaction.user.name} in {interaction.guild.name}"
            )

        for i in range(0, len(musics), per_page):
            chunk = musics[i:i+per_page]
            fullstring = ""
            for music in chunk:
                yt_link = f"[YouTube]({music['yt']})" if music['yt'] else "YouTube : No link"
                sc_link = f"[SoundCloud]({music['soundcloud']})" if music['soundcloud'] else "SoundCloud : No link"
                fullstring += f"**{music['name']}**\n {yt_link} | {sc_link}\n"

            embed = discord.Embed(
                title=f"Musics from {artist}",
                description=f"Total: {len(musics)} (Page {i//per_page + 1}/{(len(musics) - 1)//per_page + 1})",
                color=discord.Color.dark_grey()
            )
            embed.add_field(name="List", value=fullstring, inline=False)
            embed.set_footer(text="Gameplay Database", icon_url=self.bot.user.avatar)
            if ytpp_url:
                embed.set_thumbnail(url=ytpp_url)

            embeds.append(embed)

        view = PaginatorView(embeds, interaction.user)
        applogger.debug_command(interaction)
        await interaction.response.send_message(embed=embeds[0], view=view)

    @discord.app_commands.command(
        name="levels_from",
        description="List every layout and collab registered in the database from the given creator"
    )
    async def levels_from(self, interaction: discord.Interaction, user: discord.User):

        """
        List all layouts and collabs created by a specific user.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object representing the command invocation.
        user : discord.User
            The creator whose levels (layouts + collabs) should be retrieved.

        Behavior
        --------
        - Retrieves all layouts and collabs for the specified creator.
        - Separates results into layouts and collabs for clarity.
        - Displays results in paginated embeds with 10 items per page.
        - Each embed contains the total number of levels and page number.

        Exceptions
        ----------
        DataNotFound
            Raised if no levels exist for the given creator.
        """

        try:
            all_levels = database.get_levels_from(user.global_name)
        except DataNotFound:
            await interaction.response.send_message(
                f"No **levels** (layouts or collabs) from {user.global_name}"
            )
            applogger.error(
                f"Empty response on {interaction.command.name} used by {interaction.user.name} in {interaction.guild.name}"
            )
            return

        if not all_levels:
            await interaction.response.send_message(
                f"No **levels** found for {user.global_name}"
            )
            return

        per_page = 10
        embeds = []

        for i in range(0, len(all_levels), per_page):
            chunk = all_levels[i:i + per_page]

            layouts = [lvl for lvl in chunk if lvl['type'] == 'layout']
            collabs = [lvl for lvl in chunk if lvl['type'] == 'collab']

            embed = discord.Embed(
                title=f"Levels from {user.global_name}",
                description=f"Total: {len(all_levels)} (Page {i//per_page + 1}/{(len(all_levels)-1)//per_page + 1})",
                color=discord.Color.dark_grey()
            )

            if layouts:
                layout_str = "\n".join(
                    f"**{lvl['name']}** | [Open in browser]({lvl['yt']})" for lvl in layouts
                )
                embed.add_field(name=f"Layouts ({len(layouts)})", value=layout_str, inline=False)

            if collabs:
                collab_str = "\n".join(
                    f"**{lvl['name']}** | [Open in browser]({lvl['yt']})" for lvl in collabs
                )
                embed.add_field(name=f"Collabs ({len(collabs)})", value=collab_str, inline=False)

            embed.set_footer(text="Gameplay Database", icon_url=self.bot.user.avatar)
            embed.set_thumbnail(url=user.avatar)

            embeds.append(embed)

        view = PaginatorView(embeds, interaction.user)
        applogger.debug_command(interaction)
        await interaction.response.send_message(embed=embeds[0], view=view)

    @discord.app_commands.command(
        name="layouts_with",
        description="List all layouts that use a specific music or artist"
    )
    @discord.app_commands.describe(
        choice="Search by music or artist",
        name="Name of the music or artist"
    )
    @discord.app_commands.choices(
        choice=[
            discord.app_commands.Choice(name="Music", value="music"),
            discord.app_commands.Choice(name="Artist", value="artist"),
        ]
    )
    async def layouts_with(self, interaction: discord.Interaction, choice: discord.app_commands.Choice[str], name: str):

        """
        List all layouts that utilize a specific music track or are created by a particular artist.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object representing the command invocation.
        choice : discord.app_commands.Choice[str]
            Choice indicating whether to filter by 'music' or 'artist'.
        name : str
            The name of the music track or artist.

        Behavior
        --------
        - Queries the database based on the selected choice.
        - Retrieves layouts linked to the specified music or artist.
        - Paginates results with 10 layouts per embed.
        - Includes creator/artist name and YouTube thumbnail when available.

        Exceptions
        ----------
        DataNotFound
            Raised if no layouts match the given search criteria.
        InvalidYouTubeURL
            Raised if the YouTube link of a music or artist cannot be parsed.
        """

        try:
            if choice.value == "music":
                all_layouts = database.get_layouts_with_music(name)
            elif choice.value == "artist":
                all_layouts = database.get_layouts_with_artist(name)
        except DataNotFound:
            await interaction.response.send_message(f"No **layouts** found for {choice.name.lower()} '{name}'")
            applogger.error(f"Empty response on {interaction.command.name} ran by {interaction.user.name} in {interaction.guild.name}")
            return

        if not all_layouts:
            await interaction.response.send_message(f"No **layouts** found for {choice.name.lower()} '{name}'")
            return

        per_page = 10
        embeds = []

        for i in range(0, len(all_layouts), per_page):
            chunk = all_layouts[i:i + per_page]

            embed = discord.Embed(
                title=f"Layouts with {choice.name.lower()}: {name}",
                description=f"Total : {len(all_layouts)} (Page {i//per_page + 1}/{(len(all_layouts)-1)//per_page + 1})",
                color=discord.Color.dark_grey()
            )

            fullstring = "\n".join(
                f"**{layout['name']}** by *{layout['creator_name']}* | [Open in browser]({layout['yt']})"
                for layout in chunk
            )
            embed.add_field(name="List", value=fullstring, inline=False)
            embed.set_footer(text="Gameplay Database", icon_url=self.bot.user.avatar)

            if choice.value == "music":
                try:
                    getmusic = database.get_music_by_name(name)
                    url = tools.get_youtube_thumbnail(getmusic[0]["yt"])
                    if url:
                        embed.set_image(url=url)
                except DataNotFound:
                    applogger.error(f"Could not load yt thumbnail for music : {name} on {interaction.command.name}")
            elif choice.value == "artist":
                try:
                    getartist = database.get_artist_by_name(name)
                    channel_api_id = tools.get_yt_channel_id(getartist[0]['yt'])
                    ytpp_url = tools.get_youtube_pp(channel_api_id)
                    if ytpp_url:
                        embed.set_image(url=ytpp_url)
                    else:
                        embed.set_footer(text="No YouTube link available", icon_url=self.bot.user.avatar)
                except (InvalidYouTubeURL, UnboundLocalError):
                    applogger.warning(f"Failed to retrieve info due to YouTube URL on {interaction.command.name}")
                    embed.set_footer(text="No YouTube link available", icon_url=self.bot.user.avatar)

            embeds.append(embed)

        view = PaginatorView(embeds, interaction.user)
        applogger.debug_command(interaction)
        await interaction.response.send_message(embed=embeds[0], view=view)

    @discord.app_commands.command(
        name="collabs_with",
        description="List all collabs that use a specific music or artist"
    )
    @discord.app_commands.describe(
        choice="Search by music or artist",
        name="Name of the music or artist"
    )
    @discord.app_commands.choices(
        choice=[
            discord.app_commands.Choice(name="Music", value="music"),
            discord.app_commands.Choice(name="Artist", value="artist"),
        ]
    )
    async def collabs_with(self, interaction: discord.Interaction, choice: discord.app_commands.Choice[str], name: str):

        """
        List all collabs that include a specific music track or are associated with a particular artist.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object representing the command invocation.
        choice : discord.app_commands.Choice[str]
            Choice indicating whether to filter by 'music' or 'artist'.
        name : str
            The name of the music track or artist.

        Behavior
        --------
        - Queries the database for collabs filtered by music or artist.
        - Displays results in paginated embeds (10 items per page).
        - Each embed contains collab name, host name, and a clickable link.
        - Attempts to display YouTube thumbnail if available.

        Exceptions
        ----------
        DataNotFound
            Raised if no collabs match the search criteria.
        InvalidYouTubeURL
            Raised if the YouTube link cannot be parsed.
        """

        try:
            if choice.value == "music":
                all_collabs = database.get_collabs_with_music(name)
            elif choice.value == "artist":
                all_collabs = database.get_collabs_with_artist(name)
        except DataNotFound:
            await interaction.response.send_message(f"No **collabs** found for {choice.name.lower()} '{name}'")
            applogger.error(f"Empty response on {interaction.command.name} ran by {interaction.user.name} in {interaction.guild.name}")
            return

        if not all_collabs:
            await interaction.response.send_message(f"No **collabs** found for {choice.name.lower()} '{name}'")
            return

        per_page = 10
        embeds = []

        for i in range(0, len(all_collabs), per_page):
            chunk = all_collabs[i:i + per_page]

            embed = discord.Embed(
                title=f"Collabs with {choice.name.lower()}: {name}",
                description=f"Total : {len(all_collabs)} (Page {i//per_page + 1}/{(len(all_collabs)-1)//per_page + 1})",
                color=discord.Color.dark_grey()
            )

            fullstring = "\n".join(
                f"**{collab['name']}** hosted by *{collab['host_name']}* | [Open in browser]({collab['yt']})"
                for collab in chunk
            )
            embed.add_field(name="List", value=fullstring, inline=False)
            embed.set_footer(text="Gameplay Database", icon_url=self.bot.user.avatar)

            if choice.value == "music":
                try:
                    getmusic = database.get_music_by_name(name)
                    url = tools.get_youtube_thumbnail(getmusic[0]["yt"])
                    if url:
                        embed.set_image(url=url)
                except DataNotFound:
                    applogger.error(f"Could not load yt thumbnail for music : {name} on {interaction.command.name}")
            elif choice.value == "artist":
                try:
                    getartist = database.get_artist_by_name(name)
                    channel_api_id = tools.get_yt_channel_id(getartist[0]['yt'])
                    ytpp_url = tools.get_youtube_pp(channel_api_id)
                    if ytpp_url:
                        embed.set_image(url=ytpp_url)
                    else:
                        embed.set_footer(text="No YouTube link available", icon_url=self.bot.user.avatar)
                except (InvalidYouTubeURL, UnboundLocalError):
                    applogger.warning(f"Failed to retrieve info due to YouTube URL on {interaction.command.name}")
                    embed.set_footer(text="No YouTube link available", icon_url=self.bot.user.avatar)

            embeds.append(embed)

        view = PaginatorView(embeds, interaction.user)
        applogger.debug_command(interaction)
        await interaction.response.send_message(embed=embeds[0], view=view)


    @discord.app_commands.command(
        name="levels_with",
        description="List all levels (layouts + collabs) that use a specific music or artist"
    )
    @discord.app_commands.describe(
        choice="Search by music or artist",
        name="Name of the music or artist"
    )
    @discord.app_commands.choices(
        choice=[
            discord.app_commands.Choice(name="Music", value="music"),
            discord.app_commands.Choice(name="Artist", value="artist"),
        ]
    )
    async def levels_with(self, interaction: discord.Interaction, choice: discord.app_commands.Choice[str], name: str):

        """
        List all levels (layouts + collabs) that include a specific music track or are associated with a specific artist.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object representing the command invocation.
        choice : discord.app_commands.Choice[str]
            Choice indicating whether to filter by 'music' or 'artist'.
        name : str
            The name of the music track or artist.

        Behavior
        --------
        - Retrieves both layouts and collabs matching the specified music or artist.
        - Displays results in paginated embeds (10 items per page).
        - Each embed includes the level name, creator/host, and a clickable link.
        - Displays thumbnails from YouTube if available.

        Exceptions
        ----------
        DataNotFound
            Raised if no levels match the given search criteria.
        InvalidYouTubeURL
            Raised if the YouTube link cannot be parsed.
        """

        try:
            if choice.value == "music":
                all_levels = database.get_levels_with_music(name)
            elif choice.value == "artist":
                all_levels = database.get_levels_with_artist(name)
        except DataNotFound:
            await interaction.response.send_message(f"No **levels** found for {choice.name.lower()} '{name}'")
            applogger.error(f"Empty response on {interaction.command.name} ran by {interaction.user.name} in {interaction.guild.name}")
            return

        if not all_levels:
            await interaction.response.send_message(f"No **levels** found for {choice.name.lower()} '{name}'")
            return

        per_page = 10
        embeds = []

        for i in range(0, len(all_levels), per_page):
            chunk = all_levels[i:i + per_page]

            embed = discord.Embed(
                title=f"Levels with {choice.name.lower()}: {name}",
                description=f"Total : {len(all_levels)} (Page {i//per_page + 1}/{(len(all_levels)-1)//per_page + 1})",
                color=discord.Color.dark_grey()
            )

            fullstring = "\n".join(
                f"**{lvl['name']}** by *{lvl['creator_name'] if 'creator_name' in lvl else lvl['host_name']}* | [Open in browser]({lvl['yt']})"
                for lvl in chunk
            )
            embed.add_field(name="List", value=fullstring, inline=False)
            embed.set_footer(text="Gameplay Database", icon_url=self.bot.user.avatar)

            if choice.value == "music":
                try:
                    getmusic = database.get_music_by_name(name)
                    url = tools.get_youtube_thumbnail(getmusic[0]["yt"])
                    if url:
                        embed.set_image(url=url)
                except DataNotFound:
                    applogger.error(f"Could not load yt thumbnail for music : {name} on {interaction.command.name}")
            elif choice.value == "artist":
                try:
                    getartist = database.get_artist_by_name(name)
                    channel_api_id = tools.get_yt_channel_id(getartist[0]['yt'])
                    ytpp_url = tools.get_youtube_pp(channel_api_id)
                    if ytpp_url:
                        embed.set_image(url=ytpp_url)
                    else:
                        embed.set_footer(text="No YouTube link available", icon_url=self.bot.user.avatar)
                except (InvalidYouTubeURL, UnboundLocalError):
                    applogger.warning(f"Failed to retrieve info due to YouTube URL on {interaction.command.name}")
                    embed.set_footer(text="No YouTube link available", icon_url=self.bot.user.avatar)

            embeds.append(embed)

        view = PaginatorView(embeds, interaction.user)
        applogger.debug_command(interaction)
        await interaction.response.send_message(embed=embeds[0], view=view)


    @discord.app_commands.command(
        name="parts_of",
        description="List the parts registered in the database that belong to a specific collab"
    )
    async def parts_of(self, interaction: discord.Interaction, collab_name: str):

        """
        List all parts associated with a given collab, showing which parts are registered.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object representing the command invocation.
        collab_name : str
            The name of the collab for which to retrieve parts.

        Behavior
        --------
        - Retrieves all parts registered under the specified collab.
        - Displays the total number of parts versus expected total builders.
        - Shows each part with its creator and optional YouTube link.
        - If parts are missing, displays a message encouraging requests.
        - Adds a thumbnail using the collab's YouTube video if available.

        Exceptions
        ----------
        DataNotFound
            Raised if no parts exist for the given collab.
        """

        try:
            parts, total_builders = database.get_parts_of(collab_name)
        except DataNotFound:
            await interaction.response.send_message(f"No **parts** found for collab `{collab_name}`.")
            applogger.error(f"Empty response on {interaction.command.name} ran by {interaction.user.name} in {interaction.guild.name}")
            return

        registered_parts = len(parts)

        list_embed = discord.Embed(
            title=f"Parts of {collab_name}",
            description=f"Total registered: {registered_parts}/{total_builders}",
            color=discord.Color.dark_grey()
        )

        try:
            getcollab = database.get_collab_by_name(collab_name)
            url = tools.get_youtube_thumbnail(getcollab[0]["yt"])
            if url:
                list_embed.set_image(url=url)
        except DataNotFound:
            applogger.error(f"Couldn't get yt thumbnail for collab : {collab_name} on {interaction.command.name} ran by {interaction.user.name} in {interaction.guild.name}")

        parts_str = ""
        for part in parts:
            name, yt, creator = part
            yt_link = f"[Open in browser]({yt})" if yt else "No YouTube link"
            parts_str += f"**{name}** — by *{creator}* | {yt_link}\n"

        list_embed.add_field(
            name="List",
            value=parts_str[:1024] if parts_str else "No parts found.",
            inline=False
        )

        if total_builders and registered_parts < total_builders:
            list_embed.set_footer(
                text=(
                    f"{total_builders - registered_parts} part(s) missing from this collab. "
                    "Feel free to request them"
                ),
                icon_url=self.bot.user.avatar
            )
        else:
            list_embed.set_footer(
                text="All parts of this collab are registered.",
                icon_url=self.bot.user.avatar
            )

        list_embed.set_thumbnail(url=self.bot.user.avatar)

        applogger.debug_command(interaction)
        await interaction.response.send_message(embed=list_embed)


    




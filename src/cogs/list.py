import discord
from discord.ext import commands

import database
from utilities.applogger import AppLogger
from exceptions.custom_exceptions import DataNotFound, InvalidYouTubeURL
from utilities import tools

applogger = AppLogger()

class ListCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(name="layouts_from", description="List the levels registered in the database from the given creator")
    async def layouts_from(self, interaction: discord.Interaction, user: discord.User):
        
        try:
            get = database.get_layouts_from(user.global_name)
        except DataNotFound:
            await interaction.response.send_message(f"No **levels** from {user.global_name}")
            applogger.error(f"Empty response on {interaction.command.name} used by {interaction.user.name}")
            return
        
        list_embed = discord.Embed(
            title=f"Levels created by {user.global_name}",
            description=f"Total : {len(get)}",
            color=discord.Color.dark_grey()
        )

        fullstring = ""
        for level in get:
            fullstring += f"{level['name']} | [Open in browser]({level['yt']})\n"

        list_embed.add_field(name="List", value=fullstring)

        list_embed.set_footer(text="Gameplay Database", icon_url=self.bot.user.avatar)
        list_embed.set_thumbnail(url=user.avatar)
        applogger.debug_command(interaction)
        await interaction.response.send_message(embed=list_embed)

    @discord.app_commands.command(
        name="collabs_from",
        description="List the collabs registered in the database from the given host"
    )
    async def collabs_from(self, interaction: discord.Interaction, user: discord.User):
        try:
            get = database.get_collabs_from(user.global_name)
        except DataNotFound:
            await interaction.response.send_message(f"No **collabs** from {user.global_name}")
            applogger.error(f"Empty response on {interaction.command.name} used by {interaction.user.name}")
            return
        
        list_embed = discord.Embed(
            title=f"Collabs hosted by {user.global_name}",
            description=f"Total : {len(get)}",
            color=discord.Color.dark_grey()
        )

        fullstring = ""
        for collab in get:
            fullstring += f"{collab['name']} | [Open in browser]({collab['yt']})\n"

        list_embed.add_field(name="List", value=fullstring[:1024])
        list_embed.set_footer(text="Gameplay Database", icon_url=self.bot.user.avatar)
        list_embed.set_thumbnail(url=user.avatar)
        
        applogger.debug_command(interaction)
        await interaction.response.send_message(embed=list_embed)

    @discord.app_commands.command(
    name="parts_from",
    description="List all collab parts built by the given creator"
    )
    async def parts_from(self, interaction: discord.Interaction, user: discord.User):

        try:
            get = database.get_parts_from(user.global_name)
        except DataNotFound:
            await interaction.response.send_message(f"No **collab parts** from {user.global_name}")
            applogger.error(f"Empty response on {interaction.command.name} used by {interaction.user.name}")
            return

        list_embed = discord.Embed(
            title=f"Collab parts built by {user.global_name}",
            description=f"Total : {len(get)}",
            color=discord.Color.dark_grey()
        )

        fullstring = ""
        for part in get:
            master = part["masterlevel"] if part["masterlevel"] else "Unknown collab"
            fullstring += f"**{part['name']}** *(from {master})* | [Open in browser]({part['yt']})\n"

        list_embed.add_field(name="List", value=fullstring[:1024])
        list_embed.set_footer(text="Gameplay Database", icon_url=self.bot.user.avatar)
        list_embed.set_thumbnail(url=user.avatar)

        applogger.debug_command(interaction)
        await interaction.response.send_message(embed=list_embed)

            
    @discord.app_commands.command(
        name="musics_from",
        description="List the musics registered in the database from the given artist"
    )
    async def musics_from(self, interaction: discord.Interaction, artist: str):

        try:
            get = database.get_musics_from(artist)
        except DataNotFound:
            await interaction.response.send_message(f"No **musics** from {artist}")
            applogger.error(f"Empty response on {interaction.command.name} used by {interaction.user.name}")
            return
        
        list_embed = discord.Embed(
            title=f"Musics from {artist}",
            description=f"Total : {len(get)}",
            color=discord.Color.dark_grey()
        )

        fullstring = ""
        for music in get:
            yt_link = f"[YouTube]({music['yt']})" if music["yt"] else "YouTube : No link"
            sc_link = f"[SoundCloud]({music['soundcloud']})" if music["soundcloud"] else "SoundCloud : No link"
            fullstring += f"**{music['name']}**\n {yt_link} | {sc_link}\n"

        list_embed.add_field(name="List", value=fullstring[:1024])
        list_embed.set_footer(text="Gameplay Database", icon_url=self.bot.user.avatar)

        ytpp_url = None 
        try:
            get_artist = database.get_artist_by_name(artist)
        except DataNotFound:
            applogger.error(f"Failed to retrieve {artist} data from database")

        db_artist = get_artist[0]

        try:
            channel_api_id = tools.get_yt_channel_id(db_artist['yt'])
            ytpp_url = tools.get_youtube_pp(channel_api_id)
        except (InvalidYouTubeURL, UnboundLocalError):
            applogger.warning(f"Failed to retrieve info due to youtube URL on {interaction.command.name} ran by {interaction.user.name}")
            applogger.debug_command(interaction)
            return await interaction.response.send_message(embed=list_embed)
        
        if ytpp_url:
            list_embed.set_thumbnail(url=ytpp_url)
        else:
            list_embed.set_footer(text="No YouTube link available", icon_url=self.bot.user.avatar)
        
        applogger.debug_command(interaction)

        await interaction.response.send_message(embed=list_embed)

    @discord.app_commands.command(
        name="levels_from",
        description="List every layout and collab registered in the database from the given creator"
    )
    async def levels_from(self, interaction: discord.Interaction, user: discord.User):
        try:
            get = database.get_levels_from(user.global_name)
        except DataNotFound:
            await interaction.response.send_message(f"No **levels** (layouts or collabs) from {user.global_name}")
            applogger.error(f"Empty response on {interaction.command.name} used by {interaction.user.name}")
            return
        
        list_embed = discord.Embed(
            title=f"Levels from {user.global_name}",
            description=f"Total : {len(get)}",
            color=discord.Color.dark_grey()
        )

        layouts = [lvl for lvl in get if lvl['type'] == 'layout']
        collabs = [lvl for lvl in get if lvl['type'] == 'collab']

        # --- Layouts ---
        if layouts:
            layout_str = ""
            for layout in layouts:
                layout_str += f"{layout['name']} | [Open in browser]({layout['yt']})\n"
            list_embed.add_field(
                name=f"Layouts ({len(layouts)})",
                value=layout_str[:1024],
                inline=False
            )

        # --- Collabs ---
        if collabs:
            collab_str = ""
            for collab in collabs:
                collab_str += f"{collab['name']} | [Open in browser]({collab['yt']})\n"
            list_embed.add_field(
                name=f"Collabs ({len(collabs)})",
                value=collab_str[:1024],
                inline=False
            )

        list_embed.set_footer(text="Gameplay Database", icon_url=self.bot.user.avatar)
        list_embed.set_thumbnail(url=user.avatar)
        
        applogger.debug_command(interaction)
        await interaction.response.send_message(embed=list_embed)

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
        try:
            if choice.value == "music":
                get = database.get_layouts_with_music(name)
            elif choice.value == "artist":
                get = database.get_layouts_with_artist(name)
        except DataNotFound:
            await interaction.response.send_message(f"No **layouts** found for {choice.name.lower()} '{name}'")
            applogger.error(f"Empty response on {interaction.command.name} used by {interaction.user.name}")
            return

        list_embed = discord.Embed(
            title=f"Layouts with {choice.name.lower()}: {name}",
            description=f"Total : {len(get)}",
            color=discord.Color.dark_grey()
        )

        fullstring = "\n".join(
            f"**{layout['name']}** by *{layout['creator_name']}* | [Open in browser]({layout['yt']})"
            for layout in get
        )

        if choice.value == "music":
            try:
                getmusic = database.get_music_by_name(name)
                url = tools.get_youtube_thumbnail(getmusic[0]["yt"])
                if url:
                    list_embed.set_image(url=url)
            except DataNotFound:
                applogger.error(f"Could not load yt thumbnail for music : {name} on {interaction.command.name}")

        elif choice.value == "artist":
            ytpp_url = None 
            try:
                getartist = database.get_artist_by_name(name)
                channel_api_id = tools.get_yt_channel_id(getartist[0]['yt'])
                ytpp_url = tools.get_youtube_pp(channel_api_id)
            except (InvalidYouTubeURL, UnboundLocalError):
                applogger.warning(f"Failed to retrieve info due to youtube URL on {interaction.command.name} ran by {interaction.user.name}")
                applogger.debug_command(interaction)
                list_embed.add_field(name="List", value=fullstring[:1024])
                list_embed.set_footer(text="Gameplay Database", icon_url=self.bot.user.avatar)
                return await interaction.response.send_message(embed=list_embed)
            
            if ytpp_url:
                list_embed.set_image(url=ytpp_url)
            else:
                list_embed.set_footer(text="No YouTube link available", icon_url=self.bot.user.avatar)
            

        list_embed.add_field(name="List", value=fullstring[:1024])
        list_embed.set_footer(text="Gameplay Database", icon_url=self.bot.user.avatar)
        
        applogger.debug_command(interaction)
        await interaction.response.send_message(embed=list_embed)


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
        try:
            if choice.value == "music":
                get = database.get_collabs_with_music(name)
            elif choice.value == "artist":
                get = database.get_collabs_with_artist(name)
        except DataNotFound:
            await interaction.response.send_message(f"No **collabs** found for {choice.name.lower()} '{name}'")
            applogger.error(f"Empty response on {interaction.command.name} used by {interaction.user.name}")
            return

        list_embed = discord.Embed(
            title=f"Collabs with {choice.name.lower()}: {name}",
            description=f"Total : {len(get)}",
            color=discord.Color.dark_grey()
        )

        fullstring = "\n".join(
            f"**{collab['name']}** hosted by *{collab['host_name']}* | [Open in browser]({collab['yt']})"
            for collab in get
        )

        if choice.value == "music":
            try:
                getmusic = database.get_music_by_name(name)
                url = tools.get_youtube_thumbnail(getmusic[0]["yt"])
                if url:
                    list_embed.set_image(url=url)
            except DataNotFound:
                applogger.error(f"Could not load yt thumbnail for music : {name} on {interaction.command.name}")

        elif choice.value == "artist":
            ytpp_url = None 
            try:
                getartist = database.get_artist_by_name(name)
                channel_api_id = tools.get_yt_channel_id(getartist[0]['yt'])
                ytpp_url = tools.get_youtube_pp(channel_api_id)
            except (InvalidYouTubeURL, UnboundLocalError):
                applogger.warning(f"Failed to retrieve info due to youtube URL on {interaction.command.name} ran by {interaction.user.name}")
                applogger.debug_command(interaction)
                list_embed.add_field(name="List", value=fullstring[:1024])
                list_embed.set_footer(text="Gameplay Database", icon_url=self.bot.user.avatar)
                return await interaction.response.send_message(embed=list_embed)
            
            if ytpp_url:
                list_embed.set_image(url=ytpp_url)
            else:
                list_embed.set_footer(text="No YouTube link available", icon_url=self.bot.user.avatar)

        list_embed.add_field(name="List", value=fullstring[:1024])
        list_embed.set_footer(text="Gameplay Database", icon_url=self.bot.user.avatar)
        
        applogger.debug_command(interaction)
        await interaction.response.send_message(embed=list_embed)


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
        try:
            if choice.value == "music":
                get = database.get_levels_with_music(name)
            elif choice.value == "artist":
                get = database.get_levels_with_artist(name)
        except DataNotFound:
            await interaction.response.send_message(f"No **levels** found for {choice.name.lower()} '{name}'")
            applogger.error(f"Empty response on {interaction.command.name} used by {interaction.user.name}")
            return

        list_embed = discord.Embed(
            title=f"Levels with {choice.name.lower()}: {name}",
            description=f"Total : {len(get)}",
            color=discord.Color.dark_grey()
        )

        fullstring = "\n".join(
            f"**{lvl['name']}** by *{lvl['creator_name'] if 'creator_name' in lvl.keys() else lvl['host_name']}* | [Open in browser]({lvl['yt']})"
            for lvl in get
        )

        if choice.value == "music":
            try:
                getmusic = database.get_music_by_name(name)
                url = tools.get_youtube_thumbnail(getmusic[0]["yt"])
                if url:
                    list_embed.set_image(url=url)
            except DataNotFound:
                applogger.error(f"Could not load yt thumbnail for music : {name} on {interaction.command.name} ran by {interaction.user.name}")

        elif choice.value == "artist":
            ytpp_url = None 
            try:
                getartist = database.get_artist_by_name(name)
                channel_api_id = tools.get_yt_channel_id(getartist[0]['yt'])
                ytpp_url = tools.get_youtube_pp(channel_api_id)
            except (InvalidYouTubeURL, UnboundLocalError):
                applogger.warning(f"Failed to retrieve info due to youtube URL on {interaction.command.name} ran by {interaction.user.name}")
                applogger.debug_command(interaction)
                list_embed.add_field(name="List", value=fullstring[:1024])
                list_embed.set_footer(text="Gameplay Database", icon_url=self.bot.user.avatar)
                return await interaction.response.send_message(embed=list_embed)
            
            if ytpp_url:
                list_embed.set_image(url=ytpp_url)
            else:
                list_embed.set_footer(text="No YouTube link available", icon_url=self.bot.user.avatar)

        list_embed.add_field(name="List", value=fullstring[:1024])
        list_embed.set_footer(text="Gameplay Database", icon_url=self.bot.user.avatar)
        
        applogger.debug_command(interaction)
        await interaction.response.send_message(embed=list_embed)


    @discord.app_commands.command(
        name="parts_of",
        description="List the parts registered in the database that belong to a specific collab"
    )
    async def parts_of(self, interaction: discord.Interaction, collab_name: str):
        try:
            parts, total_builders = database.get_parts_of(collab_name)
        except DataNotFound:
            await interaction.response.send_message(f"No **parts** found for collab `{collab_name}`.")
            applogger.error(f"Empty response on {interaction.command.name} used by {interaction.user.name}")
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
            applogger.error(f"Couldn't get yt thumbnail for collab : {collab_name} on {interaction.command.name} ran by {interaction.user.name}")

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


    




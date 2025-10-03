import discord
from discord.ext import commands
from utilities.applogger import AppLogger
from utilities import tools

import database

applogger = AppLogger()

class QueryCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @discord.app_commands.command(name="get_creator_by_name", description="Retrieves data about a creator by giving name")
    @discord.app_commands.describe(user="Creator username (discord)")
    async def get_creator_by_name(self, interaction: discord.Interaction, user: discord.User):
        
        get = database.get_creator_by_name(user.global_name)
        if not get:
            await interaction.response.send_message("**User** not found.")
            applogger.error(f"Empty response on {interaction.command.name} used by {interaction.user.name}")
            return
        creator = get[0]

        embed = discord.Embed(
            title=f"Creator overview : {creator['username']}",
            description="Infos",
            color=discord.Color.dark_grey()
        )

        embed.add_field(name="Creator ID (database)", value=creator["id"], inline=False)
        embed.add_field(name="Username", value=creator["username"], inline=False)
        embed.add_field(name="Nationality", value=creator["nationality"], inline=False)
        embed.add_field(name="Discord", value=creator["discord"], inline=False)
        embed.add_field(name="Discord user ID", value=creator["discord_uid"], inline=False)
        embed.add_field(name="Youtube", value=f"[Open in browser]({creator['yt']})" if creator['yt'] else None, inline=False)
        embed.add_field(name="Layouts registered", value=creator["layouts_registered"], inline=False)
        embed.add_field(name="Collab participations", value=creator["collab_participations"], inline=False)
        embed.add_field(name="Total time built", value=creator["total_time_built"], inline=False)
        embed.add_field(name="Registration date", value=creator["registration_date"], inline=False)
        embed.add_field(name="Recorder name", value=creator["recorder_name"], inline=False)

        embed.set_footer(text="Gameplay Database", icon_url=self.bot.user.avatar)
        embed.set_thumbnail(url=self.bot.user.avatar)

        embed.set_image(url=user.avatar)

        applogger.debug_command(interaction)
        await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="get_layout_by_name", description="Retrieves data about a layout by giving name")
    @discord.app_commands.describe(name="Layout name")
    async def get_layout_by_name(self, interaction: discord.Interaction, name: str):

        get = database.get_layout_by_name(name)
        
        if not get:
            await interaction.response.send_message("**Layout** not found.")
            applogger.error(f"Empty response on {interaction.command.name} used by {interaction.user.name}")
            return
        layout = get[0]

        embed = discord.Embed(
            title=f"Layout overview : {layout['name']}",
            description="Infos",
            color=discord.Color.dark_grey()
        )

        embed.add_field(name="Layout ID (database)", value=layout["id"])
        embed.add_field(name="Creator ID (database)", value=layout["creator_id"])
        embed.add_field(name="Creator", value=layout["creator_name"], inline=False)
        embed.add_field(name="Name", value=layout["name"], inline=False)
        embed.add_field(name="Type", value=layout["type"], inline=False)
        embed.add_field(name="Length", value=layout["length"], inline=False)
        embed.add_field(name="Youtube", value=f"[Open in browser]({layout['yt']})" if layout['yt'] else None, inline=False)
        embed.add_field(name="Music ID (database)", value=layout["music_id"], inline=False)
        embed.add_field(name="Music NG ID", value=layout["music_ngid"], inline=False)
        embed.add_field(name="Music name", value=layout["music_name"], inline=False)
        embed.add_field(name="Artist ID (database)", value=layout["artist_id"])
        embed.add_field(name="Music artist", value=layout["music_artist"], inline=False)
        embed.add_field(name="In-game ID", value=layout["igid"], inline=False)
        embed.add_field(name="Masterlevel", value=layout["masterlevel"], inline=False)
        embed.add_field(name="Registration date", value=layout["registration_date"], inline=False)
        embed.add_field(name="Recorder name", value=layout["recorder_name"], inline=False)
        embed.add_field(name="Recorder notes", value=layout["recorder_notes"], inline=False)

        embed.set_footer(text="Gameplay Database", icon_url=self.bot.user.avatar)
        embed.set_thumbnail(url=self.bot.user.avatar)

        embed.set_image(url=tools.get_youtube_thumbnail(layout["yt"]))
        
        applogger.debug_command(interaction)
        await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="get_collab_by_name", description="Retrieves data about a collab by giving name")
    @discord.app_commands.describe(name="Collab name")
    async def get_collab_by_name(self, interaction: discord.Interaction, name: str):

        get = database.get_collab_by_name(name)
        
        if not get:
            await interaction.response.send_message("**Collab** not found.")
            applogger.error(f"Empty response on {interaction.command.name} used by {interaction.user.name}")
            return
        collab = get[0]

        embed = discord.Embed(
            title=f"Collab overview : {collab['name']}",
            description="Infos",
            color=discord.Color.dark_teal()
        )

        embed.add_field(name="Collab ID (database)", value=collab["id"])
        embed.add_field(name="Host ID (database)", value=collab["host_id"])
        embed.add_field(name="Host", value=collab["host_name"], inline=False)
        embed.add_field(name="Name", value=collab["name"], inline=False)
        embed.add_field(name="Builders number", value=collab["builders_number"], inline=False)
        embed.add_field(name="Length", value=collab["length"], inline=False)
        embed.add_field(name="Youtube", value=f"[Open in browser]({collab['yt']})" if collab['yt'] else None, inline=False)
        embed.add_field(name="Music ID (database)", value=collab["music_id"], inline=False)
        embed.add_field(name="Music NG ID", value=collab["music_ngid"], inline=False)
        embed.add_field(name="Music name", value=collab["music_name"], inline=False)
        embed.add_field(name="Music artist", value=collab["music_artist"], inline=False)
        embed.add_field(name="In-game ID", value=collab["igid"], inline=False)
        embed.add_field(name="Registration date", value=collab["registration_date"], inline=False)
        embed.add_field(name="Recorder name", value=collab["recorder_name"], inline=False)
        embed.add_field(name="Recorder notes", value=collab["recorder_notes"], inline=False)

        embed.set_footer(text="Gameplay Database", icon_url=self.bot.user.avatar)
        embed.set_thumbnail(url=self.bot.user.avatar)

        embed.set_image(url=tools.get_youtube_thumbnail(collab["yt"]))

        applogger.debug_command(interaction)
        await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="get_music_by_name", description="Retrieves data about a music by giving name")
    @discord.app_commands.describe(name="Music name")
    async def get_music_by_name(self, interaction: discord.Interaction, name: str):

        get = database.get_music_by_name(name)
        
        if not get:
            await interaction.response.send_message("**Music** not found.")
            applogger.error(f"Empty response on {interaction.command.name} used by {interaction.user.name}")
            return
        music = get[0]

        embed = discord.Embed(
            title=f"Music overview : {music['name']}",
            description="Infos",
            color=discord.Color.dark_grey()
        )

        embed.add_field(name="Music ID (database)", value=music["id"], inline=False)
        embed.add_field(name="Name", value=music["name"], inline=False)
        embed.add_field(name="Artist ID", value=music["artist_id"], inline=False)
        embed.add_field(name="Artist", value=music["artist"], inline=False)
        embed.add_field(name="Length", value=music["length"], inline=False)
        embed.add_field(name="Type", value=music["type"], inline=False)
        embed.add_field(name="Youtube", value=f"[Open in browser]({music['yt']})" if music['yt'] else None, inline=False)
        embed.add_field(name="SoundCloud", value=f"[Open in browser]({music['soundcloud']})" if music["soundcloud"] else None, inline=False)
        embed.add_field(name="Uses", value=music["uses"], inline=False)
        embed.add_field(name="Newgrounds ID", value=music["ngid"], inline=False)
        embed.add_field(name="Registration date", value=music["registration_date"], inline=False)
        embed.add_field(name="Recorder name", value=music["recorder_name"], inline=False)
        embed.add_field(name="Recorder notes", value=music["recorder_notes"], inline=False)

        embed.set_footer(text="Gameplay Database", icon_url=self.bot.user.avatar)
        embed.set_thumbnail(url=self.bot.user.avatar)

        embed.set_image(url=tools.get_youtube_thumbnail(music["yt"]))
        
        applogger.debug_command(interaction)
        await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="get_artist_by_name", description="Retrieves data about an artist by giving name")
    @discord.app_commands.describe(name="Artist name")
    async def get_artist_by_name(self, interaction: discord.Interaction, name: str):

        get = database.get_artist_by_name(name)
        
        if not get:
            await interaction.response.send_message("**Artist** not found.")
            applogger.error(f"Empty response on {interaction.command.name} used by {interaction.user.name}")
            return
        artist = get[0]

        embed = discord.Embed(
            title=f"Artist overview : {artist['name']}",
            description="Infos",
            color=discord.Color.dark_grey()
        )

        embed.add_field(name="Artist ID", value=artist["id"], inline=False)
        embed.add_field(name="Name", value=artist["name"], inline=False)
        embed.add_field(name="Youtube", value=f"[Open in browser]({artist['yt']})" if artist["yt"] else None, inline=False)
        embed.add_field(name="Soundcloud", value=f"[Open in browser]({artist['soundcloud']})" if artist["soundcloud"] else None, inline=False)
        embed.add_field(name="Songs registered", value=artist["songs_registered"], inline=False)
        embed.add_field(name="Total song uses", value=artist["total_song_uses"], inline=False)
        embed.add_field(name="Registration date", value=artist["registration_date"], inline=False)
        embed.add_field(name="Recorder name", value=artist["recorder_name"], inline=False)
        embed.add_field(name="Recorder notes", value=artist["recorder_notes"], inline=False)

        embed.set_footer(text="Gameplay Database", icon_url=self.bot.user.avatar)
        embed.set_thumbnail(url=self.bot.user.avatar)

        channel_api_id = tools.get_yt_channel_id(artist['yt'])
        ytpp_url = tools.get_youtube_pp(channel_api_id)

        embed.set_image(url=ytpp_url)

        applogger.debug_command(interaction)
        await interaction.response.send_message(embed=embed)




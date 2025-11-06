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

    @discord.app_commands.command(name="levels_from", description="List the levels registered in the database from the given creator")
    async def levels_from(self, interaction: discord.Interaction, user: discord.User):
        
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


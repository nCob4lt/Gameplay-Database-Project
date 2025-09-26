import discord
from discord.ext import commands
import sqlite3

import database
from utilities.applogger import AppLogger

connection = sqlite3.connect("gpdb.db")
c = connection.cursor()

database.initialize()

connection.commit()
connection.close()

applogger = AppLogger()

class RegistrationCog(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @discord.app_commands.command(name="add_creator", description="Adds directly a creator and its info into the database (prior confirmation)")
    @discord.app_commands.describe(user="Creator discord user (discord mention expected)")
    @discord.app_commands.describe(nationality="Creator nationality (prior confirmation)")
    @discord.app_commands.describe(yt="Youtube link to their channel (leave blank if none)")
    async def add_creator(self, interaction: discord.Interaction, user: discord.User, nationality: str, yt: str = None):

        registrator = interaction.user.name
        await database.database_queue.put((database.register_creator,
                                            (user.global_name, nationality, user.name, user.id, yt, registrator,),
                                              {}))

        embed = discord.Embed(
                title="Registration (mod action)",
                description="User successfully registered",
                color=discord.Color.dark_grey()
            )
        
        embed.add_field(name="Username", value=user.global_name, inline=False)
        embed.add_field(name="Nationality", value=nationality, inline=False)
        embed.add_field(name="Discord username", value=user.name, inline=False)
        embed.add_field(name="Youtube", value=f"[Open in browser]({yt})" if yt else None, inline=False)

        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text="Gameplay Database", icon_url=self.bot.user.avatar)
        embed.set_thumbnail(url=self.bot.user.avatar)

        applogger.debug_command(interaction)
        await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="add_layout", description="Adds directly a layout and its info into the database (prior confirmation)")
    @discord.app_commands.describe(creator="Creator of the layout (discord mention expected)")
    @discord.app_commands.describe(name="Name of the layout")
    @discord.app_commands.describe(length="Length of the layout")
    @discord.app_commands.describe(yt="Youtube link of the layout")
    @discord.app_commands.describe(music_name="Name of the music used")
    @discord.app_commands.describe(music_artist="Name of the artist that created the music")
    @discord.app_commands.describe(music_ngid="Newgrounds ID of the music (leave blank if unavailable)")
    @discord.app_commands.describe(type="Type of gameplay used/represented in the layout (speedcore, atmospheric, flow etc... leave blank if unsure)")
    @discord.app_commands.describe(igid="In-game ID of the layout (leave blank if not on servers)")
    @discord.app_commands.describe(masterlevel="The collab the part belongs to, if it is one, if not, leave blank")
    @discord.app_commands.describe(recorder_notes="Write anything you want about this layout right here")
    async def add_layout(
        self,
        interaction: discord.Interaction,
        creator: discord.User,
        name: str,
        length: str,
        yt: str,
        music_name: str,
        music_artist: str,
        music_ngid: int = None,
        type: str = None,
        igid: int = None,
        masterlevel: str = None,
        recorder_notes: str = None):
        
        registrator = interaction.user.name
        await database.database_queue.put((database.register_layout,
                                            (creator.global_name, name, length, yt, music_name, music_artist, music_ngid, type, igid, masterlevel, recorder_notes, registrator,),
                                              {}))

        embed = discord.Embed(
            title="Registration (mod action)",
            description="Layout successffully registered",
            color=discord.Color.dark_grey()
        )

        embed.add_field(name="Creator", value=creator.global_name, inline=False)
        embed.add_field(name="Name", value=name, inline=False)
        embed.add_field(name="Length", value=length, inline=False)
        embed.add_field(name="Youtube link", value=f"[Open in browser]({yt})" if yt else None, inline=False)
        embed.add_field(name="Music name", value=music_name, inline=False)
        embed.add_field(name="Music artist", value=music_artist, inline=False)
        embed.add_field(name="Music NG ID", value=music_ngid, inline=False)
        embed.add_field(name="Type", value=type, inline=False)
        embed.add_field(name="In-game ID", value=igid, inline=False)
        embed.add_field(name="Masterlevel", value=masterlevel, inline=False)
        embed.add_field(name="Recorder notes", value=recorder_notes, inline=False)
        embed.add_field(name="Recorder name", value=registrator, inline=False)

        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text="Gameplay Database", icon_url=self.bot.user.avatar)
        embed.set_thumbnail(url=self.bot.user.avatar)

        applogger.debug_command(interaction)
        await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="add_collab", description="Adds directly a collab and its info into the database (prior confirmation)")
    @discord.app_commands.describe(host="Collab host (discord mention expected)")
    @discord.app_commands.describe(name="Name of the collab")
    @discord.app_commands.describe(builders_number="Number of builders that participated in the collab")
    @discord.app_commands.describe(length="Length of the collab")
    @discord.app_commands.describe(yt="Youtube link of the collab")
    @discord.app_commands.describe(music_name="Name of the music used")
    @discord.app_commands.describe(music_artist="Name of the artist that created the music")
    @discord.app_commands.describe(music_ngid="Newgrounds ID of the music (leave blank if unavailable)")
    @discord.app_commands.describe(igid="In-game ID of the collab (leave blank if not on servers)")
    @discord.app_commands.describe(recorder_notes="Write anything you want about this collab right here")
    async def add_collab(
        self, 
        interaction: discord.Interaction, 
        host: discord.User, 
        name: str, 
        builders_number: int, 
        length: str, 
        yt: str, 
        music_name: str, 
        music_artist: str, 
        music_ngid: int = None, 
        igid: int = None, 
        recorder_notes: str = None):

        registrator = interaction.user.name
        await database.database_queue.put((database.register_collab,
                                            (host.global_name, name, builders_number, length, yt, music_name, music_artist, music_ngid, igid, registrator, recorder_notes,),
                                              {}))

        embed = discord.Embed(
            title="Registration (mod action)",
            description="Collab successfully registered",
            color=discord.Color.dark_grey()
        )

        embed.add_field(name="Host", value=host, inline=False)
        embed.add_field(name="Name", value=name, inline=False)
        embed.add_field(name="Builders number", value=builders_number, inline=False)
        embed.add_field(name="Length", value=length, inline=False)
        embed.add_field(name="Youtube link", value=f"[Open in browser]({yt})" if yt else None, inline=False)
        embed.add_field(name="Music name", value=music_name, inline=False)
        embed.add_field(name="Music artist", value=music_artist, inline=False)
        embed.add_field(name="Music NG ID", value=music_ngid, inline=False)
        embed.add_field(name="In-game ID", value=igid, inline=False)
        embed.add_field(name="Recorder notes", value=recorder_notes, inline=False)
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
        recorder_notes: str = None
    ):
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
        recorder_notes: str = None
    ):
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







    
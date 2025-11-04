import discord
from discord.ext import commands

import database
from utilities.applogger import AppLogger

class ListCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(name="levels_from", description="List the levels registered in the database from the given creator")
    async def levels_from(self, interaction: discord.Interaction, user: discord.User):
        pass

    @discord.app_commands.command(name="musics_from", description="List the musics registered in the database from the given artist")
    async def musics_from(self, interaction: discord.Interaction, artist: str):
        pass
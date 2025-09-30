import discord
from discord.ext import commands
import os

from cogs.maincog import MainCog
from cogs.query import QueryCog
from cogs.registration import RegistrationCog
from cogs.errorhandler import ErrorHandlerCog
from utilities.applogger import AppLogger

applogger = AppLogger()

class GameplayDatabase(commands.Bot):
    def __init__(self) -> None:
        super().__init__(command_prefix="db!", intents=discord.Intents.all())

    async def setup_hook(self):

        await bot.add_cog(MainCog(bot))
        await bot.add_cog(RegistrationCog(bot))
        await bot.add_cog(QueryCog(bot))
        await bot.add_cog(ErrorHandlerCog(bot, applogger))

        synced = await self.tree.sync()
        applogger.info(f"Synchronized commands : {[cmd.name for cmd in synced]}")

bot = GameplayDatabase()
bot.remove_command("help")
TOKEN = os.getenv("DISCORD_GDDB_TOKEN")
bot.run(TOKEN)
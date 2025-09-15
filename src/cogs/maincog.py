import discord
from discord.ext import commands, tasks
import database
from utilities.applogger import AppLogger

intents = discord.Intents.all()
intents.guilds = True
applogger = AppLogger()


class MainCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener(name="on_ready")
    async def starting(self):
        applogger.info("Ready to use")
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Gameplay Database"))

        if not self.sync.is_running():
            self.sync.start()
            applogger.info("Sync task started")

        self.bot.loop.create_task(database.database_worker())

    @tasks.loop(seconds=5)
    async def sync(self):
        await database.database_queue.put((database.synchronize_data, (), {}))

            
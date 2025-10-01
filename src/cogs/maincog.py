from datetime import datetime
import io
import sqlite3
import discord
from discord.ext import commands, tasks
import database
from utilities.applogger import AppLogger
from utilities.recovery import Recovery

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

        if not self.save.is_running():
            self.save.start()
            applogger.info("Save task started")

        self.bot.loop.create_task(database.database_worker())

    @tasks.loop(seconds=5)
    async def sync(self):
        await database.database_queue.put((database.synchronize_data, (), {}))

    @tasks.loop(minutes=5)
    async def save(self):
        applogger.debug("Starting database save...")
        Recovery.create_save()

    @discord.app_commands.command(name="load_backup", description="Loads a file from save folder")
    @discord.app_commands.describe(filename="Name of the file")
    async def loadsave(self, interaction: discord.Interaction, filename: str):
        applogger.debug_command(interaction)
        Recovery.load_save(filename)


    

            
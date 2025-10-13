from discord.ext import commands
import discord
from utilities.applogger import AppLogger
from exceptions.custom_exceptions import *

class ErrorHandlerCog(commands.Cog):

    def __init__(self, bot, applogger: AppLogger):
        self.bot = bot
        self.applogger = applogger

        self.bot.tree.error(self.on_app_command_error)

    @commands.Cog.listener("on_app_command_error")
    async def on_app_command_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
        self.applogger.error(
            f"Raised unhandled app command error: {interaction.command.name if interaction.command else 'unknown'} - {error}"
        )
        
        if isinstance(error, discord.app_commands.CommandInvokeError):
            original = error.original

            match original:
                case DataNotFound():
                    await interaction.response.send_message("**User** not found !", ephemeral=True)

                case MissingModPermissions():
                    await interaction.response.send_message("**You** are not authorized !", ephemeral=True)
        
    @commands.Cog.listener()
    async def on_error(self, event_name, *args, **kwargs):
        self.applogger.error(f"Unhandled event error: {event_name}", exc_info=True)

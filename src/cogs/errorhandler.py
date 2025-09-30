from discord.ext import commands
import discord
from utilities.applogger import AppLogger

class ErrorHandlerCog(commands.Cog):

    def __init__(self, bot, applogger: AppLogger):
        self.bot = bot
        self.applogger = applogger

        self.bot.tree.error = self.on_app_command_error
        bot.add_listener(self.on_error)

    @commands.Cog.listener()
    async def on_app_command_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
        self.applogger.error(
            f"Unhandled app command error: {interaction.command.name if interaction.command else 'unknown'}", 
            exc_info=error
        )
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message("An unexpected error occurred.", ephemeral=True)
        except Exception:
            pass
        
    @commands.Cog.listener()
    async def on_error(self, event_name, *args, **kwargs):
        self.applogger.error(f"Unhandled event error: {event_name}", exc_info=True)

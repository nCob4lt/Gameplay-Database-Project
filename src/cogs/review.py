import discord
from discord.ext import commands

import database
from exceptions.custom_exceptions import DataNotFound
from utilities.applogger import AppLogger
from views.requestview import ReviewRequestView
from utilities import tools

applogger = AppLogger()

class ReviewCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(name="review_next_request",
                                   description="Displays the oldest pending creator registration request.")
    async def review_next_request(self, interaction: discord.Interaction):

        await tools.check_mod(interaction)
        
        try:
            next_request = database.get_oldest_request()
        except DataNotFound:
            await interaction.response.send_message("**No** pending requests at the moment.")
            applogger.error(f"No pending requests at the moment - Interaction user : {interaction.user.name}")
            return
        
        type_, id_, date = next_request
        
        try:
            details = database.get_request_details(type_, id_)
        except DataNotFound:
            await interaction.response.send_message("Failed to fetch requests details, check traceback in *latest.log* for more details")
            applogger.error(f"No pending requests at the moment - Interaction user : {interaction.user.name}")
            return
        
        embed = discord.Embed(
            title=f"Pending {type_.capitalize()} request registration",
            description=f"Submission date : {date}",
            color=discord.Color.dark_grey()
        )

        match type_:

            case "creator":
                embed.add_field(name="Username", value=details["username"], inline=False)
                embed.add_field(name="Nationality", value=details["nationality"], inline=False)
                embed.add_field(name="Discord username", value=details["discord"], inline=False)
                embed.add_field(name="Youtube", value=f"[Open in browser]({details['yt']})" if details["yt"] else "None", inline=False)
                embed.add_field(name="Recorder name", value=details["recorder_name"], inline=False)

            case "layout":
                embed.add_field(name="Name", value=details["name"], inline=False)
                embed.add_field(name="Creator", value=details["creator_name"], inline=False)
                embed.add_field(name="Type", value=details["type"], inline=False)
                embed.add_field(name="Length", value=details["length"], inline=False)
                embed.add_field(name="YouTube", value=f"[Open in browser]({details['yt']})" if details["yt"] else None, inline=False)
                embed.add_field(name="Music", value=f"{details['music_name']} by {details['music_artist']}", inline=False)
                embed.add_field(name="NG ID", value=details["music_ngid"], inline=False)
                embed.add_field(name="In-game ID", value=details["igid"], inline=False)
                embed.add_field(name="Masterlevel", value=details["masterlevel"], inline=False)
                embed.add_field(name="Recorder notes", value=details["recorder_notes"] or "None", inline=False)
                embed.add_field(name="Recorder name", value=details["recorder_name"], inline=False)

            case "collab":
                embed.add_field(name="Name", value=details["name"], inline=False)
                embed.add_field(name="Host", value=details["host_name"], inline=False)
                embed.add_field(name="Builders", value=details["builders_number"], inline=False)
                embed.add_field(name="Length", value=details["length"], inline=False)
                embed.add_field(name="YouTube", value=f"[Open in browser]({details['yt']})" if details["yt"] else "None", inline=False)
                embed.add_field(name="Music", value=f"{details['music_name']} by {details['music_artist']}", inline=False)
                embed.add_field(name="NG ID", value=details["music_ngid"], inline=False)
                embed.add_field(name="In-game ID", value=details["igid"], inline=False)
                embed.add_field(name="Recorder notes", value=details["recorder_notes"] or "None", inline=False)
                embed.add_field(name="Recorder name", value=details["recorder_name"], inline=False)

            case "music":
                embed.add_field(name="Name", value=details["name"], inline=False)
                embed.add_field(name="Artist", value=details["artist"], inline=False)
                embed.add_field(name="Length", value=details["length"], inline=False)
                embed.add_field(name="Type", value=details["type"] or "Unknown", inline=False)
                embed.add_field(name="YouTube", value=f"[Open in browser]({details['yt']})" if details["yt"] else "None", inline=False)
                embed.add_field(name="SoundCloud", value=f"[Open in browser]({details['soundcloud']})" if details["soundcloud"] else "None", inline=False)
                embed.add_field(name="Newgrounds ID", value=details["ngid"] or "None", inline=False)
                embed.add_field(name="Recorder notes", value=details["recorder_notes"] or "None", inline=False)
                embed.add_field(name="Recorder name", value=details["recorder_name"], inline=False)

            case "artist":
                embed.add_field(name="Name", value=details["name"], inline=False)
                embed.add_field(name="YouTube", value=f"[Open in browser]({details['yt']})" if details["yt"] else "None", inline=False)
                embed.add_field(name="SoundCloud", value=f"[Open in browser]({details['soundcloud']})" if details["soundcloud"] else "None", inline=False)
                embed.add_field(name="Recorder notes", value=details["recorder_notes"] or "None", inline=False)
                embed.add_field(name="Recorder name", value=details["recorder_name"], inline=False)

        embed.set_footer(text="Gameplay Database", icon_url=self.bot.user.avatar)
        embed.set_thumbnail(url=self.bot.user.avatar)

        view = ReviewRequestView(request_type=type_, request_id=id_)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)



            
        
        

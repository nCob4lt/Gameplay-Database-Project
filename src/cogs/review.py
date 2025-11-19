"""
ReviewCog module for the Gameplay Database bot.

This cog handles the moderation and review of pending registration requests
for creators, layouts, collabs, musics, and artists. It provides an interface
for moderators to view detailed information about the oldest pending request
and approve or reject it through a Discord UI with interactive buttons.

Classes
-------
ReviewCog(commands.Cog)
    Cog that provides a command to review the next pending database registration request.
"""

import discord
from discord.ext import commands

import database
from exceptions.custom_exceptions import DataNotFound
from utilities.applogger import AppLogger
from views.requestview import ReviewRequestView
from utilities import tools

applogger = AppLogger()

class ReviewCog(commands.Cog):

    """
    Cog responsible for reviewing and managing pending database registration requests.

    Attributes
    ----------
    bot : commands.Bot
        The Discord bot instance used to send messages and interact with the API.
    """

    def __init__(self, bot: commands.Bot):

        """
        Initialize the ReviewCog with a Discord bot instance.

        Parameters
        ----------
        bot : commands.Bot
            The bot instance this cog will be attached to.
        """

        self.bot = bot

    @discord.app_commands.command(
        name="review_next_request",
        description="Displays the oldest pending registration or update request."
    )
    async def review_next_request(self, interaction: discord.Interaction):

        """
        Display the oldest pending registration or update request in the database.

        This command fetches the oldest request from all registration tables
        (`requestcreator`, `requestlayout`, `requestcollab`, `requestmusic`, `requestartist`)
        and update tables (`request_update_creator`, `request_update_layout`,
        `request_update_collab`, `request_update_music`, `request_update_artist`).

        Moderators can interact with the embed using a custom ReviewRequestView to
        approve or reject the request.

        The embed contains key details depending on the request type:
            - Registration requests: user/creator/layout/musical info, YouTube/SoundCloud links,
            IDs, masterlevels, and recorder notes.
            - Update requests: target ID, column being updated, old value, new value,
            and recorder name.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object representing the user's slash command invocation.

        Returns
        -------
        None
            Sends a paginated Discord embed with request details and an interactive view.

        Raises
        ------
        DataNotFound
            If there are no pending requests or if request details cannot be retrieved.
        """

        await tools.check_mod(interaction)
        
        try:
            next_request = database.get_oldest_request()
        except DataNotFound:
            await interaction.response.send_message("**No** pending requests at the moment.")
            applogger.error(f"No pending requests at the moment - Interaction user : {interaction.user.name} in {interaction.guild.name}")
            return
        
        type_, id_, date = next_request
        
        try:
            details = database.get_request_details(type_, id_)
        except DataNotFound:
            await interaction.response.send_message("Failed to fetch request details. Check logs for more info.")
            applogger.error(f"Failed to fetch request details - Interaction user : {interaction.user.name} in {interaction.guild.name}")
            return

        embed = discord.Embed(
            title=f"Pending {type_.replace('_', ' ').capitalize()} request",
            description=f"Submission date: {date}",
            color=discord.Color.dark_grey()
        )

        # REGISTRATION REQUESTS
        if type_ in ["creator", "layout", "collab", "music", "artist", "update_creator", "update_layout", "update_collab", "update_music", "update_artist"]:
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
                    embed.add_field(name="YouTube", value=f"[Open in browser]({details['yt']})" if details["yt"] else "None", inline=False)
                    embed.add_field(name="Music", value=f"{details['music_name']} by {details['music_artist']}", inline=False)
                    embed.add_field(name="NG ID", value=details["music_ngid"] or "None", inline=False)
                    embed.add_field(name="In-game ID", value=details["igid"] or "None", inline=False)
                    embed.add_field(name="Masterlevel", value=details["masterlevel"] or "None", inline=False)
                    embed.add_field(name="Recorder notes", value=details["recorder_notes"] or "None", inline=False)
                    embed.add_field(name="Recorder name", value=details["recorder_name"], inline=False)

                case "collab":
                    embed.add_field(name="Name", value=details["name"], inline=False)
                    embed.add_field(name="Host", value=details["host_name"], inline=False)
                    embed.add_field(name="Builders", value=details["builders_number"], inline=False)
                    embed.add_field(name="Length", value=details["length"], inline=False)
                    embed.add_field(name="YouTube", value=f"[Open in browser]({details['yt']})" if details["yt"] else "None", inline=False)
                    embed.add_field(name="Music", value=f"{details['music_name']} by {details['music_artist']}", inline=False)
                    embed.add_field(name="NG ID", value=details["music_ngid"] or "None", inline=False)
                    embed.add_field(name="In-game ID", value=details["igid"] or "None", inline=False)
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

                case "update_creator":
                    embed.add_field(name="Target ID", value=details["target_id"], inline=False)
                    embed.add_field(name="Column", value=details["column_name"], inline=False)
                    embed.add_field(name="Old Value", value=details["old_value"] or "None", inline=False)
                    embed.add_field(name="New Value", value=details["new_value"] or "None", inline=False)
                    embed.add_field(name="Recorder", value=details["recorder_name"], inline=False)
                    embed.add_field(name="Submission Date", value=details["registration_date"], inline=False)

                case "update_layout":
                    embed.add_field(name="Target ID", value=details["target_id"], inline=False)
                    embed.add_field(name="Column", value=details["column_name"], inline=False)
                    embed.add_field(name="Old Value", value=details["old_value"] or "None", inline=False)
                    embed.add_field(name="New Value", value=details["new_value"] or "None", inline=False)
                    embed.add_field(name="Recorder", value=details["recorder_name"], inline=False)
                    embed.add_field(name="Submission Date", value=details["registration_date"], inline=False)

                case "update_collab":
                    embed.add_field(name="Target ID", value=details["target_id"], inline=False)
                    embed.add_field(name="Column", value=details["column_name"], inline=False)
                    embed.add_field(name="Old Value", value=details["old_value"] or "None", inline=False)
                    embed.add_field(name="New Value", value=details["new_value"] or "None", inline=False)
                    embed.add_field(name="Recorder", value=details["recorder_name"], inline=False)
                    embed.add_field(name="Submission Date", value=details["registration_date"], inline=False)

                case "update_music":
                    embed.add_field(name="Target ID", value=details["target_id"], inline=False)
                    embed.add_field(name="Column", value=details["column_name"], inline=False)
                    embed.add_field(name="Old Value", value=details["old_value"] or "None", inline=False)
                    embed.add_field(name="New Value", value=details["new_value"] or "None", inline=False)
                    embed.add_field(name="Recorder", value=details["recorder_name"], inline=False)
                    embed.add_field(name="Submission Date", value=details["registration_date"], inline=False)

                case "update_artist":
                    embed.add_field(name="Target ID", value=details["target_id"], inline=False)
                    embed.add_field(name="Column", value=details["column_name"], inline=False)
                    embed.add_field(name="Old Value", value=details["old_value"] or "None", inline=False)
                    embed.add_field(name="New Value", value=details["new_value"] or "None", inline=False)
                    embed.add_field(name="Recorder", value=details["recorder_name"], inline=False)
                    embed.add_field(name="Submission Date", value=details["registration_date"], inline=False)

                case _:
                    await interaction.response.edit_message(
                        content=f"❌ Unknown request type: {self.request_type}",
                        embed=None,
                        view=None
                    )
                    applogger.error(f"Unknown request type {self.request_type}")
                    return


        embed.set_footer(text="Gameplay Database", icon_url=self.bot.user.avatar)
        embed.set_thumbnail(url=self.bot.user.avatar)

        view = ReviewRequestView(request_type=type_, request_id=id_)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)




            
        
        

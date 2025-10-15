import discord
import database

from utilities.applogger import AppLogger
from exceptions.custom_exceptions import DataNotFound

applogger = AppLogger()

class ReviewRequestView(discord.ui.View):

    def __init__(self, request_type, request_id):

        super().__init__(timeout=None)
        self.request_type = request_type
        self.request_id = request_id

    @discord.ui.button(label="✅ Accept", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):

        try:
            details = database.get_request_details(self.request_type, self.request_id)
        except DataNotFound:
            await interaction.response.edit_message(content="**Failed** to fetch request details, check traceback for more info",
                                                     embed=None,
                                                       view=None)
            return
        
        match self.request_type:

            case "creator":
                
                await database.database_queue.put((
                    database.register_creator,
                    (
                        details["username"],
                        details["nationality"],
                        details["discord"],
                        details["discord_uid"],
                        details["yt"],
                        interaction.user.name,  # registrator
                    ),
                    {}
                ))

            case "layout":
                await database.database_queue.put((
                    database.register_layout,
                    (
                        details["creator_name"],
                        details["name"],
                        details["length"],
                        details["yt"],
                        details["music_name"],
                        details["music_artist"],
                        details["music_ngid"],
                        details["type"],
                        details["igid"],
                        details["masterlevel"],
                        details["recorder_notes"],
                        interaction.user.name,  # registrator
                    ),
                    {}
                ))

            case "collab":
                await database.database_queue.put((
                    database.register_collab,
                    (
                        details["host_name"],
                        details["name"],
                        details["builders_number"],
                        details["length"],
                        details["yt"],
                        details["music_name"],
                        details["music_artist"],
                        details["music_ngid"],
                        details["igid"],
                        interaction.user.name,  # registrator
                        details["recorder_notes"],
                    ),
                    {}
                ))

            case "music":
                await database.database_queue.put((
                    database.register_music,
                    (
                        details["name"],
                        details["artist"],
                        details["length"],
                        details["type"],
                        details["yt"],
                        details["soundcloud"],
                        details["ngid"],
                        interaction.user.name,  # registrator
                        details["recorder_notes"],
                    ),
                    {}
                ))

            case "artist":
                await database.database_queue.put((
                    database.register_artist,
                    (
                        details["name"],
                        details["yt"],
                        details["soundcloud"],
                        interaction.user.name,  # registrator
                        details["recorder_notes"],
                    ),
                    {}
                ))

            case _:
                await interaction.response.edit_message(
                    content=f"❌ Unknown request type: {self.request_type}",
                    embed=None,
                    view=None
                )
                applogger.error(f"Unknown request type {self.request_type}")
                return
            
        database.delete_request(self.request_type, self.request_id)

        await interaction.response.edit_message(content="✅ Request **accepted** and **processed!**", embed=None, view=None)
        applogger.info(f"Request {self.request_type} ID: {self.request_id} accepted by {interaction.user}")

    @discord.ui.button(label="❌ Reject", style=discord.ButtonStyle.danger)
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        database.delete_request(self.request_type, self.request_id)
        await interaction.response.edit_message(content="❌ Request **rejected** and **deleted.**", embed=None, view=None)
        applogger.warning(f"Request {self.request_type} #{self.request_id} rejected by {interaction.user}")

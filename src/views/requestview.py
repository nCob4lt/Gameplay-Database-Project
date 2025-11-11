import discord
import database

from utilities.applogger import AppLogger
from exceptions.custom_exceptions import DataNotFound

applogger = AppLogger()

class ReviewRequestView(discord.ui.View):

    """
    A Discord UI View for reviewing pending registration requests in the Gameplay Database.

    This view provides "Accept" and "Reject" buttons to allow moderators to approve or reject 
    pending requests for creators, layouts, collabs, music, or artists. Upon accepting, the request 
    is processed and added to the database asynchronously. Rejected requests are removed without 
    being processed.

    Attributes
    ----------
    request_type : str
        The type of the registration request (e.g., "creator", "layout", "collab", "music", "artist").
    request_id : int
        The unique identifier of the pending request in the database.
    """

    def __init__(self, request_type, request_id):

        """
        Initialize the ReviewRequestView with the type and ID of the request.

        Parameters
        ----------
        request_type : str
            The type of request to review.
        request_id : int
            The ID of the request to review.
        """

        super().__init__(timeout=None)
        self.request_type = request_type
        self.request_id = request_id

    @discord.ui.button(label="✅ Accept", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):

        """
        Accept and process the pending request.

        Fetches request details from the database and enqueues the corresponding registration 
        function to add it permanently. Only valid request types are processed. Upon completion, 
        the request is removed from the queue.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction triggered by clicking the "Accept" button.
        button : discord.ui.Button
            The button that was clicked.

        Notes
        -----
        - Supports request types: "creator", "layout", "collab", "music", "artist".
        - Unknown request types will log an error and abort processing.
        - Database operations are enqueued to `database.database_queue` for asynchronous execution.
        """

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
                        details["gdusername"],
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
        applogger.info(f"Request {self.request_type} ID: {self.request_id} accepted by {interaction.user} in {interaction.guild.name}")

    @discord.ui.button(label="❌ Reject", style=discord.ButtonStyle.danger)
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):

        """
        Reject and delete the pending request.

        Removes the request from the database without processing it.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction triggered by clicking the "Reject" button.
        button : discord.ui.Button
            The button that was clicked.
        """
        
        database.delete_request(self.request_type, self.request_id)
        await interaction.response.edit_message(content="❌ Request **rejected** and **deleted.**", embed=None, view=None)
        applogger.warning(f"Request {self.request_type} #{self.request_id} rejected by {interaction.user} in {interaction.guild.name}")

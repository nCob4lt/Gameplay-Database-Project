import discord

class PaginatorView(discord.ui.View):

    """
    A Discord UI View for paginating through multiple embeds with "Previous" and "Next" buttons.

    This view is designed to display a series of embeds and allows a specific user to navigate 
    between them using buttons. The buttons are automatically enabled or disabled depending on 
    the current page index. Only the user who initiated the pagination can control the navigation.

    Attributes
    ----------
    embeds : list[discord.Embed]
        A list of embeds to paginate through.
    current_page : int
        The index of the currently displayed embed.
    user : discord.User
        The Discord user who is allowed to control the pagination.
    """

    def __init__(self, embeds: list[discord.Embed], user: discord.User, timeout: int = 60):

        """
        Initialize the PaginatorView with embeds and the controlling user.

        Parameters
        ----------
        embeds : list[discord.Embed]
            The embeds to display in the pagination.
        user : discord.User
            The user who can interact with the pagination buttons.
        timeout : int, optional
            The time in seconds before the view times out (default is 60 seconds).
        """

        super().__init__(timeout=timeout)
        self.embeds = embeds
        self.current_page = 0
        self.user = user

        self.previous.disabled = True
        if len(embeds) == 1:
            self.next.disabled = True

    async def update_buttons(self, interaction: discord.Interaction):

        """
        Update the state of the pagination buttons and edit the message to show the current embed.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction that triggered the update, used to edit the message.
        """

        self.previous.disabled = (self.current_page == 0)
        self.next.disabled = (self.current_page == len(self.embeds) - 1)
        await interaction.message.edit(embed=self.embeds[self.current_page], view=self)

    @discord.ui.button(label="←", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):

        """
        Handle the "Previous" button click to navigate to the previous embed.

        Only the designated user can interact with this button. If the user is not allowed, 
        a private ephemeral message is sent.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction triggered by clicking the button.
        button : discord.ui.Button
            The button that was clicked.
        """
        
        if interaction.user != self.user:
            return await interaction.response.send_message("You can't control this pagination.", ephemeral=True)
        self.current_page -= 1
        await self.update_buttons(interaction)
        await interaction.response.defer()

    @discord.ui.button(label="→", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):

        """
        Handle the "Next" button click to navigate to the next embed.

        Only the designated user can interact with this button. If the user is not allowed, 
        a private ephemeral message is sent.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction triggered by clicking the button.
        button : discord.ui.Button
            The button that was clicked.
        """
        
        if interaction.user != self.user:
            return await interaction.response.send_message("You can't control this pagination.", ephemeral=True)
        self.current_page += 1
        await self.update_buttons(interaction)
        await interaction.response.defer()

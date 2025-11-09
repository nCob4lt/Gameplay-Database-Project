import discord

class PaginatorView(discord.ui.View):
    def __init__(self, embeds: list[discord.Embed], user: discord.User, timeout: int = 60):
        super().__init__(timeout=timeout)
        self.embeds = embeds
        self.current_page = 0
        self.user = user

        # On désactive le bouton "Précédent" au début
        self.previous.disabled = True
        if len(embeds) == 1:
            self.next.disabled = True

    async def update_buttons(self, interaction: discord.Interaction):
        self.previous.disabled = (self.current_page == 0)
        self.next.disabled = (self.current_page == len(self.embeds) - 1)
        await interaction.message.edit(embed=self.embeds[self.current_page], view=self)

    @discord.ui.button(label="←", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            return await interaction.response.send_message("You can't control this pagination.", ephemeral=True)
        self.current_page -= 1
        await self.update_buttons(interaction)
        await interaction.response.defer()

    @discord.ui.button(label="→", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            return await interaction.response.send_message("You can't control this pagination.", ephemeral=True)
        self.current_page += 1
        await self.update_buttons(interaction)
        await interaction.response.defer()

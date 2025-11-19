import discord
from discord.ext import commands

import database

class UpdateCog(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:

        """Initialize the RegistrationCog with a reference to the bot."""

        self.bot = bot

    def convert_value(self, attr: str, value: str):
        int_fields = ["discord_uid", "music_ngid", "igid"]
        if attr in int_fields:
            return int(value)
        return value
    
    def build_update_embed(self, interaction: discord.Interaction, table: str, entry):

        embed = discord.Embed(
            title="Update (mod action)",
            description=f"{table.capitalize()} successfully updated",
            color=discord.Color.dark_grey()
        )

        get = dict(entry[0])

        
        for key, val in get.items():
            embed.add_field(
                name=key.replace("_", " ").capitalize(),
                value=val if val is not None else "None",
                inline=False
            )

        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text="Gameplay Database", icon_url=interaction.client.user.avatar)
        embed.set_thumbnail(url=interaction.client.user.avatar)

        return embed
    
    @discord.app_commands.command(
        name="update_creator",
        description="Update a field of an existing creator (mod action)"
    )
    @discord.app_commands.describe(
        id="Creator ID",
        field="Field to modify",
        value="New value"
    )
    @discord.app_commands.choices(
        field=[
            discord.app_commands.Choice(name="Discord", value="discord"),
            discord.app_commands.Choice(name="Discord UID", value="discord_uid"),
            discord.app_commands.Choice(name="YouTube", value="yt"),
            discord.app_commands.Choice(name="GD Username", value="gdusername"),
        ]
    )
    async def update_creator(self, interaction: discord.Interaction, id: int, field: discord.app_commands.Choice[str], value: str):
        await interaction.response.defer()

        table = "creator"
        attr = field.value
        converted = self.convert_value(attr, value)

        old_entry = database.get_creator_by_id(id)
        old_value = dict(old_entry[0]).get(attr, None) if old_entry else None

        await database.database_queue.put((database.update, (table, id, attr, converted), {}))

        embed = discord.Embed(
            title=f"Update on {table.capitalize()}",
            description=f"{table.capitalize()} entry updated successfully.",
            color=discord.Color.dark_grey()
        )

        embed.add_field(name="ID", value=str(id), inline=False)
        embed.add_field(name="Column", value=f"``{attr}``", inline=False)
        embed.add_field(name="Old Value", value=str(old_value) if old_value is not None else "None", inline=False)
        embed.add_field(name="New Value", value=str(converted) if converted is not None else "None", inline=False)

        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text="Gameplay Database", icon_url=interaction.client.user.avatar)
        embed.set_thumbnail(url=interaction.client.user.avatar)

        await interaction.followup.send(embed=embed)


    @discord.app_commands.command(
        name="update_layout",
        description="Update a field of an existing layout (mod action)"
    )
    @discord.app_commands.describe(
        id="Layout ID",
        field="Field to modify",
        value="New value"
    )
    @discord.app_commands.choices(
        field=[
            discord.app_commands.Choice(name="YouTube", value="yt"),
            discord.app_commands.Choice(name="Music NG ID", value="music_ngid"),
            discord.app_commands.Choice(name="IGID", value="igid"),
        ]
    )
    async def update_layout(self, interaction: discord.Interaction, id: int, field: discord.app_commands.Choice[str], value: str):
        await interaction.response.defer()

        table = "layout"
        attr = field.value
        converted = self.convert_value(attr, value)

        old_entry = database.get_layout_by_id(id)
        old_value = dict(old_entry[0]).get(attr, None) if old_entry else None

        await database.database_queue.put((database.update, (table, id, attr, converted), {}))

        embed = discord.Embed(
            title=f"Update on {table.capitalize()}",
            description=f"{table.capitalize()} entry updated successfully.",
            color=discord.Color.dark_grey()
        )
        embed.add_field(name="ID", value=str(id), inline=False)
        embed.add_field(name="Column", value=f"``{attr}``", inline=False)
        embed.add_field(name="Old Value", value=str(old_value) if old_value is not None else "None", inline=False)
        embed.add_field(name="New Value", value=str(converted) if converted is not None else "None", inline=False)

        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text="Gameplay Database", icon_url=interaction.client.user.avatar)
        embed.set_thumbnail(url=interaction.client.user.avatar)

        await interaction.followup.send(embed=embed)


    @discord.app_commands.command(
        name="update_collab",
        description="Update a field of an existing collab (mod action)"
    )
    @discord.app_commands.describe(
        id="Collab ID",
        field="Field to modify",
        value="New value"
    )
    @discord.app_commands.choices(
        field=[
            discord.app_commands.Choice(name="YouTube", value="yt"),
            discord.app_commands.Choice(name="Music NG ID", value="music_ngid"),
            discord.app_commands.Choice(name="IGID", value="igid"),
        ]
    )
    async def update_collab(self, interaction: discord.Interaction, id: int, field: discord.app_commands.Choice[str], value: str):
        await interaction.response.defer()

        table = "collab"
        attr = field.value
        converted = self.convert_value(attr, value)

        old_entry = database.get_collab_by_id(id)
        old_value = dict(old_entry[0]).get(attr, None) if old_entry else None

        await database.database_queue.put((database.update, (table, id, attr, converted), {}))

        embed = discord.Embed(
            title=f"Update on {table.capitalize()}",
            description=f"{table.capitalize()} entry updated successfully.",
            color=discord.Color.dark_grey()
        )
        embed.add_field(name="ID", value=str(id), inline=False)
        embed.add_field(name="Column", value=f"``{attr}``", inline=False)
        embed.add_field(name="Old Value", value=str(old_value) if old_value is not None else "None", inline=False)
        embed.add_field(name="New Value", value=str(converted) if converted is not None else "None", inline=False)

        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text="Gameplay Database", icon_url=interaction.client.user.avatar)
        embed.set_thumbnail(url=interaction.client.user.avatar)

        await interaction.followup.send(embed=embed)


    @discord.app_commands.command(
        name="update_music",
        description="Update a field of an existing music entry (mod action)"
    )
    @discord.app_commands.describe(
        id="Music ID",
        field="Field to modify",
        value="New value"
    )
    @discord.app_commands.choices(
        field=[
            discord.app_commands.Choice(name="Type", value="type"),
            discord.app_commands.Choice(name="YouTube", value="yt"),
            discord.app_commands.Choice(name="SoundCloud", value="soundcloud"),
        ]
    )
    async def update_music(self, interaction: discord.Interaction, id: int, field: discord.app_commands.Choice[str], value: str):
        await interaction.response.defer()

        table = "music"
        attr = field.value
        converted = self.convert_value(attr, value)

        old_entry = database.get_music_by_id(id)
        old_value = dict(old_entry[0]).get(attr, None) if old_entry else None

        await database.database_queue.put((database.update, (table, id, attr, converted), {}))

        embed = discord.Embed(
            title=f"Update on {table.capitalize()}",
            description=f"{table.capitalize()} entry updated successfully.",
            color=discord.Color.dark_grey()
        )
        embed.add_field(name="ID", value=str(id), inline=False)
        embed.add_field(name="Column", value=f"``{attr}``", inline=False)
        embed.add_field(name="Old Value", value=str(old_value) if old_value is not None else "None", inline=False)
        embed.add_field(name="New Value", value=str(converted) if converted is not None else "None", inline=False)

        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text="Gameplay Database", icon_url=interaction.client.user.avatar)
        embed.set_thumbnail(url=interaction.client.user.avatar)

        await interaction.followup.send(embed=embed)


    @discord.app_commands.command(
        name="update_artist",
        description="Update a field of an existing artist (mod action)"
    )
    @discord.app_commands.describe(
        id="Artist ID",
        field="Field to modify",
        value="New value"
    )
    @discord.app_commands.choices(
        field=[
            discord.app_commands.Choice(name="YouTube", value="yt"),
            discord.app_commands.Choice(name="SoundCloud", value="soundcloud"),
        ]
    )
    async def update_artist(self, interaction: discord.Interaction, id: int, field: discord.app_commands.Choice[str], value: str):
        await interaction.response.defer()

        table = "artist"
        attr = field.value
        converted = self.convert_value(attr, value)

        old_entry = database.get_artist_by_id(id)
        old_value = dict(old_entry[0]).get(attr, None) if old_entry else None

        await database.database_queue.put((database.update, (table, id, attr, converted), {}))

        embed = discord.Embed(
            title=f"Update on {table.capitalize()}",
            description=f"{table.capitalize()} entry updated successfully.",
            color=discord.Color.dark_grey()
        )
        embed.add_field(name="ID", value=str(id), inline=False)
        embed.add_field(name="Column", value=f"``{attr}``", inline=False)
        embed.add_field(name="Old Value", value=str(old_value) if old_value is not None else "None", inline=False)
        embed.add_field(name="New Value", value=str(converted) if converted is not None else "None", inline=False)

        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text="Gameplay Database", icon_url=interaction.client.user.avatar)
        embed.set_thumbnail(url=interaction.client.user.avatar)

        await interaction.followup.send(embed=embed)





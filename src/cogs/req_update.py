import discord
from discord.ext import commands

import database
from utilities import tools
from exceptions.custom_exceptions import *
from utilities.applogger import AppLogger

applogger = AppLogger()

class RequestUpdateCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(
        name="request_update_creator",
        description="Registers a request to update a creator entry in the Gameplay Database"
    )
    @discord.app_commands.describe(
        id="ID of the creator to update",
        field="Field to modify",
        value="New value for the field"
    )
    @discord.app_commands.choices(
        field=[
            discord.app_commands.Choice(name="Discord", value="discord"),
            discord.app_commands.Choice(name="Discord UID", value="discord_uid"),
            discord.app_commands.Choice(name="YouTube", value="yt"),
            discord.app_commands.Choice(name="GD Username", value="gdusername"),
        ]
    )
    async def request_update_creator(self, interaction: discord.Interaction, id: int, field: discord.app_commands.Choice[str], value: str):
        await interaction.response.defer()
        
        attr = field.value
        converted = tools.convert_value(attr, value)

        try:
            old_entry = database.get_creator_by_id(id)
        except DataNotFound:
            applogger.error(f"Tried to request an update for a non-existent entry on {interaction.command.name} ran by {interaction.user.name} in {interaction.guild.name} | ID : {id}")
            await interaction.followup.send("The entry with the given ID does **not** exist.")
            return
        old_value = dict(old_entry[0]).get(attr, None) if old_entry else None
        registrator = interaction.user.name

        await database.database_queue.put((
            database.register_update_creator,
            (id, attr, old_value, converted, registrator),
            {}
        ))

        embed = discord.Embed(
            title=f"Update request on Creator",
            description="Creator update request successfully submitted.",
            color=discord.Color.dark_grey()
        )
        embed.add_field(name="ID", value=id, inline=False)
        embed.add_field(name="Column", value=f"``{attr}``", inline=False)
        embed.add_field(name="Old Value", value=str(old_value) if old_value is not None else "None", inline=False)
        embed.add_field(name="New Value", value=str(converted) if converted is not None else "None", inline=False)
        embed.add_field(name="Recorder", value=registrator, inline=False)

        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text="Gameplay Database", icon_url=interaction.client.user.avatar)
        embed.set_thumbnail(url=interaction.client.user.avatar)

        applogger.debug_command(interaction)
        await interaction.followup.send(embed=embed)


    # ------------------ REQUEST UPDATE LAYOUT ------------------
    @discord.app_commands.command(
        name="request_update_layout",
        description="Registers a request to update a layout entry in the Gameplay Database"
    )
    @discord.app_commands.describe(
        id="ID of the layout to update",
        field="Field to modify",
        value="New value for the field"
    )
    @discord.app_commands.choices(
        field=[
            discord.app_commands.Choice(name="YouTube", value="yt"),
            discord.app_commands.Choice(name="Music NG ID", value="music_ngid"),
            discord.app_commands.Choice(name="IGID", value="igid"),
        ]
    )
    async def request_update_layout(self, interaction: discord.Interaction, id: int, field: discord.app_commands.Choice[str], value: str):
        await interaction.response.defer()
        
        attr = field.value
        converted = tools.convert_value(attr, value)

        try:
            old_entry = database.get_layout_by_id(id)
        except DataNotFound:
            applogger.error(f"Tried to request an update for a non-existent entry on {interaction.command.name} ran by {interaction.user.name} in {interaction.guild.name} | ID : {id}")
            await interaction.followup.send("The entry with the given ID does **not** exist.")
            return
        old_value = dict(old_entry[0]).get(attr, None) if old_entry else None
        registrator = interaction.user.name

        await database.database_queue.put((
            database.register_update_layout,
            (id, attr, old_value, converted, registrator),
            {}
        ))

        embed = discord.Embed(
            title=f"Update request on Layout",
            description="Layout update request successfully submitted.",
            color=discord.Color.dark_grey()
        )
        embed.add_field(name="ID", value=id, inline=False)
        embed.add_field(name="Column", value=f"``{attr}``", inline=False)
        embed.add_field(name="Old Value", value=str(old_value) if old_value is not None else "None", inline=False)
        embed.add_field(name="New Value", value=str(converted) if converted is not None else "None", inline=False)
        embed.add_field(name="Recorder", value=registrator, inline=False)

        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text="Gameplay Database", icon_url=interaction.client.user.avatar)
        embed.set_thumbnail(url=interaction.client.user.avatar)

        applogger.debug_command(interaction)
        await interaction.followup.send(embed=embed)


    # ------------------ REQUEST UPDATE COLLAB ------------------
    @discord.app_commands.command(
        name="request_update_collab",
        description="Registers a request to update a collab entry in the Gameplay Database"
    )
    @discord.app_commands.describe(
        id="ID of the collab to update",
        field="Field to modify",
        value="New value for the field"
    )
    @discord.app_commands.choices(
        field=[
            discord.app_commands.Choice(name="YouTube", value="yt"),
            discord.app_commands.Choice(name="Music NG ID", value="music_ngid"),
            discord.app_commands.Choice(name="IGID", value="igid"),
        ]
    )
    async def request_update_collab(self, interaction: discord.Interaction, id: int, field: discord.app_commands.Choice[str], value: str):
        await interaction.response.defer()
        
        attr = field.value
        converted = tools.convert_value(attr, value)

        try:
            old_entry = database.get_collab_by_id(id)
        except DataNotFound:
            applogger.error(f"Tried to request an update for a non-existent entry on {interaction.command.name} ran by {interaction.user.name} in {interaction.guild.name} | ID : {id}")
            await interaction.followup.send("The entry with the given ID does **not** exist.")
            return
        old_value = dict(old_entry[0]).get(attr, None) if old_entry else None
        registrator = interaction.user.name

        await database.database_queue.put((
            database.register_update_collab,
            (id, attr, old_value, converted, registrator),
            {}
        ))

        embed = discord.Embed(
            title=f"Update request on Collab",
            description="Collab update request successfully submitted.",
            color=discord.Color.dark_grey()
        )
        embed.add_field(name="ID", value=id, inline=False)
        embed.add_field(name="Column", value=f"``{attr}``", inline=False)
        embed.add_field(name="Old Value", value=str(old_value) if old_value is not None else "None", inline=False)
        embed.add_field(name="New Value", value=str(converted) if converted is not None else "None", inline=False)
        embed.add_field(name="Recorder", value=registrator, inline=False)

        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text="Gameplay Database", icon_url=interaction.client.user.avatar)
        embed.set_thumbnail(url=interaction.client.user.avatar)

        applogger.debug_command(interaction)
        await interaction.followup.send(embed=embed)


    # ------------------ REQUEST UPDATE MUSIC ------------------
    @discord.app_commands.command(
        name="request_update_music",
        description="Registers a request to update a music entry in the Gameplay Database"
    )
    @discord.app_commands.describe(
        id="ID of the music to update",
        field="Field to modify",
        value="New value for the field"
    )
    @discord.app_commands.choices(
        field=[
            discord.app_commands.Choice(name="Type", value="type"),
            discord.app_commands.Choice(name="YouTube", value="yt"),
            discord.app_commands.Choice(name="SoundCloud", value="soundcloud"),
        ]
    )
    async def request_update_music(self, interaction: discord.Interaction, id: int, field: discord.app_commands.Choice[str], value: str):
        await interaction.response.defer()
        
        attr = field.value
        converted = tools.convert_value(attr, value)

        try:
            old_entry = database.get_music_by_id(id)
        except DataNotFound:
            applogger.error(f"Tried to request an update for a non-existent entry on {interaction.command.name} ran by {interaction.user.name} in {interaction.guild.name} | ID : {id}")
            await interaction.followup.send("The entry with the given ID does **not** exist.")
            return
        old_value = dict(old_entry[0]).get(attr, None) if old_entry else None
        registrator = interaction.user.name

        await database.database_queue.put((
            database.register_update_music,
            (id, attr, old_value, converted, registrator),
            {}
        ))

        embed = discord.Embed(
            title=f"Update request on Music",
            description="Music update request successfully submitted.",
            color=discord.Color.dark_grey()
        )
        embed.add_field(name="ID", value=id, inline=False)
        embed.add_field(name="Column", value=f"``{attr}``", inline=False)
        embed.add_field(name="Old Value", value=str(old_value) if old_value is not None else "None", inline=False)
        embed.add_field(name="New Value", value=str(converted) if converted is not None else "None", inline=False)
        embed.add_field(name="Recorder", value=registrator, inline=False)

        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text="Gameplay Database", icon_url=interaction.client.user.avatar)
        embed.set_thumbnail(url=interaction.client.user.avatar)

        applogger.debug_command(interaction)
        await interaction.followup.send(embed=embed)


    # ------------------ REQUEST UPDATE ARTIST ------------------
    @discord.app_commands.command(
        name="request_update_artist",
        description="Registers a request to update an artist entry in the Gameplay Database"
    )
    @discord.app_commands.describe(
        id="ID of the artist to update",
        field="Field to modify",
        value="New value for the field"
    )
    @discord.app_commands.choices(
        field=[
            discord.app_commands.Choice(name="YouTube", value="yt"),
            discord.app_commands.Choice(name="SoundCloud", value="soundcloud"),
            discord.app_commands.Choice(name="Name", value="name"),
            discord.app_commands.Choice(name="Recorder Notes", value="recorder_notes"),
        ]
    )
    async def request_update_artist(self, interaction: discord.Interaction, id: int, field: discord.app_commands.Choice[str], value: str):
        await interaction.response.defer()
        
        attr = field.value
        converted = tools.convert_value(attr, value)

        try:
            old_entry = database.get_artist_by_id(id)
        except DataNotFound:
            applogger.error(f"Tried to request an update for a non-existent entry on {interaction.command.name} ran by {interaction.user.name} in {interaction.guild.name} | ID : {id}")
            await interaction.followup.send("The entry with the given ID does **not** exist.")
            return
        old_value = dict(old_entry[0]).get(attr, None) if old_entry else None
        registrator = interaction.user.name

        await database.database_queue.put((
            database.register_update_artist,
            (id, attr, old_value, converted, registrator),
            {}
        ))

        embed = discord.Embed(
            title=f"Update request on Artist",
            description="Artist update request successfully submitted.",
            color=discord.Color.dark_grey()
        )
        embed.add_field(name="ID", value=id, inline=False)
        embed.add_field(name="Column", value=f"``{attr}``", inline=False)
        embed.add_field(name="Old Value", value=str(old_value) if old_value is not None else "None", inline=False)
        embed.add_field(name="New Value", value=str(converted) if converted is not None else "None", inline=False)
        embed.add_field(name="Recorder", value=registrator, inline=False)

        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text="Gameplay Database", icon_url=interaction.client.user.avatar)
        embed.set_thumbnail(url=interaction.client.user.avatar)

        applogger.debug_command(interaction)
        await interaction.followup.send(embed=embed)

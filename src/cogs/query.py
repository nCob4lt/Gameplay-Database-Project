import discord
from discord.ext import commands

import database

class QueryCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @discord.app_commands.command(name="get_creator_by_name", description="Retrieves data about a creator by giving name")
    @discord.app_commands.describe(username="Creator username")
    async def get_creator_by_name(self, interaction: discord.Interaction, username: str):
        
        get = database.get_creator_by_name(username)
        if not get:
            await interaction.response.send_message("**User** not found.")
            return

        embed = discord.Embed(
            title=f"Creator overview : {get[0][1]}",
            description="Infos -------------------------------------------------------------------",
            color=discord.Color.dark_grey()
        )

        embed.add_field(name="Username", value=get[0][1], inline=False)
        embed.add_field(name="Nationality", value=get[0][2], inline=False)
        embed.add_field(name="Discord", value=get[0][3], inline=False)
        embed.add_field(name="Discord uid", value=get[0][4], inline=False)
        embed.add_field(name="Youtube", value=f"[Open in browser]({get[0][5]})" if get[0][5] else None, inline=False)
        embed.add_field(name="Layouts registered", value=get[0][6], inline=False)
        embed.add_field(name="Collab participations", value=get[0][7], inline=False)
        embed.add_field(name="Total time built", value=get[0][8], inline=False)
        embed.add_field(name="Registration date", value=get[0][9], inline=False)
        embed.add_field(name="Recorder name", value=get[0][10], inline=False)

        await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="get_layout_by_name", description="Retrieves data about a layout by giving name")
    @discord.app_commands.describe(name="Layout name")
    async def get_layout_by_name(self, interaction: discord.Interaction, name: str):

        get = database.get_layout_by_name(name)
        if not get:
            await interaction.response.send_message("**Layout** not found.")
            return

        embed = discord.Embed(
            title=f"Layout overview : {get[0][4]}",
            description="Infos -------------------------------------------------------------------",
            color=discord.Color.dark_grey()
        )

        embed.add_field(name="Creator", value=get[0][2], inline=False)
        embed.add_field(name="Name", value=get[0][4], inline=False)
        embed.add_field(name="Type", value=get[0][3], inline=False)
        embed.add_field(name="Length", value=get[0][5], inline=False)
        embed.add_field(name="Youtube", value=f"[Open in browser]({get[0][6]})" if get[0][6] else None, inline=False)
        embed.add_field(name="Music NG ID", value=get[0][8], inline=False)
        embed.add_field(name="Music name", value=get[0][9], inline=False)
        embed.add_field(name="Music artist", value=get[0][10], inline=False)
        embed.add_field(name="In-game ID", value=get[0][11], inline=False)
        embed.add_field(name="Masterlevel", value=get[0][16], inline=False)
        embed.add_field(name="Registration date", value=get[0][12], inline=False)
        embed.add_field(name="Recorder name", value=get[0][13], inline=False)
        embed.add_field(name="Recorder notes", value=get[0][14], inline=False)
        

        await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="get_collab_by_name", description="Retrieves data about a collab by giving name")
    @discord.app_commands.describe(name="Collab name")
    async def get_collab_by_name(self, interaction: discord.Interaction, name: str):

        get = database.get_collab_by_name(name)
        if not get:
            await interaction.response.send_message("**Collab** not found.")
            return

        embed = discord.Embed(
            title=f"Collab overview : {get[0][3]}",
            description="Infos -------------------------------------------------------------------",
            color=discord.Color.dark_teal()
        )

        embed.add_field(name="Host", value=get[0][2], inline=False)
        embed.add_field(name="Name", value=get[0][3], inline=False)
        embed.add_field(name="Builders number", value=get[0][4], inline=False)
        embed.add_field(name="Length", value=get[0][5], inline=False)
        embed.add_field(name="Youtube", value=f"[Open in browser]({get[0][6]})" if get[0][6] else None, inline=False)
        embed.add_field(name="Music NG ID", value=get[0][8], inline=False)
        embed.add_field(name="Music name", value=get[0][9], inline=False)
        embed.add_field(name="Music artist", value=get[0][10], inline=False)
        embed.add_field(name="In-game ID", value=get[0][11], inline=False)
        embed.add_field(name="Registration date", value=get[0][12], inline=False)
        embed.add_field(name="Recorder name", value=get[0][13], inline=False)
        embed.add_field(name="Recorder notes", value=get[0][14], inline=False)

        await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="get_music_by_name", description="Retrieves data about a music by giving name")
    @discord.app_commands.describe(name="Music name")
    async def get_music_by_name(self, interaction: discord.Interaction, name: str):

        get = database.get_music_by_name(name)
        if not get:
            await interaction.response.send_message("**Music** not found.")
            return

        embed = discord.Embed(
            title=f"Music overview : {get[0][1]}",
            description="Infos -------------------------------------------------------------------",
            color=discord.Color.dark_gold()
        )

        embed.add_field(name="Name", value=get[0][1], inline=False)
        embed.add_field(name="Artist", value=get[0][2], inline=False)
        embed.add_field(name="Length", value=get[0][3], inline=False)
        embed.add_field(name="Type", value=get[0][4], inline=False)
        embed.add_field(name="Youtube", value=f"[Open in browser]({get[0][5]})" if get[0][5] else None, inline=False)
        embed.add_field(name="SoundCloud", value=f"[Open in browser]({get[0][6]})" if get[0][6] else None, inline=False)
        embed.add_field(name="Uses", value=get[0][7], inline=False)
        embed.add_field(name="NG ID", value=get[0][8], inline=False)
        embed.add_field(name="Registration date", value=get[0][9], inline=False)
        embed.add_field(name="Recorder name", value=get[0][10], inline=False)
        embed.add_field(name="Recorder notes", value=get[0][11], inline=False)

        await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="get_artist_by_name", description="Retrieves data about an artist by giving name")
    @discord.app_commands.describe(name="Artist name")
    async def get_artist_by_name(self, interaction: discord.Interaction, name: str):

        get = database.get_artist_by_name(name)
        if not get:
            await interaction.response.send_message("**Artist** not found.")
            return

        embed = discord.Embed(
            title=f"Artist overview : {get[0][1]}",
            description="Infos -------------------------------------------------------------------",
            color=discord.Color.dark_blue()
        )

        embed.add_field(name="Name", value=get[0][1], inline=False)
        embed.add_field(name="Youtube", value=f"[Open in browser]({get[0][2]})" if get[0][2] else None, inline=False)
        embed.add_field(name="Soundcloud", value=f"[Open in browser]({get[0][3]})" if get[0][3] else None, inline=False)
        embed.add_field(name="Songs registered", value=get[0][4], inline=False)
        embed.add_field(name="Total song uses", value=get[0][5], inline=False)
        embed.add_field(name="Registration date", value=get[0][6], inline=False)
        embed.add_field(name="Recorder name", value=get[0][7], inline=False)
        embed.add_field(name="Recorder notes", value=get[0][8], inline=False)

        await interaction.response.send_message(embed=embed)




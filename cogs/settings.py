#cogs/settings.py - displays guild settings and their current values

import discord
from discord.ext import commands

class SettingsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_settings = {}

    # Command to show the settings, which returns the name of the guild
    @commands.command(name='settings')
    async def settings(self, ctx):
        guild_id = ctx.guild.id
        guild_name = ctx.guild.name
        
        
        guild_id = ctx.guild.id
        guild_name = ctx.guild.name

        # Check if the guild is in the settings dictionary, if not, initialize it
        if guild_id not in self.guild_settings:
            self.guild_settings[guild_id] = {
                'Example Setting 1': 'Enabled',
                'Example Setting 2': 'Disabled',
                'Example Setting 3': 'True'
            }

        # Create an embed for the settings
        embed =discord.Embed(
            title="Settings",
            description="Bot settings and their current values.",
            color=discord.Color.green()
        )

        # Add each setting to the embed as a field
        for setting, value in self.guild_settings[guild_id].items():
            embed.add_field(name=setting, value=value, inline=False)

        # Send the embed message
        await ctx.send(embed=embed)

# Function to add the cog to the bot
async def setup(bot):
    await bot.add_cog(SettingsCog(bot))
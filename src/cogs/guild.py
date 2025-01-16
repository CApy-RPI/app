import discord
from datetime import datetime, timezone
from discord.ext import commands
from modules.timestamp import now, format_time


class Guild(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="settings", help="Manage server settings")
    async def settings(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid settings command. Use !settings [list, set]")

    @settings.command(name="list", help="List server settings")
    async def list_settings(self, ctx):
        guild = self.bot.db.get_data("guild", ctx.guild.id)
        embed = discord.Embed(
            title="Server Settings",
            color=discord.Color.green(),
        )
        embed.add_field(
            name="announcements_channel",
            value=guild.get_value("announcements_channel"),
            inline=False,
        )
        embed.add_field(
            name="moderator_channel",
            value=guild.get_value("moderator_channel"),
            inline=False,
        )
        embed.add_field(
            name="eboard_role", value=guild.get_value("eboard_role"), inline=False
        )

        await ctx.send(embed=embed)

    @settings.command(name="set", help="Change a server setting")
    @commands.has_permissions(administrator=True)
    async def modify_setting(self, ctx, name: str, value):
        guild = self.bot.db.get_data("guild", ctx.guild.id)
        try:
            previous_value = str(guild.get_value(name))
            guild.set_value(name, value)
            self.bot.db.upsert_data(guild)
            valid_embed = discord.Embed(
                title="Success!",
                description=f"'{name}' changed to '{value}' from '{previous_value}'.",
                color=discord.Color.green(),
            )
            await ctx.send(embed=valid_embed)
            return
        except KeyError as e:
            fail_embed = discord.Embed(
                title=f"Setting {name} does not exist!",
                description="Type the setting name exactly as shown",
                color=discord.Color.red(),
            )
            await ctx.send(embed=fail_embed)


# Setup function to load the cog
async def setup(bot):
    await bot.add_cog(Guild(bot))

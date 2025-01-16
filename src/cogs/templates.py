# THIS COG CONTAINS TEMPLATES FOR COMMANDS - NOT INTENDED FOR END USERS

import discord
import logging
from discord.ext import commands


class Templates(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = logging.getLogger(
            f"discord.cog.{self.__class__.__name__.lower()}"
        )

    #! Template code for a single command
    @commands.command(name="single", help="Shows the bot's latency.")
    async def single(self, ctx):
        message = f"⏱ {round(self.bot.latency * 1000)} ms Latency!"
        embed = discord.Embed(
            title="Ping",
            description=message,
            color=discord.Color.pink(),
        )
        self.logger.info(message)
        await ctx.send(embed=embed)

    #! Template code for a command that cannot be run without admin permissions
    @commands.command(name="admin_required", help="ADMIN - Shows the bot's latency.")
    @commands.has_permissions(administrator=True)
    async def admin_ping(self, ctx):
        message = f"⏱ {round(self.bot.latency * 1000)} ms Latency!"
        embed = discord.Embed(
            title="Ping (But better)",
            description=message,
            color=discord.Color.pink(),
        )
        self.logger.info(message)
        await ctx.send(embed=embed)

    #! Template code for a command that cannot be run without the set eboard role
    @commands.command(name="eboard_required", help="EBOARD - Shows the bot's latency.")
    async def eboard_ping(self, ctx):
        if self.bot.db.get_data("guild", ctx.guild.id).get_value("eboard_role") is None:
            embed = discord.Embed(
                title="eboard role not configured!",
                description="Use '!settings set eboard_role' to fix this",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)
            return

        if not commands.has_role(
            self.bot.db.get_data("guild", ctx.guild.id).get_value("eboard_role")
        ):
            embed = discord.Embed(
                title="Missing required eboard role!",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)
            return

        message = f"⏱ {round(self.bot.latency * 1000)} ms Latency!"
        embed = discord.Embed(
            title="Ping (But eboard)",
            description=message,
            color=discord.Color.pink(),
        )
        self.logger.info(message)
        await ctx.send(embed=embed)

    #! Template code for a command that can optionally run with additional admin functionality
    # w/ input of admin param. If the user attempts to run admin without permissions, the command will be run as usual.
    @commands.command(
        name="admin_optional",
        help="Shows the bot's latency, use optional admin param to change to red",
    )
    async def admin_optional(self, ctx, admin=None):
        message = f"⏱ {round(self.bot.latency * 1000)} ms Latency!"
        if admin == "admin" and ctx.message.author.guild_permissions.administrator:
            embed = discord.Embed(
                title="Ping (But better + red)",
                description=message,
                color=discord.Color.red(),
            )
        else:
            embed = discord.Embed(
                title="Ping",
                description=message,
                color=discord.Color.pink(),
            )
        self.logger.info(message)
        await ctx.send(embed=embed)

    #! Template code for a command group
    @commands.group(name="say", invoke_without_command=True, help="Says something.")
    async def say(self, ctx):
        embed = discord.Embed(
            title="Say",
            description="Say something!",
            color=discord.Color.pink(),
        )
        await ctx.send(embed=embed)

    # Here is one command in the group
    @say.command(name="hello", help="Says hello.")
    async def hello(self, ctx):
        embed = discord.Embed(
            title="Say",
            description="Hello!",
            color=discord.Color.pink(),
        )
        await ctx.send(embed=embed)

    # Here is another command in the group
    @say.command(name="goodbye", help="Says goodbye.")
    async def goodbye(self, ctx):
        embed = discord.Embed(
            title="Say",
            description="Goodbye!",
            color=discord.Color.pink(),
        )
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Templates(bot))

# cogs.ping.py - displays the bot's latency (for testing)
#              - serves as a template cog

import discord
import logging
from discord.ext import commands


class Ping(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = logging.getLogger(
            f"discord.cog.{self.__class__.__name__.lower()}"
        )

    #! Template code for a single command
    @commands.command(name="ping", help="Shows the bot's latency.")
    async def ping(self, ctx):
        message = f"⏱ {round(self.bot.latency * 1000)} ms Latency!"
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
    await bot.add_cog(Ping(bot))

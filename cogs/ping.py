# cogs.ping.py - displays the bot's latency (for testing)

import discord
import logging
from discord.ext import commands


class Ping(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = logging.getLogger(
            f"discord.cog.{self.__class__.__name__.lower()}"
        )

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


async def setup(bot: commands.Bot):
    await bot.add_cog(Ping(bot))

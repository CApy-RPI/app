import discord
import logging
from discord.ext import commands


class Ping(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = logging.getLogger(
            f"discord.cog.{self.__class__.__name__.lower()}"
        )

    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.info(f"{self.__class__.__name__} is loaded.")

    @commands.command(pass_context=True)
    async def ping(self, ctx):
        message = f"⏱|** {round(self.bot.latency * 1000)} ms** Latency!"
        self.logger.info(message)
        await ctx.send(message)


async def setup(bot: commands.Bot):
    await bot.add_cog(Ping(bot))

import discord
import logging
from discord.ext import commands


class Profile(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = logging.getLogger(
            f"discord.cog.{self.__class__.__name__.lower()}"
        )

    @commands.command(name="profile", help="Shows your profile.")
    async def profile(self, ctx):
        # embed = discord.Embed(
        #     title= ctx.author.display_name + "'s Profile",
        #     description=ctx.author.mention,
        #     color=discord.Color.purple(),
        # )

        # embed.set_thumbnail(url=ctx.author.avatar_url)
        # embed.add_field(name="Name", value=ctx.author.display_name, inline=True)
        # embed.add_field(name="ID", value=ctx.author.id, inline=True)
        # await ctx.send(embed=embed)

        dm_embed = discord.Embed(
            title="Welcome to the RPI Discord!",
            description="We're excited to have you here! Before we get started, we need some information from you to create your profile. Please follow these steps:",
            color=discord.Color.purple(),
        )

        dm_embed.add_field(
            name="Step 1: DM the bot",
            value="DM this bot with the following information:\n\n"
            "1. Your name (first and last)\n"
            "2. Your major\n"
            "3. Your graduation year (YYYY)\n"
            "4. Any other information you want to share (optional)\n",
            inline=False,
        )

        dm_embed.add_field(
            name="Step 2: Wait for the bot to respond",
            value="After you've sent the information, the bot will respond with a confirmation message. If you don't see the message, check your DMs for any errors.",
            inline=False,
        )

        await ctx.author.send(embed=dm_embed)
async def setup(bot: commands.Bot):
    await bot.add_cog(Profile(bot))

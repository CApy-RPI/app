import discord
from discord.ext import commands
import logging

class Update(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(
            f"discord.cog.{self.__class__.__name__.lower()}"
        )

    @commands.command(name="update", help="Update your profile with new information.")
    async def update(self, ctx):

        # Create an embed with a welcome message
        aspects = ["First Name", "Last Name", "Major", "Graduation Year", "RIN", "RPI Email"]
        aspects_embed = discord.Embed(
            title="Update Page",
            description="What aspect do you want to update?\n".join([f"{i+1}. {aspect}" for i, aspect in enumerate(aspects)]),
            color=discord.Color.pink(),
        )
        await ctx.send(embed=aspects_embed)

        user_choice = await self.user_choice(ctx.author)

        if user_choice is None:
            return  # Handle if user doesn't respond in time

        if user_choice.isdigit() and 1 <= int(user_choice) <= len(aspects):
            await ctx.send(f"Updating {aspects[int(user_choice)-1]}...")
        else:
            await ctx.send("Invalid choice. Please enter a number between 1 and {}".format(len(aspects)))




    async def user_choice(self, user):
        try:
            await user.send("What aspect do you want to update?")

            # Wait for the user's reply (timeout in seconds)
            msg = await self.bot.wait_for(
                "message", check=lambda message: message.author == user and isinstance(message.channel, discord.DMChannel), timeout=60
            )

            return msg.content
        except discord.TimeoutError:
            await user.send("You took too long to respond! Please start the profile setup again.")
            return None
        


async def setup(bot):
    await bot.add_cog(Update(bot))
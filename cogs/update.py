import discord
from discord.ext import commands
import logging
from modules.database import Database
from cogs.profile import Profile
class Update(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.logger = logging.getLogger(
            f"discord.cog.{self.__class__.__name__.lower()}"
        )
        self.major_list = self.load_major_list()
        
    def load_major_list(self):
        """
        Loads the list of majors from the majors.txt file.
        """
        try:
            with open("resources/majors.txt", "r") as f:
                major_list = [line.strip() for line in f.readlines()]
                return major_list
        except FileNotFoundError:
            self.logger.error("majors.txt not found")
            return []

    @commands.command(name="update", help="Update your profile with new information.")
    async def update(self, ctx):

        # Create an embed with a welcome message
        updatedUser = self.bot.db.get_data("user", ctx.author.id)
        if(updatedUser == -1 or updatedUser == None or not updatedUser):
            await ctx.send("You do not have a profile yet! Please use the !profile command to create one.")
            return
        
        aspects = ["First Name", "Last Name", "Major", "Graduation Year", "RIN", "RPI Email", "Exit"]
        aspects_embed = discord.Embed(
            title="Update Page",
            description="\n".join([f"{i+1}. {aspect}" for i, aspect in enumerate(aspects)]),
            color=discord.Color.pink(),
        )
        while True:
            await ctx.send(embed=aspects_embed)
            user_choice = await self.user_choice(ctx.author)

            if user_choice is None:
                return  # Handle if user doesn't respond in time

            if user_choice.isdigit() and 1 <= int(user_choice) <= len(aspects):
                new_value = aspects[int(user_choice) - 1]
                aspect = aspects[int(user_choice) - 1]

                if(aspect == "Exit"):
                    await ctx.send("Exiting update page.")
                    break
                if(aspect == "First Name"):
                    await ctx.send("Your previous response was: " + updatedUser.get_value("first_name"))
                    new_value = await self.ask_question(ctx.author, "What is your updated first name? (Example: John)")
                    updatedUser.set_value("first_name", new_value)
                elif(aspect == "Last Name"):
                    await ctx.send("Your previous response was: " + updatedUser.get_value("last_name"))
                    new_value = await self.ask_question(ctx.author, "What is your updated last name? (Example: Smith)")
                    updatedUser.set_value("last_name", new_value)
                elif(aspect == "Major"):
                    await ctx.send("Your previous response was: " + ", ".join(updatedUser.get_value("major")))
                    new_value = await Profile.ask_major(self, ctx.author)
                    updatedUser.set_value("major", new_value)
                elif(aspect == "Graduation Year"):
                    await ctx.send("Your previous response was: " + updatedUser.get_value("graduation_year"))
                    new_value = await Profile.ask_graduation_year(self, ctx.author)
                    updatedUser.set_value("graduation_year", new_value)
                elif(aspect == "RIN"):
                    await ctx.send("Your previous response was: " + updatedUser.get_value("student_id"))
                    new_value = await Profile.ask_rin(self, ctx.author)
                    updatedUser.set_value("student_id", new_value)
                elif(aspect == "RPI Email"):
                    await ctx.send("Your previous response was: " + updatedUser.get_value("school_email"))
                    new_value = await Profile.ask_email(self, ctx.author)
                    updatedUser.set_value("school_email", new_value)

                await ctx.send(f"Your {aspect} has been updated.")

            else:
                await ctx.send("Invalid choice. Please enter a number between 1 and {}".format(len(aspects)))
        await self.show_profile(ctx, updatedUser)
        self.bot.db.update_data(updatedUser)

    async def user_choice(self, user):
        """
        Asks the user to select an aspect of their profile to update.

        :param user: The user to ask.
        :type user: discord.User
        :return: The user's response.
        :rtype: str
        :raises discord.TimeoutError: The user took too long to respond.
        """
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


    async def ask_question(self, user, question):
        """
        Sends a question to the user and waits for a response.
        Returns the user's response or None if they don't respond in time.
        """
        try:
            await user.send(question)

            # Wait for the user's reply (timeout in seconds)
            msg = await self.bot.wait_for(
                "message", check=lambda message: message.author == user and isinstance(message.channel, discord.DMChannel), timeout=60
            )

            await user.send(f"Your response: {msg.content}")

            return msg.content  # Return the response
        except discord.TimeoutError:
            await user.send("You took too long to respond! Please start the profile setup again.")
            return None
        
    async def show_profile(self, ctx, user_profile):
        """
        Sends an embed showing the user's updated profile. 
        """
        embed = discord.Embed(
            title=f"{ctx.author.display_name}'s Updated Profile",
            description="Here is the information you provided:",
            color=discord.Color.purple(),
        )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        embed.add_field(name="First Name", value=user_profile.get_value("first_name"), inline=True)
        embed.add_field(name="Last Name", value=user_profile.get_value("last_name"), inline=True)
        embed.add_field(name="Major", value=", ".join(user_profile.get_value("major")), inline=True)
        embed.add_field(name="Graduation Year", value=user_profile.get_value("graduation_year"), inline=True)
        embed.add_field(name="RPI Email", value=user_profile.get_value("school_email"), inline=True)
        embed.add_field(name="RIN", value=user_profile.get_value("student_id"), inline=True)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Update(bot))
import asyncio
import discord
import string
import logging
from discord.ext import commands
from modules.database import Database
from modules.email import get_verified_email
import subprocess

class Profile(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = logging.getLogger(
            f"discord.cog.{self.__class__.__name__.lower()}"
        )
        self.major_list = self.load_major_list()

    def load_major_list(self):
        try:
            with open("resources/majors.txt", "r") as f:
                return [line.strip() for line in f.readlines()]
        except FileNotFoundError:
            self.logger.error("majors.txt not found")
            return []

    @commands.group(
        name="profile", invoke_without_command=True, help="Profile commands."
    )
    async def profile(self, ctx):
        embed = discord.Embed(
            title="Profile Commands",
            description="Below are the profile commands you can use.\n!profile create - Creates your profile.\n!profile update - Updates your profile.\n!profile show - Shows your profile.",
            color=discord.Color.purple(),
        )
        await ctx.send(embed=embed)

    @profile.command(name="create", help="Creates your profile.")
    async def create(self, ctx):

        # Create an embed with a welcome message
        """
        This command will guide you through creating your profile. It will ask for your first name, last name, major, graduation year, RPI email, and RPI RIN. If you have already created a profile, it will ask you if you want to override it. If you do not want to override, it will allow you to exit the profile creation.
        """
        # Send the welcome message to the user
        dm_embed = discord.Embed(
            title="Welcome to the RPI Discord!",
            description="We're excited to have you here! Before we get started, we need some information from you to create your profile. Please answer the following questions with your information. (If you made any mistakes, you can update it after completing vertification using the !update command.)",
            color=discord.Color.purple(),
        )
        await ctx.author.send(embed=dm_embed)

        user = self.bot.db.get_data("user", ctx.author.id)
        if not user:
            user = self.bot.db.create_data("user", ctx.author.id)
        else:
            await ctx.send(
                "You already have a profile. Are you sure want to override it? If you do not please use the update command.\n Type Y or N"
            )
            msg = await self.bot.wait_for(
                "message",
                check=lambda message: message.author == ctx.author
                and isinstance(message.channel, discord.DMChannel),
            )
            if msg.content.lower() == "y":
                await ctx.send(
                    "Ok. The profile will be overwritten. If you want to update your profile please use the update command."
                )
                user = self.bot.db.create_data("user", ctx.author.id)
            else:
                await ctx.send(
                    "Ok. The profile will not be overwritten. If you want to update your profile please use the update command."
                )
                return

        # Ask for user's first name
        first_name = await self.ask_question(
            ctx.author, "What is your (preferred) first name? (Example: John)"
        )
        if first_name is None:
            return  # Handle if user doesn't respond in time

        # Ask for user's last name
        last_name = await self.ask_question(
            ctx.author,
            'What is your last name? (Please make sure to capitalize appropriately, e.g "Smith")',
        )
        if last_name is None:
            return

        # Ask for user's major
        major = await self.ask_major(ctx.author)
        if major is None:
            return

        # Ask for graduation year
        grad_year = await self.ask_graduation_year(ctx.author)
        if grad_year is None:
            return

        # Ask for user's RPI email
        rpi_email = await self.ask_email(ctx.author)
        if rpi_email is None:
            return

        rpi_rin = await self.ask_rin(ctx.author)
        if rpi_rin is None:
            return

        # Create an embed with the collected profile information
        profile_embed = discord.Embed(
            title=f"{ctx.author.display_name}'s Profile",
            description="Here is the information you provided:",
            color=discord.Color.purple(),
        )

        # Add the profile information to the embed
        profile_embed.set_thumbnail(url=ctx.author.display_avatar.url)
        profile_embed.add_field(name="First Name", value=first_name, inline=True)
        profile_embed.add_field(name="Last Name", value=last_name, inline=True)
        profile_embed.add_field(name="Major", value=", ".join(major), inline=True)
        profile_embed.add_field(name="Graduation Year", value=grad_year, inline=True)
        profile_embed.add_field(name="RPI Email", value=rpi_email, inline=True)
        profile_embed.add_field(name="RPI RIN", value=rpi_rin, inline=True)

        # Save the collected profile information to the database
        user.set_value("first_name", first_name)
        user.set_value("last_name", last_name)
        user.set_value("major", major)
        user.set_value("graduation_year", grad_year)
        user.set_value("school_email", rpi_email)
        user.set_value("student_id", rpi_rin)
        self.bot.db.upsert_data(user)

        # Send the profile back to the user for confirmation
        await ctx.author.send(embed=profile_embed)

    async def ask_question(self, user, question):
        """
        Sends a question to the user and waits for a response.
        Returns the user's response or None if they don't respond in time.
        """
        try:
            await user.send(question)

            # Wait for the user's reply (timeout in seconds)
            msg = await self.bot.wait_for(
                "message",
                check=lambda message: message.author == user
                and isinstance(message.channel, discord.DMChannel),
                timeout=60,
            )

            await user.send(f"Your response: {msg.content}")

            return msg.content  # Return the response
        except discord.TimeoutError:
            await user.send(
                "You took too long to respond! Please start the profile setup again."
            )
            return None

    async def ask_graduation_year(self, user):
        """
        Sends a question to the user regarding the graduation year and waits for a response.
        Checks if the response is a valid year and returns it if it is.
        Return None if the user doesn't respond in time or if the response is not a valid year.
        """
        while True:
            grad_year = await self.ask_question(
                user, "What is your graduation year (YYYY)?"
            )
            if grad_year is None:
                return None

            if grad_year.isdigit() and len(grad_year) == 4:
                return grad_year
            else:
                await user.send(
                    f"{grad_year} is not a valid year. Please enter a valid year (YYYY)."
                )

    async def ask_major(self, user):
        """
        Sends a question to the user regarding the major and waits for a response.
        Checks if the response is a valid major and returns it if it is.
        Return None if the user doesn't respond in time or if the response is not a valid major.
        """
        while True:
            # Create an embed with the list of majors
            major_embed = discord.Embed(
                title="Major List",
                description="Respond with the number(s) that correspond to your current Major.",
            )

            for i, major in enumerate(self.major_list):
                major_embed.description += f"\n{i+1}. {major}"
            await user.send(embed=major_embed)

            # Wait for the user's reply (timeout in seconds)
            msg = await self.bot.wait_for(
                "message",
                check=lambda message: message.author == user
                and isinstance(message.channel, discord.DMChannel),
                timeout=60,
            )

            # Split the message via commas to determine the selected majors
            major_choices = msg.content.split(",")
            major_choices = [choice.strip() for choice in major_choices]

            # Check if the user's reply contains duplicate majors
            if len(major_choices) != len(set(major_choices)):
                await user.send(
                    f"{msg.content} contains duplicate majors. Please enter a valid major."
                )
                continue
            selected_majors = []
            valid = True

            # Check if the user's reply is a valid major
            for choice in major_choices:
                if choice.isdigit() and 0 <= int(choice) - 1 < len(self.major_list):
                    selected_majors.append(self.major_list[int(choice) - 1])
                else:
                    valid = False
                    break

            if valid:
                await user.send(f"Your selected majors: {', '.join(selected_majors)}")
                return selected_majors
            else:
                await user.send(
                    f"{msg.content} is not a valid major. Please enter a valid major."
                )

    async def ask_email(self, user):
        """
        Sends a question to the user regarding the email and waits for a response.
        Checks if the response is a valid email and returns it if it is.
        Return None if the user doesn't respond in time or if the response is not a valid email.
        """
        while True:

            rpi_email = await self.ask_question(
                user,
                "What is your RPI email? Please type out your full email address! (Example: smithj23@rpi.edu)",
            )
            if rpi_email is None:
                self.logger.info("User did not respond in time or did not input an email") 
                return None

            if rpi_email[-8:] == "@rpi.edu":
                self.logger.info("Starting Flask server for OAuth verification...")
                flask_process = subprocess.Popen(
                    ["python", "app.py"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                oauth_url = f"http://localhost:5000/login?state={user.id}"
                await user.send(f"To verify your RPI email, please authenticate here: {oauth_url}")
                # Poll for verification result
                for _ in range(50):  # Wait up to 100 seconds, checking every 2 seconds
                    await asyncio.sleep(2)
                    rpi_email = get_verified_email(user.id)
                    if rpi_email:
                        await user.send(f"Email verified successfully as {rpi_email}.")
                        return rpi_email
                
                await user.send("Email verification timed out. Please try again.")
                return None
            else:
                await user.send(
                    f"{rpi_email} is not a valid email. Please enter a valid email."
                )

    async def ask_rin(self, user):
        """
        Sends a question to the user regarding the RIN and waits for a response.
        Checks if the response is a valid RIN and returns it if it is.
        Return None if the user doesn't respond in time or if the response is not a valid RIN.
        """
        while True:
            rin = await self.ask_question(
                user, "What is your RIN? (Example: 123456789)"
            )
            if rin is None:
                self.logger.info("User did not respond in time or did not input an RIN")
                return None

            if rin.isdigit() and len(rin) == 9:
                return rin
            else:
                await user.send(
                    f"{rin} is not a valid RIN. Please enter a valid RIN. Make sure it has 9 digits."
                )

    @profile.command(name="update", help="Updates your profile.")
    async def update(self, ctx):
        # Create an embed with a welcome message
        """
        Updates your profile by allowing you to modify each individual aspect of your profile.
        """
        updated_user = self.bot.db.get_data("user", ctx.author.id)
        if not updated_user:
            await ctx.send(
                "You do not have a profile yet! Please use the !profile command to create one."
            )
            return

        aspects = [
            "First Name",
            "Last Name",
            "Major",
            "Graduation Year",
            "RIN",
            "RPI Email",
            "Exit",
        ]
        aspects_embed = discord.Embed(
            title="Update Page",
            description="\n".join(
                [f"{i+1}. {aspect}" for i, aspect in enumerate(aspects)]
            ),
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

                if aspect == "Exit":
                    await ctx.send("Exiting update page.")
                    break
                if aspect == "First Name":
                    await ctx.send(
                        "Your previous response was: "
                        + updated_user.get_value("first_name")
                    )
                    new_value = await self.ask_question(
                        ctx.author, "What is your updated first name? (Example: John)"
                    )
                    updated_user.set_value("first_name", new_value)
                elif aspect == "Last Name":
                    await ctx.send(
                        "Your previous response was: "
                        + updated_user.get_value("last_name")
                    )
                    new_value = await self.ask_question(
                        ctx.author, "What is your updated last name? (Example: Smith)"
                    )
                    updated_user.set_value("last_name", new_value)
                elif aspect == "Major":
                    await ctx.send(
                        "Your previous response was: "
                        + ", ".join(updated_user.get_value("major"))
                    )
                    new_value = await Profile.ask_major(self, ctx.author)
                    updated_user.set_value("major", new_value)
                elif aspect == "Graduation Year":
                    await ctx.send(
                        "Your previous response was: "
                        + updated_user.get_value("graduation_year")
                    )
                    new_value = await Profile.ask_graduation_year(self, ctx.author)
                    updated_user.set_value("graduation_year", new_value)
                elif aspect == "RIN":
                    await ctx.send(
                        "Your previous response was: "
                        + updated_user.get_value("student_id")
                    )
                    new_value = await Profile.ask_rin(self, ctx.author)
                    updated_user.set_value("student_id", new_value)
                elif aspect == "RPI Email":
                    await ctx.send(
                        "Your previous response was: "
                        + updated_user.get_value("school_email")
                    )
                    new_value = await Profile.ask_email(self, ctx.author)
                    updated_user.set_value("school_email", new_value)

                await ctx.send(f"Your {aspect} has been updated.")

            else:
                await ctx.send(
                    f"Invalid choice. Please enter a number between 1 and {len(aspects)}"
                )
        await self.show_user_profile(ctx, updated_user)
        self.bot.db.update_data(updated_user)

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
                "message",
                check=lambda message: message.author == user
                and isinstance(message.channel, discord.DMChannel),
                timeout=60,
            )

            return msg.content
        except discord.TimeoutError:
            self.logger.error("You took too long to respond! Please start the profile setup again.")
            await user.send(
                "You took too long to respond! Please start the profile setup again."
            )
            return None

    async def show_user_profile(self, ctx, user_profile):
        """
        Sends an embed showing the user's updated profile.
        """
        embed = discord.Embed(
            title=f"{ctx.author.display_name}'s Updated Profile",
            description="Here is the information you provided:",
            color=discord.Color.purple(),
        )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        embed.add_field(
            name="First Name", value=user_profile.get_value("first_name"), inline=True
        )
        embed.add_field(
            name="Last Name", value=user_profile.get_value("last_name"), inline=True
        )
        embed.add_field(
            name="Major", value=", ".join(user_profile.get_value("major")), inline=True
        )
        embed.add_field(
            name="Graduation Year",
            value=user_profile.get_value("graduation_year"),
            inline=True,
        )
        embed.add_field(
            name="RPI Email", value=user_profile.get_value("school_email"), inline=True
        )
        embed.add_field(
            name="RIN", value=user_profile.get_value("student_id"), inline=True
        )

        await ctx.send(embed=embed)

    @profile.command(name="show", help="Shows your profile.")
    async def show_profile(self, ctx):
        """
        Shows your profile.
        """
        user = self.bot.db.get_data("user", ctx.author.id)
        if user == -1 or not user:
            await ctx.send(
                "You don't have a profile. Please use the !profile command to create one."
            )
            return
        await self.show_user_profile(ctx, user)


async def setup(bot: commands.Bot):
    await bot.add_cog(Profile(bot))

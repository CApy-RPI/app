import discord
import logging
from discord.ext import commands

class Profile(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = logging.getLogger(
            f"discord.cog.{self.__class__.__name__.lower()}"
        )

        self.major_list = [
            "Aeronautical Engineering",
            "Applied Physics",
            "Architecture",
            "Biology",
            "Biomedical Engineering",
            "Business Analytics",
            "Business and Management",
            "Chemical Engineering",
            "Chemistry",
            "Civil Engineering",
            "Cognitive Science",
            "Computer and Systems Engineering",
            "Computer Science",
            "Economics",
            "Electrical Engineering",
            "Environmental Engineering",
            "Environmental Science",
            "Games and Simulation Arts and Sciences",
            "Geology",
            "Industrial and Management Engineering",
            "Information Technology and Web Science",
            "Materials Engineering",
            "Mathematics",
            "Mechanical Engineering",
            "Music",
            "Nuclear Engineering",
            "Philosophy",
            "Physics",
            "Psychology",
            "Science, Technology, and Society",
            "Sustainability Studies",
        ]

    @commands.command(name="profile", help="Shows your profile.")
    async def profile(self, ctx):

        # Create an embed with a welcome message
        dm_embed = discord.Embed(
            title="Welcome to the RPI Discord!",
            description="We're excited to have you here! Before we get started, we need some information from you to create your profile. Please answer the following questions with your information.",
            color=discord.Color.purple(),
        )
        # Send the welcome message to the user
        await ctx.author.send(embed=dm_embed)

        # Ask for user's first name
        first_name = await self.ask_question(ctx.author, "What is your (preferred) first name? (Example: John)")
        if first_name is None:
            return  # Handle if user doesn't respond in time
        
        # Ask for user's last name
        last_name = await self.ask_question(ctx.author, "What is your last name? (Please make sure to capitalize appropriately, e.g \"Smith\")")
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
        profile_embed.add_field(name="Major", value=major, inline=True)
        profile_embed.add_field(name="Graduation Year", value=grad_year, inline=True)
        profile_embed.add_field(name="RPI Email", value=rpi_email, inline=True)
        profile_embed.add_field(name="RPI RIN", value=rpi_rin, inline=True)

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
                    "message", check=lambda message: message.author == user and isinstance(message.channel, discord.DMChannel), timeout=60
                )

                await user.send(f"Your response: {msg.content}")

                return msg.content  # Return the response
            except discord.TimeoutError:
                await user.send("You took too long to respond! Please start the profile setup again.")
                return None
    async def ask_graduation_year(self, user):

        """
        Sends a question to the user regarding the graduation year and waits for a response.
        Checks if the response is a valid year and returns it if it is.
        Return None if the user doesn't respond in time or if the response is not a valid year.
        """
        while(True):
            grad_year = await self.ask_question(user, "What is your graduation year (YYYY)?")
            if grad_year is None:
                return None
            
            if grad_year.isdigit() and len(grad_year) == 4:
                return grad_year
            else:
                await user.send(f"{grad_year} is not a valid year. Please enter a valid year (YYYY).")

    async def ask_major(self, user):
        
        """
        Sends a question to the user regarding the major and waits for a response.
        Checks if the response is a valid major and returns it if it is.
        Return None if the user doesn't respond in time or if the response is not a valid major.
        """
        while(True):
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
                "message", check=lambda message: message.author == user and isinstance(message.channel, discord.DMChannel), timeout=60
            )
            major = int(msg.content)-1
            
            if major is None:
                return None
            
            if 0 <= major < len(self.major_list):
                await user.send(f"Your major: {self.major_list[major]}")
                return self.major_list[major]
            else:
                await user.send(f"{self.major_list[major]} is not a valid major. Please enter a valid major.")

    async def ask_email(self, user):
        """
        Sends a question to the user regarding the email and waits for a response.
        Checks if the response is a valid email and returns it if it is.
        Return None if the user doesn't respond in time or if the response is not a valid email.
        """
        while(True):
            rpi_email = await self.ask_question(user, "What is your RPI email?")
            if rpi_email is None:
                return None

            if rpi_email.count("@") == 1 and rpi_email.count(".") > 0:
                return rpi_email
            else:
                await user.send(f"{rpi_email} is not a valid email. Please enter a valid email.") 

    async def ask_rin(self, user):
        """
        Sends a question to the user regarding the RIN and waits for a response.
        Checks if the response is a valid RIN and returns it if it is.
        Return None if the user doesn't respond in time or if the response is not a valid RIN.
        """
        while(True):
            rin = await self.ask_question(user, "What is your RIN?")
            if rin is None:
                return None
            
            if rin.isdigit() and len(rin) == 9:
                return rin
            else:
                await user.send(f"{rin} is not a valid RIN. Please enter a valid RIN. Make sure it has 9 digits.")
            
async def setup(bot: commands.Bot):
    await bot.add_cog(Profile(bot))

import discord
from discord.ext import commands
from modules.database import Database
from datetime import datetime

# Change this to fetch data from some sort of database


class EventCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    @commands.command(name="events", help="Shows all upcoming events")
    async def events(self, ctx):
        """
        Handles output for !event command
        """

        # All events listed for current guild
        guild_events = self.db.get_data("guild", ctx.guild.id).get_value("events")

        if not guild_events:
            embed = discord.Embed(
                title="No Upcoming Events",
                description="There are no events scheduled at the moment.",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)
            return

        # Create an embed for the events list
        embed = discord.Embed(
            title="Upcoming Events",
            # description="Here are the upcoming events:",
            color=discord.Color.green(),
        )

        for event in guild_events:
            event_details = f"{event['date']} at {event['time']}"
            embed.add_field(name=event["name"], value=event_details, inline=False)

        # Send the embed message
        await ctx.send(embed=embed)

    # Command to add a new event, allowing spaces in the event name
    @commands.command(
        name="add_event",
        help='Add a new event. Usage: !add_event "<name>" <mm-dd-yyyy> <00:00 PM>',
    )
    async def add_event(self, ctx, name: str, date: str, *time):
        """Creates event, adds to guild events list, prints confirmation embed"""
        # Fetch existing guild data or create new if it doesn't exist
        guild_data = self.db.get_data("guild", ctx.guild.id)
        if not guild_data:
            guild_data = self.db.create_data("guild", ctx.guild.id)
            self.db.update_data(guild_data)

        # Add the event to the guild events list
        time_str = " ".join(time)
        new_event = {"name": name, "date": date, "time": time_str}
        guild_data.append_value("events", new_event)

        # Update the database with the new event
        self.db.update_data(guild_data)

        # Create an embed to confirm the event was added
        embed = discord.Embed(
            title="Event Added",
            description=f"Event '{name}' has been added successfully!",
            color=discord.Color.blue(),
        )
        embed.add_field(name="Date", value=date, inline=True)
        embed.add_field(name="Time", value=time_str, inline=True)

        # Send the embed confirmation message and also store it
        msg = await ctx.send(embed=embed)

        # Allow check mark (✅) and X (❌) emojis for users to react with
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")

        # Add the event to the user_events dictionary
        self.attendance[msg.id] = {"yes": set(), "no": set()}


    # Command to clear all events
    @commands.command(name="clear_events", help="Clears all upcoming events")
    async def clear_events(self, ctx):
        user_events.clear()
        embed = discord.Embed(
            title="Events Cleared",
            description="All events have been successfully cleared.",
            color=discord.Color.orange(),
        )
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def reaction_attendance_add(self, reaction, user):
        """Handles reactions to track user sign up"""
        if user.bot: # Ignore the bot reactions
            return
        
        message_id = reaction.message.id

        guild_data = self.db.get_data("guild", reaction.message.guild.id)
        event = next((event for event in guild_data.get_value("events") if event["id"] == message_id), None)  

        if event:
            if str(reaction.emoji) == "✅":
                if user.id not in event["users"]:
                    event["users"].append(user.id)
            elif str(reaction.emoji) == "❌":
                if user.id in event["users"]:
                    event["users"].remove(user.id)

            self.db.update_data(guild_data)           

    @commands.Cog.listener()
    async def reaction_attendance_remove(self, reaction, user):
        """Handles reactions to track user removal"""
        if user.bot: # Ignore the bot reactions
            return
        
        message_id = reaction.message.id
        guild_data = self.db.get_data("guild", reaction.message.guild.id)
        event = next((event for event in guild_data.get_value("events") if event["id"] == message_id), None)

        if event:
            if str(reaction.emoji) == "✅" and user.id in event["users"]:
                event["users"].remove(user.id)

            self.db.update_data(guild_data)


    # MAKE A FUNCTION TO SHOW ADMIN ALL ATTENDEES FOR AN EVENT
    #! RESTRICT REGULAR MEMBERS FROM USING THIS FEATURE
    @commands.command(name="attendance", help="Shows attendance for upcoming events")
    async def all_events_attendance(self, ctx, message_id: int): 
        """"Displays all attendance for a certain events"""
        if message_id not in self.attendance:
            await ctx.send("No attendance found for this event")

    yes_list = "\n".join([user.name for user in self.attendance[message_id]["yes"]])
    no_list = "\n".join([user.name for user in self.attendance[message_id]["no"]])

    embed = discord.Embed(
        title="Attendance",
        description=f"**Yes:**\n{yes_list}\n\n**No:**\n{no_list}",
        color=discord.Color.green()
    )
    embed.add_field(name="Going✅", value=yes_list or "Empty", inline=False)
    embed.add_field(name="Not Going❌", value=no_list or "Empty", inline=False)

    await ctx.send(embed=embed)

    # embed = discord.Embed(
    #     title="Attendance",
    #     description=f"Event ID: {message_id}",
    #     color=discord.Color.blue(),
    # )
    
    #! MAKE A FUNCTION TO SHOW SPECIFIC EVENTS THAT A SINGLE USER IS SIGNED UP TO ATTEND

    @commands.command(name="announce", help="Announces an event in the announcements channel. Usage: !announce <event_id>")
    async def announce(self, ctx, event_id: int):
        """Announces an event in the announcements channel"""
        # Get event data from the database
        guild_data = self.db.get_data("guild", ctx.guild.id)
        event = next((event for event in guild_data.get_value("events") if event["id"] == event_id), None)

        if not event:
            await ctx.send("Event not found")
            return
        
        # Find the Announcements channel
        announcement_channel = discord.utils.get(ctx.guild.text_channels, name="announcements")

        # Create it if it doesn't exist
        if announcement_channel is None:
            announcement_channel = await ctx.guild.create_text_channel("announcements")

        # Create the embed for announcements
        embed = discord.Embed(
            title="Event Announcement",
            description=f"**Event:** {event['name']}\n**Date:** {event['date']}\n**Time:** {event['time']}",
            color=discord.Color.purple(),
        )
        
        # Send announcement to the channel
        await announcement_channel.send(embed=embed)
        await ctx.send(f"Event announced in #{announcement_channel.name}")
        # await ctx.send(f"Announcement sent to {announcement_channel.mention}.")

# Setup function to load the cog
async def setup(bot):
    await bot.add_cog(EventCog(bot))

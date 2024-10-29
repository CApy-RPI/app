import discord
from datetime import datetime, timezone
from discord.ext import commands
from modules.database import Database
from modules.timestamp import now, format_time


class EventCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    @commands.group(name="event", help="Manage events")
    async def event(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(
                "Invalid event command. Use !event [list, add, delete, clear]"
            )

    @event.command(name="list", help="Shows all upcoming events")
    async def list_events(self, ctx):
        """
        Handles output for !event list command
        """
        guild_events = self.db.get_paginated_linked_data(
            "event", self.db.get_data("guild", ctx.guild.id), 1, 10
        )

        if not guild_events:
            await self._send_no_events_embed(ctx)
            return

        embed = self._create_events_embed(guild_events)
        await ctx.send(embed=embed)

    async def send_no_events_embed(self, ctx):
        """
        Sends an embed message when there are no upcoming events.
        """
        embed = discord.Embed(
            title="No Upcoming Events",
            description="There are no events scheduled at the moment.",
            color=discord.Color.red(),
        )
        await ctx.send(embed=embed)

    def create_events_embed(self, guild_events):
        """
        Creates an embed with the list of upcoming events.
        """
        embed = discord.Embed(
            title="Upcoming Events",
            color=discord.Color.green(),
        )

        for event in guild_events:
            event_details = (
                f"{event.get_value('datetime')} \nEvent ID: {event.get_value('id')}"
            )
            embed.add_field(
                name=event.get_value("name"), value=event_details, inline=False
            )

        return embed

    @event.command(name="add", help="Add a new event. Usage: !event add")
    async def add_event(self, ctx):
        """Creates event, adds to guild events list, prints confirmation embed"""

        name = await self.ask_for_event_name(ctx)
        date = await self.ask_for_event_date(ctx)
        time = await self.ask_for_event_time(ctx)
        location = await self.ask_for_event_location(ctx)

        time_str = format_time(f"{date} {time}")

        guild_data = self.db.get_data("guild", ctx.guild.id)
        new_event_id = int(datetime.now(timezone.utc).timestamp() * 1000)
        new_event_data = self.create_event_data(
            new_event_id, name, time_str, location, ctx.guild.id
        )

        self.db.upsert_data(new_event_data)
        guild_data.append_value("event", new_event_id)
        self.db.upsert_data(guild_data)

        embed = self.create_confirmation_embed(name, time_str, location, new_event_id)
        await ctx.send(embed=embed)

    async def ask_for_event_name(self, ctx):
        """Asks for the event name and returns it."""
        await ctx.send("Please enter the event name:")
        name_message = await self.bot.wait_for(
            "message", check=lambda m: m.author == ctx.author
        )
        return name_message.content

    async def ask_for_event_location(self, ctx):
        """Asks for the event location and returns it."""
        await ctx.send("Please enter the event location:")
        location_message = await self.bot.wait_for(
            "message", check=lambda m: m.author == ctx.author
        )
        return location_message.content

    async def ask_for_event_date(self, ctx):
        """Asks for the event date and returns it."""
        await ctx.send("Please enter the event date (MM/DD/YY):")
        date_message = await self.bot.wait_for(
            "message", check=lambda m: m.author == ctx.author
        )
        return date_message.content

    async def ask_for_event_time(self, ctx):
        """Asks for the event time and returns it."""
        await ctx.send("Please enter the event time (HH:MM AM/PM):")
        time_message = await self.bot.wait_for(
            "message", check=lambda m: m.author == ctx.author
        )
        return time_message.content

    def create_event_data(
        self, event_id: int, name: str, time_str: str, location: str, guild_id: int
    ):
        """Creates a new event data object."""
        new_event_data = self.db.create_data("event", event_id)

        # Ensure all values are serializable
        new_event_data.set_value("name", name)  # Should be a string
        new_event_data.set_value("datetime", time_str)  # Ensure this is a string
        new_event_data.set_value("location", location)  # Ensure this is a string
        new_event_data.set_value("guild_id", guild_id)  # Should be an int

        return new_event_data

    def create_confirmation_embed(
        self, name: str, time_str: str, location: str, event_id: int
    ):
        """Creates an embed to confirm the event was added."""
        embed = discord.Embed(
            title="Event Added",
            description=f"Event '{name}' has been added successfully!",
            color=discord.Color.blue(),
        )
        embed.add_field(name="Date/Time", value=time_str, inline=True)
        embed.add_field(name="Location", value=location, inline=True)
        embed.add_field(name="Event ID", value=str(event_id), inline=False)
        return embed

    @event.command(name="delete", help="Deletes a specific event given id. Usage: !event delete [id]")
    async def delete_event(self, ctx, id: int):
        """
        NOT FUNCTIONAL ON self.db.delete()
        Deletes an event given event id
        """
        self.bot.logger.info(
            f"User {ctx.author.name} ({ctx.author.id}) is attempting to delete event with id {id}"
        )
        event_data = self.bot.db.get_data("event", id)

        if event_data:
            self.bot.db.soft_delete("event", id)
            await ctx.send(embed=self.create_event_deletion_embed(id))
            self.bot.logger.warning(f"Event ID {id} deleted successfully.")
        else:
            await ctx.send(
                f"Event with ID '{id}' has already been deleted or does not exist."
            )
            self.bot.logger.warning(f"Attempted to delete nonexistent event ID {id}.")

        #!CHECK THIS

        # # Allow check mark (✅) and X (❌) emojis for users to react with
        # await msg.add_reaction("✅")
        # await msg.add_reaction("❌")

        # # Add the event to the user_events dictionary
        # self.attendance[msg.id] = {"yes": set(), "no": set()}


    def create_event_deletion_embed(self, id: int):
        """Creates an embed to confirm the event was deleted."""
        embed = discord.Embed(
            title="Event Deleted",
            description=f"Event with ID '{id}' has been deleted successfully!",
            color=discord.Color.red(),
        )
        embed.add_field(name="Event ID", value=str(id), inline=False)
        return embed

    def create_clear_events_embed(self):
        """Creates an embed to confirm all events have been cleared."""
        embed = discord.Embed(
            title="Events Cleared",
            description="All events have been successfully cleared.",
            color=discord.Color.orange(),
        )
        return embed

    @event.command(name="clear", help="Clears all upcoming events. Usage: !event clear")
    async def clear_events(self, ctx):
        """
        Deletes all future guild events
        """
        self.bot.logger.info(
            f"User {ctx.author} is clearing all events for guild {ctx.guild.id}."
        )

        # Soft delete all future events associated with this guild
        self.bot.db.bulk_soft_delete_cutoff("event", now())

        # Create an embed to confirm the events have been cleared
        embed = self.create_clear_events_embed()

        # Send the embed confirmation message
        await ctx.send(embed=embed)
        self.bot.logger.info("All events cleared successfully.")





    @commands.Cog.listener()
    async def reaction_attendance_add(self, reaction, user):
        """Handles reactions to track user sign up for an event"""
        if user.bot: # Ignore the bot reactions
            return
        
        message_id = reaction.message.id
        guild_data = self.db.get_data("guild", reaction.message.guild.id)
       
       # search for event by event id
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
        """Handles reactions to track user removal for an event"""
        if user.bot: # Ignore the bot reactions
            return
        
        message_id = reaction.message.id
        guild_data = self.db.get_data("guild", reaction.message.guild.id)

        # search for event by event id
        event = next((event for event in guild_data.get_value("events") if event["id"] == message_id), None)

        if event:
            if str(reaction.emoji) == "✅" and user.id in event["users"]:
                event["users"].remove(user.id)

            self.db.update_data(guild_data)

    #! RESTRICT REGULAR MEMBERS FROM USING THIS FEATURE
    # Shows admin all the users who are registered for a specific event
    @commands.command(name="attendance", help="Shows attendance for a specific event (Admin Only). Usage: !attendance [event id]")
    @commands.has_permissions(administrator=True)
    async def show_event_attendance(self, ctx, message_id: int): 
        """"Displays attendance for a specific event"""
        guild_data = self.db.get_data("guild", ctx.guild.id)
        event = next((event for event in guild_data.get_value("events") if event["id"] == event_id), None)

        if not event or not event.get["user"]:
            await ctx.send("Event not found")
            return

        attendees = [self.bot.get_user(user_id).name for user_id in event["user"]]
        attendee_list = "\n".join(attendees) if attendees else "No attendees yet."

        embed = discord.Embed(
            title="Event Attendance",
            description=f"**Event ID:** {event_id}",
            color=discord.Color.green(),
        )
        embed.add_field(name="Attendees", value=attendee_list, inline=False)

        await ctx.send(embed=embed)
    
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
            description=f"**Event:** {event['name']}\n**Date/Time:** {event['datetime']}\n**Location:** {event['location']}",
            color=discord.Color.purple(),
        )
        
        # Send announcement to the channel
        await announcement_channel.send(embed=embed)
        await ctx.send(f"Event announced in #{announcement_channel.name}")
        # await ctx.send(f"Announcement sent to {announcement_channel.mention}.")

# Setup function to load the cog
async def setup(bot):
    await bot.add_cog(EventCog(bot))

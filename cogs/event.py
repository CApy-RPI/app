import re
import discord
from datetime import datetime, timezone
from discord.ext import commands
from modules.timestamp import now, format_time, get_timezone, localize_datetime
from discord import RawReactionActionEvent

# Configure logging


class Event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.logger.info("Event cog initialized.")
        self.allowed_reactions = ["✅", "❌"]

    @commands.group(name="event", help="Access/Modify Event data.")
    async def event(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="Event Command Help",
                description="Here are the available event commands and their usage:",
                color=discord.Color.blue(),
            )
            embed.add_field(
                name="!event list", value="Shows all upcoming events", inline=False
            )
            embed.add_field(
                name="!event add",
                value="Add a new event. Usage: !event add",
                inline=False,
            )
            embed.add_field(
                name="!event delete",
                value="Delete an existing event. Usage: !event delete [event_id]",
                inline=False,
            )
            embed.add_field(
                name="!event clear",
                value="Clear all events for the guild. Usage: !event clear",
                inline=False,
            )
            await ctx.send(embed=embed)

    @event.command(name="list", help="Shows all upcoming events")
    async def list_events(self, ctx):
        """
        Handles output for !event list command.
        """
        self.bot.logger.info(f"User {ctx.author} requested the list of events.")
        guild_events = self.bot.db.get_paginated_linked_data(
            "event", self.bot.db.get_data("guild", ctx.guild.id), 1, 10
        )
        self.bot.logger.info(f"Retrieved events: {guild_events}")

        # If no events are returned, send an "No events" embed
        if not guild_events:
            await self.send_no_events_embed(ctx)
            return

        # Create and send an embed listing all events
        embed = self.create_events_embed(guild_events)
        await ctx.send(embed=embed)

    async def send_no_events_embed(self, ctx):
        """
        Sends an embed message when there are no upcoming events.
        """
        self.bot.logger.info(f"No upcoming events for guild {ctx.guild.id}.")
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
            event_details = f"{localize_datetime(event.get_value('datetime'), event.get_value('timezone'))} \nEvent ID: {event.get_value('id')}"
            embed.add_field(
                name=event.get_value("name"), value=event_details, inline=False
            )

        self.bot.logger.info(f"Created events embed with {len(guild_events)} events.")
        return embed

    @event.command(name="add", help="Add a new event. Usage: !event add")
    async def add_event(self, ctx):
        """Creates event, adds to guild events list, prints confirmation embed"""
        self.bot.logger.info(f"User {ctx.author} is adding a new event.")

        name = await self.ask_for_event_name(ctx)
        date = await self.ask_for_event_date(ctx)
        time = await self.ask_for_event_time(ctx)
        location = await self.ask_for_event_location(ctx)
        event_timezone = get_timezone(time)

        time_str = format_time(f"{date} {time}")

        guild_data = self.bot.db.get_data("guild", ctx.guild.id)
        new_event_id = int(datetime.now(timezone.utc).timestamp() * 1000)
        new_event_data = self.create_event_data(
            new_event_id, name, time_str, location, event_timezone, ctx.guild.id
        )

        self.bot.db.upsert_data(new_event_data)
        guild_data.append_value("event", new_event_id)
        self.bot.db.upsert_data(guild_data)

        embed = self.create_confirmation_embed(
            name,
            localize_datetime(time_str, new_event_data.get_value("timezone")),
            location,
            new_event_id,
        )
        await ctx.send(embed=embed)
        self.bot.logger.info(f"Event '{name}' added with ID {new_event_id}.")

    async def ask_for_event_name(self, ctx):
        """Asks for the event name and returns it."""
        await ctx.send("Please enter the event name:")
        name_message = await self.bot.wait_for(
            "message", check=lambda m: m.author == ctx.author
        )
        self.bot.logger.info(f"Event name received: {name_message.content}")
        return name_message.content

    async def ask_for_event_date(self, ctx):
        """Asks for the event date in mm/dd/yy format and returns it."""
        date_pattern = re.compile(r"^(0[1-9]|1[0-2])\/(0[1-9]|[12][0-9]|3[01])\/\d{2}$")

        while True:
            await ctx.send(
                "Please enter the event date in mm/dd/yy format (e.g., 12/31/24):"
            )
            date_message = await self.bot.wait_for(
                "message", check=lambda m: m.author == ctx.author
            )
            date_input = date_message.content.strip()

            # Check if the input matches the mm/dd/yy format
            if date_pattern.match(date_input):
                self.bot.logger.info(f"Event date received: {date_input}")
                return date_input
            else:
                await ctx.send(
                    "Invalid date format. Please enter the date in mm/dd/yy format."
                )

    async def ask_for_event_location(self, ctx):
        """Asks for the event location and returns it."""
        await ctx.send("Please enter the event location:")
        location_message = await self.bot.wait_for(
            "message", check=lambda m: m.author == ctx.author
        )
        self.bot.logger.info(f"Event location received: {location_message.content}")
        return location_message.content

    async def ask_for_event_time(self, ctx):
        """Asks for the event time in 'HH:MM AM/PM Timezone' format and returns it."""
        # Regular expression to match "HH:MM AM/PM" with an optional timezone
        time_pattern = re.compile(r"^(0[1-9]|1[0-2]):[0-5][0-9] (AM|PM)( [A-Z]{2,4})?$")

        while True:
            await ctx.send(
                "Please enter the event time in the format 'HH:MM AM/PM Timezone' (e.g., 12:00 PM PDT). Timezone is optional, defaults to EDT."
            )
            time_message = await self.bot.wait_for(
                "message", check=lambda m: m.author == ctx.author
            )
            time_input = time_message.content.strip()

            # Check if the input matches the required time format
            if time_pattern.match(time_input):
                self.bot.logger.info(f"Event time received: {time_input}")
                return time_input
            else:
                await ctx.send("Invalid time format.")

    def create_event_data(
        self,
        event_id: int,
        name: str,
        time_str: str,
        location: str,
        event_timezone: str,
        guild_id: int,
    ):
        """Creates a new event data object."""
        new_event_data = self.bot.db.create_data("event", event_id)

        new_event_data.set_value("name", name)  # Should be a string
        new_event_data.set_value("datetime", time_str)  # string
        new_event_data.set_value("location", location)  # string
        new_event_data.set_value("timezone", event_timezone)  # string
        new_event_data.set_value("guild_id", guild_id)  # int

        self.bot.logger.info(f"Event data created for event ID {event_id}.")
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

    @event.command(
        name="delete",
        help="Deletes a specific event given id. Usage: !event delete [id]",
    )
    async def delete_event(self, ctx, id: int):
        """
        Deletes an event given event id
        """
        self.bot.logger.info(
            f"User {ctx.author} is attempting to delete event ID {id}."
        )
        event_data = self.bot.db.get_data("event", id)

        if event_data:
            self.bot.db.soft_delete("event", id)
            await ctx.send(embed=self.create_event_deletion_embed(id))
            self.bot.logger.info(f"Event ID {id} deleted successfully.")
        else:
            await ctx.send(
                f"Event with ID '{id}' has already been deleted or does not exist."
            )
            self.bot.logger.warning(f"Attempted to delete non-existent event ID {id}.")

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
        self.bot.logger.info(
            f"User {ctx.author} is clearing all events for guild {ctx.guild.id}."
        )

        # Soft delete all future events associated with this guild
        self.bot.db.bulk_soft_delete_cutoff("event", now())
        self.bot.db.bulk_soft_delete_cutoff("event", now())

        # Create an embed to confirm the events have been cleared
        embed = self.create_clear_events_embed()

        # Send the embed confirmation message
        await ctx.send(embed=embed)
        self.bot.logger.info("All events cleared successfully.")

    #! RESTRICT REGULAR MEMBERS FROM USING THIS FEATURE
    # Shows admin all the users who are registered for a specific event
    @commands.command(name="attendance", help="Shows attendance for a specific event (Admin Only). Usage: !attendance [event id]")
    async def show_event_attendance(self, ctx, message_id: int): 
        """"Displays attendance for a specific event"""
        guild_data = self.bot.db.get_data("guild", ctx.guild.id)
        event = next((event for event in guild_data.get_value("event") if event["id"] == event_id), None)

        if not event or not event.get("user"):
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

    @commands.command(name="announce", help="Announces an event in the announcements channel. Usage: !announce [event id]")
    async def announce(self, ctx, event_id: int):
        """
        Announces an event in the announcements channel
        """

        # Get event data from the database
        event = self.bot.db.get_data("event", event_id)

        if not event:
            await ctx.send("ERROR: Event not found.")
            return
        
        # Find the #announcements channel
        announcement_channel = discord.utils.get(ctx.guild.text_channels, name="announcements")

        # Create it if it doesn't exist
        if announcement_channel is None:
            try:
                # Create the #announcements channel with permissions allowing only the bot to send messages
                announcement_channel = await ctx.guild.create_text_channel("announcements")
                await announcement_channel.set_permissions(ctx.guild.default_role, send_messages=False)
                await announcement_channel.set_permissions(ctx.guild.me, send_messages=True)
            except discord.Forbidden:
                await ctx.send("ERROR: I do not have permission to create channels.")
                return
        else:
            # If the channel already exists, ensure permissions are set correctly
            await announcement_channel.set_permissions(ctx.guild.default_role, send_messages=False)
            await announcement_channel.set_permissions(ctx.guild.me, send_messages=True)

        # Create the embed for announcements
        embed = discord.Embed(
            title="Event Announcement",
            description=f"**Event:** {event.get_value('name')}\n**Date/Time:** {event.get_value('datetime')}\n**Location:** {event.get_value('location')}",
            color=discord.Color.purple(),
        )

        try:
            # Send announcement to the channel and add reactions for attendance
            message = await announcement_channel.send(embed=embed)
            await message.add_reaction("✅")  # Add reaction for attendance
            await message.add_reaction("❌")  # Add reaction for decline
            await announcement_channel.send(f"React with ✅ to attend or ❌ to decline")

            # Update event data
            self.bot.db.upsert_data(event) 

            await ctx.send(f"Event announced in #{announcement_channel.name}!")
            
            self.bot.logger.info(f"Event announced successfully in #{announcement_channel.name} with message ID {message.id}. NUM 7")  #! Debug statement 7
        except discord.Forbidden:
            await ctx.send("ERROR: I do not have permission to send messages or add reactions in the announcements channel.") 

    # # Event listener for adding a reaction
    # @commands.Cog.listener()
    # async def on_raw_reaction_add(self, payload):
    #     if payload.emoji.name == "✅":  
    #         print(f"payload_user.id: {payload.user_id}")
    #         user_data = self.bot.db.get_data("user", payload.user_id)  # Assume message_id is used as the event's ID

    #         if not user_data:
    #             self.bot.logger.warning(f"No user associated with user ID {payload.user_id}.")
    #             return

    #         print(f"payload_message.id: {payload.message_id}")
    #         await self.reaction_attendance_add(payload.user_id, payload.message_id)

    # # Event listener for removing a reaction
    # @commands.Cog.listener()
    # async def on_raw_reaction_remove(self, payload):
    #     if payload.emoji.name == "❌":  
    #         user_data = self.bot.db.get_data("user", payload.user_id)

    #     if not user_data:
    #         self.bot.logger.warning(f"No user associated with user ID {payload.user_id}.")
    #         return

    #     await self.reaction_attendance_remove(payload.user_id, payload.message_id)

    # Function to handle adding attendance on reaction
    async def reaction_attendance_add(self, user_id, event_id):
        """Adds user to event attendance list."""
        #! keep track of what the message id's are

        # Pull the user data
        user_data = self.bot.db.get_data("user", user_id)
        print(user_data)

        if not user_data:
            self.bot.logger.warning(f"User ID {user_id} not found.")
            return

        # Update the "event" key in the user's JSON data with the event_id
        user_data.append_value("event", event_id)
        print(2)
        print(user_data)

        # Save the updated data back to the database
        self.bot.db.upsert_data(user_data)
        self.bot.logger.info(f"User {user_id} updated with event {event_id}.")

    # Function to handle removing attendance on reaction
    async def reaction_attendance_remove(self, user_id, event_id):
        """Removes user from event attendance list."""
        user_data = self.bot.db.get_data("user", user_id)
        print(7)
        print(user_data)

        if not user_data:
            self.bot.logger.warning(f"User ID {user_id} not found.")
            return

        print(f"Value to remove: {event_id}")
        user_data.remove_value("event", event_id)

        self.bot.db.upsert_data(user_data)
        self.bot.logger.info(f"User {user_id} updated with event {event_id}.")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        """Handle adding a reaction to limit users to only one option."""
        if payload.emoji.name not in self.allowed_reactions:
            return  # Ignore other reactions

        # Fetch the message and channel to work with reactions
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        print(message)
        
        # Check if user has already reacted with the other emoji
        for reaction in message.reactions:
            if reaction.emoji in self.allowed_reactions and reaction.emoji != payload.emoji.name:
                async for user in reaction.users():
                    if user.id == payload.user_id:
                        # User reacted with the other option, so remove it
                        await reaction.remove(user)

        # Now the user only has one reaction

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: RawReactionActionEvent):
        """Prevent unreacting by re-adding the reaction if the user removes it."""
        if payload.emoji.name not in self.allowed_reactions:
            return  # Ignore other reactions

        # Fetch the channel and message to re-add the reaction
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        user = await self.bot.fetch_user(payload.user_id)
        print(5)
        print(user)

        # Re-add the reaction to simulate a "locked" choice
        await message.add_reaction(payload.emoji.name)

# Setup function to load the cog
async def setup(bot):
    await bot.add_cog(Event(bot))


#! i need to connect the new listener functions to the async def functions now
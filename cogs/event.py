import re
import discord
from datetime import datetime, timezone
from discord.ext import commands
from modules.timestamp import now, format_time, get_timezone, localize_datetime

# Configure logging


class Event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.logger.info("Event cog initialized.")

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

    async def reaction_attendance_remove(self, payload):
        """
        Removes user from event attendance list
        """
        self.bot.logger.info(f"Reaction removed: {payload.user_id}")

        event_id = payload.message_id
        self.bot.logger.info(f"Event ID: {event_id}")

        event_data = self.bot.db.get_data("event", event_id)
        if not event_data:
            return
        event_data.remove_value("attendees", payload.user_id)
        self.bot.db.upsert_data(event_data)

    async def reaction_attendance_add(self, payload):
        """
        Adds user to event attendance list
        """
        self.bot.logger.info(f"Reaction added: {payload.user_id}")
        
        event_id = payload.message_id
        self.bot.logger.info(f"Event ID: {event_id}")

        event_data = self.bot.db.get_data("event", event_id)
        if not event_data:
            return
        event_data.append_unique_value("attendees", payload.user_id)
        self.bot.db.upsert_data(event_data)
       
    # @commands.Cog.listener()
    # async def reaction_attendance_add(self, reaction, user):
    #     """
    #     Handles reactions to track user sign up for an event
    #     """

    #     # Ignore the bot reactions
    #     if user.bot: 
    #         return
        
    #     message_id = reaction.message.id
    #     guild_data = self.bot.db.get_data("guild", reaction.message.guild.id)
       
    #    # search for event by event id
    #     event = next((event for event in guild_data.get_value("event", []) if event["id"] == message_id), None)  

    #     if event:
    #         try:
    #             if str(reaction.emoji) == "✅":
    #                 if user.id not in event["user"]:
    #                     event["user"].append(user.id)
    #             elif str(reaction.emoji) == "❌":
    #                 if user.id in event["user"]:
    #                     event["user"].remove(user.id)
    #         except KeyError as e:
    #             self.bot.logger.error(f"Error: {e} in reaction_attendance_add")
    #             return
    #         except Exception as e:
    #             self.bot.logger.error(f"Error: {e} in reaction_attendance_add")
    #             return

    #         self.bot.db.update_data(guild_data)           

    # @commands.Cog.listener()
    # async def reaction_attendance_remove(self, reaction, user):
    #     """Handles reactions to track user removal for an event"""
    #     if user.bot: # Ignore the bot reactions
    #         return
        
    #     message_id = reaction.message.id
    #     guild_data = self.bot.db.get_data("guild", reaction.message.guild.id)

    #     # search for event by event id
    #     event = next((event for event in guild_data.get_value("event") if event["id"] == message_id), None)

    #     if event:
    #         if str(reaction.emoji) == "✅" and user.id in event["user"]:
    #             event["user"].remove(user.id)

    #         self.bot.db.update_data(guild_data)

# Setup function to load the cog
async def setup(bot):
    await bot.add_cog(Event(bot))

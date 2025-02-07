import re
import discord
from datetime import datetime, timezone
from discord.ext import commands
from modules.timestamp import now, format_time, get_timezone, localize_datetime


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.logger.info("Event cog initialized.")

    @commands.group(name="events", help="Access/Modify Event data.")
    async def events(self, ctx):
        """
        Lists all guild events
        """

        if ctx.invoked_subcommand is None:
            self.bot.logger.info(f"User {ctx.author} requested the list of events.")
            guild_events = self.bot.db.get_paginated_linked_data(
                "event", self.bot.db.get_data("guild", ctx.guild.id), 1, 10
            )

            if not guild_events:
                self.bot.logger.info(f"No events found for guild {ctx.guild.id}.")
                await self.send_no_events_embed(ctx)
                return

            self.bot.logger.info(
                f"Found {len(guild_events)} events for guild {ctx.guild.id}."
            )
            embed = self.create_events_embed(guild_events)
            await ctx.send(embed=embed)

    @events.command(name="myevents", help="Get events you are registered for.")
    async def my_events(self, ctx):
        """Handles output for the command to get events the user is registered for."""
        self.bot.logger.info(f"User {ctx.author.id} requested their registered events.")

        user_events = self.bot.db.get_paginated_linked_data(
            "event", self.bot.db.get_data("user", ctx.author.id), 1, 10
        )

        if not user_events:
            await self.send_no_events_embed(ctx)
            self.bot.logger.info(f"User {ctx.author.id} has no registered events.")
            return

        await ctx.author.send(embed=self.create_events_embed(user_events))
        self.bot.logger.info(f"Sent registered events to user {ctx.author.id}.")

    @events.command(
        name="show",
        help="Show details of a specific event. Usage: !event show [event_id]",
    )
    async def show_event(self, ctx, event_id: int):
        """Displays the details of a specific event by its ID."""
        self.bot.logger.info(
            f"User {ctx.author} requested details for event ID: {event_id}."
        )

        event_data = self.bot.db.get_data("event", event_id)

        if not event_data:
            await ctx.send(f"No event found with ID: {event_id}.")
            return

        embed = self.create_event_embed(
            name=event_data.get_value("name"),
            event_description=event_data.get_value("description"),
            time_str=event_data.get_value("datetime"),
            location=event_data.get_value("location"),
            event_id=event_data.get_value("id"),
        )
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

    @events.command(name="add", help="Add a new event. Usage: !event add")
    async def add_event(self, ctx):
        """Creates event, adds to guild events list, prints confirmation embed"""
        self.bot.logger.info(f"User {ctx.author} is adding a new event.")

        name = await self.ask_for_event_name(ctx)
        event_description = await self.ask_for_event_description(ctx)
        date = await self.ask_for_event_date(ctx)
        time = await self.ask_for_event_time(ctx)
        location = await self.ask_for_event_location(ctx)
        event_timezone = get_timezone(time)

        time_str = format_time(f"{date} {time}")

        guild_data = self.bot.db.get_data("guild", ctx.guild.id)
        new_event_id = int(datetime.now(timezone.utc).timestamp() * 1000)
        new_event_data = self.create_event_data(
            new_event_id,
            name,
            event_description,
            time_str,
            location,
            event_timezone,
            ctx.guild.id,
        )

        self.bot.db.upsert_data(new_event_data)
        guild_data.append_value("event", new_event_id)
        self.bot.db.upsert_data(guild_data)

        embed = self.create_confirmation_embed(
            name,
            event_description,
            localize_datetime(time_str, new_event_data.get_value("timezone")),
            location,
            new_event_id,
        )
        await ctx.send(embed=embed)
        self.bot.logger.info(f"Event '{name}' added with ID {new_event_id}.")

    def create_confirmation_embed(
        self, name, event_description, datetime_str, location, event_id
    ):
        """Creates a confirmation embed for the added event."""
        embed = self.create_event_embed(
            name, event_description, datetime_str, location, event_id
        )
        embed.title = "Event Added Successfully!"
        embed.description = f"The event '{name}' has been added to the calendar."
        return embed

    async def ask_for_event_name(self, ctx):
        """Asks for the event name and returns it."""
        await ctx.send("Please enter the event name:")
        name_message = await self.bot.wait_for(
            "message", check=lambda m: m.author == ctx.author
        )
        self.bot.logger.info(f"Event name received: {name_message.content}")
        return name_message.content

    async def ask_for_event_description(self, ctx):
        """Asks for the event description and returns it."""
        await ctx.send("Please enter the event description:")
        description_message = await self.bot.wait_for(
            "message", check=lambda m: m.author == ctx.author
        )
        self.bot.logger.info(
            f"Event description received: {description_message.content}"
        )
        return description_message.content

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
        description: str,
        time_str: str,
        location: str,
        event_timezone: str,
        guild_id: int,
    ):
        """Creates a new event data object."""
        new_event_data = self.bot.db.create_data("event", event_id)

        new_event_data.set_value("name", name)  # Should be a string
        new_event_data.set_value("description", description)
        new_event_data.set_value("datetime", time_str)  # string
        new_event_data.set_value("location", location)  # string
        new_event_data.set_value("timezone", event_timezone)  # string
        new_event_data.set_value("guild_id", guild_id)  # int

        self.bot.logger.info(f"Event data created for event ID {event_id}.")
        return new_event_data

    def create_event_embed(
        self,
        name: str,
        event_description: str,
        time_str: str,
        location: str,
        event_id: int,
    ):
        """Creates an embed to confirm the event was added."""
        embed = discord.Embed(
            title=name,
            description=event_description,
            color=discord.Color.blue(),
        )
        embed.add_field(name="Date/Time", value=time_str, inline=True)
        embed.add_field(name="Location", value=location, inline=True)
        embed.add_field(name="Event ID", value=str(event_id), inline=False)
        return embed

    @events.command(
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

    @events.command(
        name="clear", help="Clears all upcoming events. Usage: !event clear"
    )
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


# Setup function to load the cog
async def setup(bot):
    await bot.add_cog(Events(bot))

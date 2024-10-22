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

    @event.command(name="delete", help="Deletes a specific event given id")
    async def delete_event(self, ctx, id: int):
        """
        NOT FUNCTIONAL ON self.db.delete()
        Deletes an event given event id
        """

        # Remove specified event from event table in db
        self.db.soft_delete("event", id)  # does not work

        # Create an embed to confirm the event was deleted
        embed = self.create_event_deletion_embed(id)

        # Send the embed confirmation message
        await ctx.send(embed=embed)

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

    @event.command(name="clear", help="Clears all upcoming events")
    async def clear_events(self, ctx):
        """
        NOT FUNCTIONAL WAITING ON self.db.delete()
        Deletes all future guild events
        """

        # Soft delete all future events associated with this guild
        self.db.bulk_soft_delete_after_time("event", now())

        # Create an embed to confirm the events have been cleared
        embed = self.create_clear_events_embed()

        # Send the embed confirmation message
        await ctx.send(embed=embed)


# Setup function to load the cog
async def setup(bot):
    await bot.add_cog(EventCog(bot))

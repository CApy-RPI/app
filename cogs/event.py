import discord
from datetime import datetime, timezone
from discord.ext import commands
from modules.database import Database, now, format_time, format_time_extended


class EventCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    @commands.command(name="events", help="Shows all upcoming events")
    async def events(self, ctx):
        """
        Handles output for !events command
        """
        # All events listed for current guild
        guild_events = self.db.get_paginated_linked_data(
            "event", self.db.get_data("guild", ctx.guild.id), 1, 10
        )

        # If guild has no upcoming events
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
            event_details = f"{event.get_value("datetime")} \nEvent ID: {event.get_value("id")}"
        embed.add_field(name=event.get_value("name"), value = event_details, inline=False)

        # Send the embed message
        await ctx.send(embed=embed)

    # Command to add a new event, allowing spaces in the event name
    @commands.command(
        name="add_event",
        help='Add a new event. Usage: !add_event "<name>" <mm-dd-yyyy> <00:00 PM>',
    )
    async def add_event(self, ctx, name: str, date: str, *time):
        """Creates event, adds to guild events list, prints confirmation embed"""

        guild_data = self.db.get_data("guild", ctx.guild.id)

        # Generate a unique integer ID for the new event using UTC timestamp
        time_str = format_time(date, time)
        new_event_id = int(datetime.now(timezone.utc).timestamp() * 1000)
        new_event_data = self.db.create_data("event", new_event_id)
        new_event_data.set_value("name", name)
        new_event_data.set_value("datetime", time_str)
        new_event_data.set_value("guild_id", ctx.guild.id)

        # Update event table with new event
        self.db.upsert_data(new_event_data)

        # Add the new event ID to the guild's events list
        guild_data.append_value("event", new_event_id)

        # Update the guild table with the new event
        self.db.upsert_data(guild_data)

        # Create an embed to confirm the event was added
        embed = discord.Embed(
            title="Event Added",
            description=f"Event '{name}' has been added successfully!",
            color=discord.Color.blue(),
        )
        embed.add_field(name="Date/Time", value=time_str, inline=True)
        embed.add_field(name="Event ID", value=str(new_event_id), inline=False)

        # Send the embed confirmation message
        await ctx.send(embed=embed)

    # Command to clear all events

    @commands.command(name="delete_event", help="deleted a specific event given id")
    async def delete_event(self, ctx, id: int):
        """
        NOT FUNCTIONAL ON self.db.delete()
        Deletes an event given event id
        """

        # Remove specified event from event table in db
        self.db.soft_delete("event", id)

        # Get current guild data
        current_data = self.db.get_data("guild", ctx.guild.id)

        # Get the current events list from the guild data
        current_events = current_data.get_value("events")

        # Remove the event with the provided id from the list
        current_events = [event for event in current_events if event != id]

        # Update the guild data with the new events list
        current_data.set_value("events", current_events)

        # Update the database with the modified guild data
        self.db.upsert_data(current_data)

        self.logger.info(f"Deleted event {id} for guild {ctx.guild.id}")

        # Create an embed to confirm the event was deleted
        embed = discord.Embed(
            title="Event Deleted",
            description=f"Event with ID {id} has been successfully deleted.",
            color=discord.Color.red(),
        )

        # Send the embed confirmation message
        await ctx.send(embed=embed)

    @commands.command(name="clear_events", help="Clears all upcoming events")
    async def clear_events(self, ctx):
        """
        NOT FUNCTIONAL WAITING ON self.db.delete()
        Deletes all future guild events
        """

        # Soft delete all future events associated with this guild
        self.db.soft_delete_date_cutoff("event", now())

        self.logger.info(f"Cleared all future events for guild {ctx.guild.id}")

        embed = discord.Embed(
            title="Events Cleared",
            description="All events have been successfully cleared.",
            color=discord.Color.orange(),
        )
        await ctx.send(embed=embed)


# Setup function to load the cog
async def setup(bot):
    await bot.add_cog(EventCog(bot))

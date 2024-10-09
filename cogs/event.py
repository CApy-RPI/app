import discord
from datetime import datetime, timezone
from discord.ext import commands
from modules.database import Database


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
            event_data = self.db.get_data("event", event)
            event_details = f"{event_data.get_value("date")} at {event_data.get_value("time")}"
            embed.add_field(name = event_data.get_value("name"), value = event_details, inline=False)

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
        new_event_id = int(datetime.now(timezone.utc).timestamp() * 1000)
        time_str = " ".join(time)
        new_event_data = self.db.create_data("event", new_event_id)
        new_event_data.set_value("name", name)
        new_event_data.set_value("date", date)
        new_event_data.set_value("id", new_event_id)
        new_event_data.set_value("time", time_str)
        new_event_data.set_value("guild_id", ctx.guild.id)
        self.db.update_data(new_event_data)

        # Add the new event ID to the guild's events list
        guild_data.append_value("events", new_event_id)

        # Update the guild table with the new event
        self.db.update_data(guild_data)

        # Create an embed to confirm the event was added
        embed = discord.Embed(
            title="Event Added",
            description=f"Event '{name}' has been added successfully!",
            color=discord.Color.blue(),
        )
        embed.add_field(name="Date", value=date, inline=True)
        embed.add_field(name="Time", value=time_str, inline=True)
        embed.add_field(name="Event ID", value=str(new_event_id), inline=False)

        # Send the embed confirmation message
        await ctx.send(embed=embed)

    # Command to clear all events
    @commands.command(name="clear_events", help="Clears all upcoming events")
    async def clear_events(self, ctx):
        """implementation in progress !!!"""
        user_events.clear()
        embed = discord.Embed(
            title="Events Cleared",
            description="All events have been successfully cleared.",
            color=discord.Color.orange(),
        )
        await ctx.send(embed=embed)


# Setup function to load the cog
async def setup(bot):
    await bot.add_cog(EventCog(bot))

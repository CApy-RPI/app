import discord
from discord.ext import commands

# Change this to fetch data from some sort of database
user_events = [ ]


class EventCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Command to show all upcoming events
    @commands.command(name="events", help="Shows all upcoming events")
    async def events(self, ctx):
        if not user_events:
            embed = discord.Embed(
                title="No Upcoming Events",
                description="There are no events scheduled at the moment.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Create an embed for the events list
        embed = discord.Embed(
            title="Upcoming Events",
            # description="Here are the upcoming events:",
            color=discord.Color.green()
        )

        for event in user_events:
            event_details = f"{event['date']} at {event['time']}"
            embed.add_field(name=event['name'], value=event_details, inline=False)

        # Send the embed message
        await ctx.send(embed=embed)

    # Command to add a new event, allowing spaces in the event name
    @commands.command(name="add_event", help='Add a new event. Usage: !add_event "<name>" <mm-dd-yyyy> <00:00 PM>')
    async def add_event(self, ctx, name: str, date: str, *time):
        # Add the event to the user_events list
        time_str = ' '.join(time)
        new_event = {
            "name": name,
            "date": date,
            "time": time_str
        }
        user_events.append(new_event)

        # Create an embed to confirm the event was added
        embed = discord.Embed(
            title="Event Added",
            description=f"Event '{name}' has been added successfully!",
            color=discord.Color.blue()
        )
        embed.add_field(name="Date", value=date, inline=True)
        embed.add_field(name="Time", value=time, inline=True)

        # Send the embed confirmation message
        await ctx.send(embed=embed)

    # Command to clear all events
    @commands.command(name="clear_events", help="Clears all upcoming events")
    async def clear_events(self, ctx):
        user_events.clear()
        embed = discord.Embed(
            title="Events Cleared",
            description="All events have been successfully cleared.",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)

# Setup function to load the cog
async def setup(bot):
    await bot.add_cog(EventCog(bot))
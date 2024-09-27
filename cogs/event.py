import discord
from discord.ext import commands

# Change this to fetch data from some sort of database
test_events = [
    {"name": "event1", "date": "2024-10-01", "time": "10:00 AM"},
    {"name": "event2", "date": "2024-10-15", "time": "3:00 PM"},
    {"name": "event3", "date": "2024-10-20", "time": "8:00 PM"},
]


class EventCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="events")
    async def events(self, ctx):
        if not test_events:
            await ctx.send("No upcoming events found.")
            return

        # Format the events as a message
        events_list = "\n".join([f"{event['name']} - {event['date']} at {event['time']}" for event in test_events])
        message = f"**Upcoming Events:**\n{events_list}"

        # Send the message to the Discord channel
        await ctx.send(message)


# Setup function to load the cog
async def setup(bot):
    await bot.add_cog(EventCog(bot))
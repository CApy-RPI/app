import os
import discord
import logging
from discord.ext import commands
from dotenv import load_dotenv
from modules.database import Database
from modules.email_auth import create_app
import threading

# Create the bot class, inheriting from commands.AutoShardedBot
class Bot(commands.AutoShardedBot):
    async def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger("discord.main")
        self.logger.setLevel(logging.INFO)
        self.email = Email()
        self.db = await Database()

    # Event that runs when the bot joins a new server
    async def on_guild_join(self, guild: discord.Guild):
        # If already in guild, do nothing
        if self.db.get_data("guild", guild.id):
            self.logger.info(
                f"Joined Guild: {guild.name} (ID: {guild.id}) already exists in database"
            )
            return

        # Else, add guild to data base
        new_guild_data = self.db.create_data("guild", guild.id)
        self.db.upsert_data(new_guild_data)
        self.logger.info(
            f"Inserted New Guild: {guild.name} (ID: {guild.id}) into database"
        )

    # Event that runs when a member joins a guild
    async def on_member_join(self, member: discord.Member):
        # get current guild data
        guild_data = self.db.get_data("guild", member.guild.id)

        # if guild does not exist, create it
        if not guild_data:
            self.logger.warn(
                f"Guild {member.guild.name} does not exist in database for user {member.id} on join"
            )
            guild_data = self.db.create_data("guild", member.guild.id)

        # add member id to server users list
        guild_data.append_value("users", member.id)
        self.db.upsert_data(guild_data)
        self.logger.info(
            f"User {member.id} joined guild {member.guild.name} (ID: {member.guild.id})"
        )

    async def setup_hook(self):
        # Import all cogs from the 'cogs/' directory
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                try:
                    await self.load_extension(f"cogs.{filename[:-3]}")
                    self.logger.info(f"Loaded {filename}")
                except Exception as e:
                    self.logger.error(f"Failed to load {filename}: {e}")
            else:
                self.logger.warning(f"Skipping {filename}: Not a Python file")

    async def on_ready(self):
        # Notify when the bot is ready and print shard info
        self.logger.info(f"Logged in as {self.user.name} - {self.user.id}")
        self.logger.info(f"Connected to {len(self.guilds)} guilds across {self.shard_count} shards.")

    async def on_message(self, message):
        if self.allowed_channel_id is None:
            await self.process_commands(message)
        elif message.channel.id == self.allowed_channel_id:
            await self.process_commands(message)

    async def on_command(self, ctx):
        self.logger.info(f"Command executed: {ctx.command} by {ctx.author}")

    async def on_command_error(self, ctx, error):
        self.logger.error(f"{ctx.command}: {error}")
        await ctx.send(error)
    


def run_flask():
    app = create_app()
    app.run(port=5000)
def main():
    load_dotenv()
    bot = Bot(command_prefix="!", intents=discord.Intents.all())

    """
    DEVS: If testing bot in certain channel to avoid conflicts with other bot instances set CHANNEL_LOCK = "True" in .env
    otherwise can remove CHANNEL_LCOK or set CHANNEL_LOCK = "False"
    """
    # Set the allowed channel ID and channel lock from environment
    allowed_channel_id = os.getenv("ALLOWED_CHANNEL_ID")
    channel_lock_str = os.getenv("CHANNEL_LOCK") or "False"
    channel_lock = channel_lock_str == "TRUE"
    if allowed_channel_id and channel_lock:
        bot.allowed_channel_id = int(allowed_channel_id)
    else:
        bot.allowed_channel_id = None

    bot.run(os.getenv("DEV_BOT_TOKEN"), reconnect=True)


if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    main()

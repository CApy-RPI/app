import os
import discord
import logging
from discord.ext import commands
from dotenv import load_dotenv
from modules.email import Email
from modules.database import create_user, create_guild, get_user, get_guild


# Create the bot class, inheriting from commands.AutoShardedBot
class Bot(commands.AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger("discord.main")
        self.logger.setLevel(logging.INFO)
        self.email = Email()

    # Event that runs when the bot joins a new server
    async def on_guild_join(self, guild: discord.Guild):
        """Called when the bot joins a new guild (server)."""
        self.guild_manager.add_guild(guild.id, guild.name)
        self.logger.info(f"Added new guild: {guild.name}")

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
        self.logger.info(
            f"Connected to {len(self.guilds)} guilds across {self.shard_count} shards."
        )

    async def on_message(self, message):
        await self.process_commands(message)

    async def on_command(self, ctx):
        self.logger.info(f"Command executed: {ctx.command} by {ctx.author}")

    async def on_command_error(self, ctx, error):
        self.logger.error(f"{ctx.command}: {error}")
        await ctx.send(error)


def main():
    load_dotenv()
    bot = Bot(command_prefix="!", intents=discord.Intents.all())
    bot.run(os.getenv("DEV_BOT_TOKEN"), reconnect=True)


if __name__ == "__main__":
    main()

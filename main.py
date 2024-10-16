import discord
from discord.ext import commands
import os
import logging
import asyncio


# Create the bot class, inheriting from commands.AutoShardedBot
class Bot(commands.AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger("discord.main")
        self.logger.setLevel(logging.INFO)

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
    bot = Bot(command_prefix="!", intents=discord.Intents.all())

    with open(".creds.txt", "r") as file:
        token = file.read().strip()

    bot.run(token, reconnect=True)


if __name__ == "__main__":
    main()

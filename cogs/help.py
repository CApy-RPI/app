#cogs/help.py - displays all available commands
#             - displays help for a specific command

import discord
from discord.ext import commands


class HelpCommand(commands.MinimalHelpCommand):
    def __init__(self):
        super().__init__()

    async def send_bot_help(self, mapping):
        """Handles the default help command output."""
        ctx = self.context
        bot = ctx.bot
        embed = discord.Embed(
            title="Help", description="Available commands", color=discord.Color.blue()
        )

        for cog, commands in mapping.items():
            command_list = [command.name for command in commands if not command.hidden]
            if command_list:
                cog_name = cog.qualified_name if cog else "No Category"
                embed.add_field(
                    name=cog_name, value=", ".join(command_list), inline=False
                )

        await ctx.send(embed=embed)

    async def send_cog_help(self, cog):
        """Handles help for a specific cog."""
        embed = discord.Embed(
            title=f"{cog.qualified_name} Commands", color=discord.Color.blue()
        )
        for command in cog.get_commands():
            if not command.hidden:
                embed.add_field(
                    name=command.name,
                    value=command.help or "No description",
                    inline=False,
                )

        await self.context.send(embed=embed)

    async def send_command_help(self, command):
        """Handles help for a specific command."""
        embed = discord.Embed(
            title=command.name,
            description=command.help or "No description",
            color=discord.Color.blue(),
        )
        await self.context.send(embed=embed)


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.help_command = HelpCommand()  # Set the custom help command
        self.bot.help_command.cog = self  # Set the help command's cog to be this cog

    def cog_unload(self):
        self.bot.help_command = (
            commands.DefaultHelpCommand()
        )  # Reset the help command when the cog is unloaded


async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))

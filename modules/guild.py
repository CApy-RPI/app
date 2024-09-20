# models/Guild.py - data for specific guild

class Guild:
    def __init__(self, guild_id: int, guild_name: str):
        """Initialize a new Guild with default settings."""
        self.guild_id = guild_id
        self.guild_name = guild_name
        self.settings = {
            'prefix': '!',                 # Default command prefix
            'welcome_message': 'Welcome!', # Default welcome message
            'moderation_enabled': False    # Moderation setting
        }

    def __str__(self):
        """String representation of the Guild object."""
        return f"Guild({self.guild_id}, {self.guild_name}, {self.settings})"


class GuildManager:
    def __init__(self):
        """Initialize the GuildManager to hold multiple guilds."""
        self.guilds = {} # will be stored in db

    def add_guild(self, guild_id: int, guild_name: str):
        """Add a new Guild instance when the bot joins a new guild."""
        if guild_id not in self.guilds:
            guild = Guild(guild_id, guild_name)
            self.guilds[guild_id] = guild
            print(f"Added new guild: {guild_name}")
        else:
            print(f"Guild {guild_name} already exists.")

    def get_guild(self, guild_id: int):
        """Retrieve a Guild object for the specified guild ID."""
        return self.guilds.get(guild_id, None)

    def __str__(self):
        """String representation of all guilds and their settings."""
        return str([str(guild) for guild in self.guilds.values()])

import discord

from src.data import colors, settings


class CommandHandler:
    """ Command handler superclass, each specific command handler should extend this class """

    def __init__(self, bot, command, aliases, description, usage, example):
        """
        Initialize a command handler (should be overridden by each command)

        Args:
            bot (BotClient): bot interface
            command (str): command string
            aliases (List[str]): list of aliases
            description (str): short command description
            usage (str): command usage template
            example (str): command usage demonstration
        """
        self.bot = bot
        self.command = command
        self.aliases = aliases

        self.description = description
        self.usage = usage
        self.example = example

    async def on_command(self, author, command, args, message, channel, guild):
        """
        Executes the command, should be overridden in the subclass

        Args:
            author (discord.Member): command sender
            command (str): command string
            args (List[str]): list of command arguments
            message (discord.Message): Discord message object
            channel (discord.TextChannel): text channel that the message is sent in
            guild (discord.Guild): guild that the message is sent in

        Returns:
            bool: whether the command is successful
        """
        return False

    def get_help_embedded(self):
        """
        Generates an embedded help message for this command

        Returns:
            discord.Embed: embedded message
        """
        embedded = discord.Embed(
            title=f"Help for command \"{self.command}\"",
            description=f"{self.description}",
            color=colors.COLOR_HELP
        )

        if self.aliases:
            embedded.add_field(name="**Aliases:**", value=f"> {settings.SEP.join(self.aliases)}", inline=False)
        usage = self.usage if self.usage else f"{settings.BOT_PREFIX}{self.command}"
        embedded.add_field(name="**Usage:**", value=f"> {usage}", inline=False)
        example = self.example if self.example else f"{settings.BOT_PREFIX}{self.command}"
        embedded.add_field(name="**Example:**", value=f"> {example}", inline=False)

        return embedded

    def __str__(self):
        return f"Command handler for \"{self.command}\""

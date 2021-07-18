# Built-in imports
from threading import Thread
import time

# Project imports
from src.data import settings, emojis
import src.utils.log_util as log

# External imports
import discord


# Base client class
class BotClient(discord.Client):
    """ Custom Discord client """

    def __init__(self, **options):
        log.info("Initializing bot...")
        super().__init__(**options)

        # Command handlers
        self.command_handlers = []
        # Intent handlers { intent => handler }
        self.intent_handlers = {}
        # Dynamically-registered reaction handlers
        self.reaction_handlers = []
        # Chat handler
        self.chat_handler = None
        self.chat_enabled = False

        log.info("Initialization complete!")

    #########################
    # DISCORD EVENT METHODS #
    #########################

    async def on_ready(self):
        """ Called when the Discord bot is online, sets bot status """
        log.info(f"Bot is online! Hello (happy) world from {self.user}!")
        await self.change_presence(activity=discord.Activity(name="with One", type=1))

    async def on_message(self, message):
        """
        Main method for handling messages and commands

        Args:
            message (discord.Message): incoming message (tracks all messages sent to channels)
        """
        channel = message.channel
        author = message.author
        # Ignore messages sent by bots
        if author.bot:
            return
        # Check if server or channel is whitelisted or DMs
        if channel.id not in settings.ENABLED_CHANNELS and message.guild.id not in settings.ENABLED_SERVERS and not isinstance(channel, discord.DMChannel):
            return
        # Prefix test
        if len(message.content) <= len(settings.BOT_PREFIX) or not message.content.startswith(settings.BOT_PREFIX):
            # Test if chat is enabled
            if self.chat_enabled:
                # Handle NLP
                await self.chat_handler.on_message(author, message, channel, message.guild)
                log.info(f"Chat message \"{message.content}\" received from {author.display_name}#{author.discriminator}!")
            return

        # Parse data
        info = message.content[len(settings.BOT_PREFIX):].split()
        command = info[0]
        args = info[1:]

        # Log
        log.info(f"Command \"{message.content}\" received from {author.display_name}#{author.discriminator}!")

        # Find command handler in registered handlers
        handler = None
        for loop in self.command_handlers:
            if command == loop.command or command in loop.aliases:
                handler = loop
                break

        # Not found -- unknown command
        if handler is None:
            await self.react_unknown(message)
            return

        # Found -- fire handler
        await handler.on_command(message.author, command, args, message, channel, message.guild)

    async def on_reaction_add(self, reaction, user):
        """
        Main method for handling reactions

        Args:
            reaction (discord.Reaction): reaction used
            user (discord.Member): author of this reaction
        """
        # TODO: double check reaction module, feels like i'm missing something?

        # If self react or self didn't react, ignore
        if user == self.user or not reaction.me:
            return
        # Ignore invalid reaction emotes
        if type(reaction.emoji) == discord.PartialEmoji:
            return

        message = reaction.message
        emoji = reaction.emoji  # any of {Emoji, str}

        # Find reaction handler in registered handlers
        for a in range(len(self.reaction_handlers) - 1, 0 - 1, -1):
            handler = self.reaction_handlers[a]

            # Check if the reaction has expired
            if time.time() > handler.expire_time:
                # Fire on_timeout
                await handler.on_timeout()
                del self.reaction_handlers[a]
                continue

            # Match message and reaction(s)
            if message != handler.message or emoji not in handler.emojis:
                continue

            # Correct handler, fire on_react
            await handler.on_react(user, emoji)
            del self.reaction_handlers[a]

            # Log
            log.info(f"Reaction \"{emoji}\" added by {user.display_name}#{user.discriminator} on \"{message.content}\"!")

            # We're done here, return out of this method
            return

    ####################
    # LOGISTIC METHODS #
    ####################

    def register_command_handler(self, handler):
        """
        Register a command handler to the bot, only need to do this once

        Args:
            handler (CommandHandler): command handler
        """
        self.command_handlers.append(handler)

    def register_intent_handler(self, intent, handler):
        """
        Register an intent handler to the bot, only need to do this once

        Args:
            intent (str): intent string (identifier, not description)
            handler (IntentHandler): intent handler
        """
        self.intent_handlers[intent] = handler

    def register_reaction_handler(self, handler):
        """
        Register a dynamic reaction handler to the bot, do this every time when listening to bot reactions

        Args:
            handler (ReactionHandler): reaction handler
        """
        self.reaction_handlers.append(handler)

    def register_chat_handler(self, handler):
        """
        Register a chat handler handler to the bot, there should be only one handler

        Args:
            handler (ChatHandler): reaction handler
        """
        self.chat_handler = handler

    ##########################
    # EXPRESS ACTION METHODS #
    ##########################

    @staticmethod
    async def send_typing_packet(channel):
        """
        Send the "XXX is typing..." packet to the specified channel

        Args:
            channel (discord.TextChannel): channel to send to
        """
        await channel.trigger_typing()

    @staticmethod
    async def reply(reference, content=None, embedded=None, channel=None):
        assert any([content, embedded]), "Must reply with one or more of {content (string), embedded (embedded message)}!"
        if channel is None:
            channel = reference.channel
        return await channel.send(content=content, embed=embedded, reference=reference, mention_author=False)

    @staticmethod
    async def react_unknown(message):
        await message.add_reaction(emojis.QUESTION)

    @staticmethod
    async def react_check(message):
        await message.add_reaction(emojis.CHECK)

    @staticmethod
    async def react_cross(message):
        await message.add_reaction(emojis.CROSS)

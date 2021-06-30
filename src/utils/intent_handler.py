from typing import Dict

import discord

from src.data import colors, emojis
from src.utils.reaction_handler import ReactionHandler


class IntentHandler:
    """ Intent handler superclass, each specific intent handler should extend this class """

    def __init__(self, bot, intent, description):
        """
        Initialize a command handler (should be overridden by each command)

        Args:
            bot (BotClient): bot interface
            intent (str): intent name
            description (str): short intent description
        """
        self.bot = bot
        self.intent = intent
        self.description = description

    async def on_intent_detected_wrapper(self, author, confidence, confidence_dict, message, channel, guild):
        """
        Wrapper method for automating some intent detected functionalities
        - THIS METHOD SHOULD NOT BE OVERRIDDEN!!!
        """
        # Call sub-method
        reply_message = await self.on_intent_detected(author, confidence, message, channel, guild)
        if reply_message is None:
            return

        await reply_message.add_reaction(emojis.MAGNIFYING_GLASS)
        await self.bot.react_cross(reply_message)

        async def on_react(_, _2, emote, _3, _4, _5):
            if emote == emojis.MAGNIFYING_GLASS:
                await self.bot.reply(reply_message, embedded=self.get_nlp_results_embedded(confidence_dict))
            elif emote == emojis.CROSS:
                await reply_message.delete()

        reaction_handler = ReactionHandler(author, reply_message, [emojis.MAGNIFYING_GLASS, emojis.CROSS], on_react)
        self.bot.register_reaction_handler(reaction_handler)

    async def on_intent_detected(self, author, confidence, message, channel, guild):
        """
        Executes the command, should be overridden in the subclass

        Args:
            author (discord.Member): user who triggered the intent
            confidence (float): confidence of the NLP prediction
            message (discord.Message): Discord message object
            channel (discord.TextChannel): text channel that the message is sent in
            guild (discord.Guild): guild that the message is sent in

        Returns:
            (discord.Message) reply message if applicable
        """

    def get_help_embedded(self):
        """
        Generates an embedded help message for this intent

        Returns:
            discord.Embed: embedded message
        """
        embedded = discord.Embed(
            title=f"Help for intent \"{self.intent}\"",
            description=f"{self.description}",
            color=colors.COLOR_HELP
        )

        embedded.add_field(name="**Description:**", value=f"> {self.description}", inline=False)
        return embedded

    @staticmethod
    def get_nlp_results_embedded(results):
        results = sorted(results.items(), key=lambda a: a[1], reverse=True)
        embedded = discord.Embed(
            title=f"Detailed results of this response",
            description=f"Best matching intent is \"{results[0][0]}\" with {results[0][1] * 100:05.2f}% confidence",
            color=colors.COLOR_NLP
        )
        detail_string = "```"
        for intent, confidence in results:
            detail_string += f"{intent:15s} ({confidence * 100:05.2f}%)\n"
        detail_string += "```"
        embedded.add_field(name="**Detailed results:**", value=detail_string, inline=False)
        return embedded

    def __str__(self):
        return f"Intent handler for \"{self.intent}\""

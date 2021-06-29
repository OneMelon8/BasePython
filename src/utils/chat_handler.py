# Built-in imports

# Project imports
from src.data import colors, settings, emojis
from src.nlp import primitive_model
from src.utils.reaction_handler import ReactionHandler
import src.utils.log_util as log
# External imports
import discord


class ChatHandler:
    """ Discord interface for the NLP modules """

    def __init__(self, bot):
        """
        Initialize a chat handler interface

        Args:
            bot (BotClient): bot instance
        """
        self.bot = bot
        self.initialize_nlp()

    async def on_message(self, author, message, channel, guild):
        """
        Called automatically after NLP intent is detected

        Args:
            author (discord.Member): message sender
            message (discord.Message): message to parse
            channel (discord.TextChannel): text channel that the message is sent in
            guild (discord.Guild): guild that the message is sent in
        """

        raw_message = message.content
        intent, confidence, confidence_dict = primitive_model.predict(raw_message)

        # If bot is not confident on the response, don't respond
        if confidence < settings.NLP_CONFIDENCE_THRESHOLD:
            return

        # Trigger intent if exists
        handler = self.bot.intent_handlers.get(intent)
        if handler is None:
            return

        await handler.on_intent_detected_wrapper(author, confidence, confidence_dict, message, channel, guild)

    @staticmethod
    def initialize_nlp():
        log.info("Loading NLP data... ")
        primitive_model.load_or_generate_data(force_generate=True)

        log.info("Training model...")
        primitive_model.create_and_train_model()
        log.info("Training complete! Model is now ready to be used!")

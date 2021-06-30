import random

from src.utils.intent_handler import IntentHandler


class GreetingIntentHandler(IntentHandler):
    def __init__(self, bot):
        IntentHandler.__init__(self, bot, "greeting", "Basic greetings")
        self.replies = ["Hello there", "Howdy", "You are in the presence of the great genius Baselard, state your purpose!", "Ohayou gozaimasu~"]

    async def on_intent_detected(self, author, confidence, message, channel, guild):
        await self.bot.send_typing_packet(channel)
        return await self.bot.reply(message, content=random.choice(self.replies))


class FarewellIntentHandler(IntentHandler):
    def __init__(self, bot):
        IntentHandler.__init__(self, bot, "farewell", "Basic farewell")
        self.replies = ["See ya later", "Mata ne~", "Aww, give me a head pat before you go~"]

    async def on_intent_detected(self, author, confidence, message, channel, guild):
        await self.bot.send_typing_packet(channel)
        return await self.bot.reply(message, content=random.choice(self.replies))


class HeadPatIntentHandler(IntentHandler):
    def __init__(self, bot):
        IntentHandler.__init__(self, bot, "headpat", "I like to be given head pats!")
        self.replies = ["Fuwa fuwa~", "Mm, I like head pats", "Why am I always squinting? Because I don't want anyone to see my eyes. Nope, nobody~"]

    async def on_intent_detected(self, author, confidence, message, channel, guild):
        await self.bot.send_typing_packet(channel)
        return await self.bot.reply(message, content=random.choice(self.replies))


###############################################################
def register_all(bot):
    """ Register all commands in this module """
    handlers = [GreetingIntentHandler(bot), FarewellIntentHandler(bot), HeadPatIntentHandler(bot)]
    for handler in handlers:
        bot.register_intent_handler(handler.intent, handler)

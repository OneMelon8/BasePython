import discord

import src.utils.log_util as log
from src.data import settings, emojis, colors
from src.nlp import primitive_model
from src.utils import string_util
from src.utils.command_handler import CommandHandler


class ToggleCommandHandler(CommandHandler):
    def __init__(self, bot):
        super().__init__(bot, "toggle", ["t"], "Toggle my NLP chat interface", "", "")

    async def on_command(self, author, command, args, message, channel, guild):
        self.bot.chat_enabled = not self.bot.chat_enabled
        emote = emojis.UNMUTE if self.bot.chat_enabled else emojis.MUTE
        await message.add_reaction(emote)
        status = "enabled" if self.bot.chat_enabled else "disabled"
        log.info(f"NLP chat interface is now {status}")


class IntentCommandHandler(CommandHandler):
    def __init__(self, bot):
        super().__init__(bot, "intent", ["i", "intents"], "Command to view and modify my NLP intents",
                         f"{settings.BOT_PREFIX}intent <info/list> [args...]",
                         f"> {settings.BOT_PREFIX}intent info greetings\n"
                         f"> {settings.BOT_PREFIX}intent list")
        self.is_reloading = False

    async def on_command(self, author, command, args, message, channel, guild):
        # Assert there is at least 1 arguments
        if len(args) < 1:
            await self.bot.reply(message, content=f"Invalid arguments! Check out `{settings.BOT_PREFIX}help intent`")
            return

        operation = args[0]
        if operation == "info" or operation == "i":
            if len(args) < 2:
                await self.bot.reply(message, content=f"Invalid arguments! Usage: `{settings.BOT_PREFIX}intent info <intent_name>`")
                return
            # Show intent information
            if args[1] not in primitive_model.intents:
                response = self.get_intent_not_found_embedded(args[1])
            else:
                response = self.get_intent_info_embedded(args[1])
            await self.bot.reply(message, embedded=response)
        elif operation == "list" or operation == "l":
            # List all intents
            await self.bot.reply(message, embedded=self.get_intent_list_embedded())
        else:
            await message.add_reaction(emojis.QUESTION)
            return

    ###############################
    # EMBEDDED MESSAGE GENERATORS #
    ###############################

    @staticmethod
    def get_intent_info_embedded(intent):
        embedded = discord.Embed(
            title=f"Information about intent \"{intent}\"",
            description=f"There is currently a total of **{len(primitive_model.utterances[intent])}** utterances for \"{intent}\"",
            color=colors.COLOR_NLP
        )
        embedded.add_field(name="**Utterances:**", value=f"> {string_util.quote_join(primitive_model.utterances[intent])}", inline=False)
        if primitive_model.model_changed:
            embedded.set_footer(text="* there are some pending changes to the model, reload to see them in action")
        return embedded

    @staticmethod
    def get_intent_not_found_embedded(intent):
        embedded = discord.Embed(
            title=f"Intent \"{intent}\" not found",
            description=f"Try using `{settings.BOT_PREFIX}intent list` to view all intents",
            color=colors.COLOR_NLP
        )
        if primitive_model.model_changed:
            embedded.set_footer(text="* there are some pending changes to the model, reload to see them in action")
        return embedded

    @staticmethod
    def get_intent_list_embedded():
        embedded = discord.Embed(
            title=f"List of intents in my NLP module",
            description=f"There is currently a total of **{len(primitive_model.intents)}** intents",
            color=colors.COLOR_NLP
        )
        embedded.add_field(name="**Intents:**", value=f"> {settings.SEP.join(primitive_model.intents)}", inline=False)
        if primitive_model.model_changed:
            embedded.set_footer(text="* there are some pending changes to the model, reload to see them in action")
        return embedded


###############################################################

def register_all(bot):
    """ Register all commands in this module """
    bot.register_command_handler(ToggleCommandHandler(bot))
    bot.register_command_handler(IntentCommandHandler(bot))

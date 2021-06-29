# Built-ins imports
import time

# Project imports
from src.utils import time_util, MoveMessageUtil
from src.utils.command_handler import CommandHandler
from src.data import colors, settings, emojis

# External imports
import discord


class DmReportCommandHandler(CommandHandler):
    def __init__(self, bot):
        super().__init__(bot, "report", ["vent"], "[DM Only] Report something to the moderators in AaH Discord", f"{settings.BOT_PREFIX}report [message...]", f"{settings.BOT_PREFIX}report I ate too many strawberries!")
        self.cooldowns = {}

    async def on_command(self, author, command, args, message, channel, guild):
        # DM-only command
        if not isinstance(channel, discord.DMChannel):
            await self.bot.reply(message, "This command is usable in direct message (DM) channels only!")
            return

        # Help in general
        if len(args) == 0:
            await self.bot.reply(message, content="Invalid report arguments!", embedded=self.get_help_embedded())
            return

        # Check cooldowns
        if self.cooldowns.get(author.id, -1) > time.time():
            # In cooldown, send "wait" message
            await self.bot.reply(message, content=f"This command should not be spammed. You need to wait {time_util.format_time(self.cooldowns[author.id] - time.time(), english=True)} before reporting again!")
            return
        # Not in cooldown, reset cooldown
        self.cooldowns[author.id] = time.time() + 60 * 60

        # Trigger typing
        await channel.trigger_typing()

        # Generate message embedded
        embedded = MoveMessageUtil.generate_embedded(message.author, message.content, message.attachments, is_dm=True)

        # Fetch MOVE_TO channel and send message
        channel = await self.bot.fetch_channel(settings.MOVE_TO_CHANNEL)
        sent_message = await channel.send(embed=embedded)

        # Send confirm message
        await self.bot.reply(message, content=f"`{time_util.formatted_now(include_date=True)}` >> Your report has been registered {emojis.CHECK}")

        # Send attachments if there are attachments
        if message.attachments:
            for attachment in message.attachments:
                file = await attachment.to_file()
                await sent_message.reply(content=f"Attached file `{attachment.filename}`:", file=file)


###############################################################

def register_all(bot):
    """ Register all commands in this module """
    bot.register_command_handler(DmReportCommandHandler(bot))


if __name__ == "__main__":
    cd = {}
    print(time.time())
    cd[1] = time.time()
    time.sleep(5)
    print(time.time())

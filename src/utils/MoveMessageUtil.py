# Project imports
from src.data import colors, settings, emojis
from src.utils import time_util

# External imports
import discord


async def move_message(bot, message):
    """
    Move the current message to MOVE_TO channel (in config)

    Args:
        bot (BotClient): bot to perform action on
        message (discord.Message): message to move
    """
    # Filter spam message
    raw_message = message.content
    if len(raw_message) <= 5:
        await message.add_reaction(emojis.QUESTION)
        return

    # Generate message embedded
    embedded = generate_embedded(message.author, message.content, message.attachments)
    # Delete message
    await message.delete()
    # Send confirm message
    await message.channel.send(content=f"`{time_util.formatted_now(include_date=True)}` >> Your report has been registered {emojis.CHECK}")
    # Fetch MOVE_TO channel
    channel = await bot.fetch_channel(settings.MOVE_TO_CHANNEL)
    # Send message to MOVE_TO channel
    sent_message = await channel.send(embed=embedded)

    # Scan for attachments
    if not message.attachments:
        return

    # If there is attachments, send attachment messages
    for attachment in message.attachments:
        file = await attachment.to_file()
        await sent_message.reply(content=f"Attached file `{attachment.filename}`:", file=file)


def generate_embedded(author, raw_message, attachments, is_dm=False):
    title = f"Message from {author.display_name}#{author.discriminator}"
    if is_dm:
        title = "[DM] " + title

    embedded = discord.Embed(
        title=title,
        description=f"Timestamp (UTC): {time_util.formatted_now(include_date=True)[:-4]}",
        color=colors.COLOR_HELP
    )
    embedded.add_field(name="**Message from:**", value=f"> {author.mention}", inline=False)
    if not raw_message:
        raw_message = "*no text message*"
    embedded.add_field(name="**Message details:**", value=f"> {raw_message}", inline=False)
    if attachments:
        # Add attachments field
        embedded.add_field(name="**Message attachments:**", value=f"> {settings.SEP.join(att.filename for att in attachments)}", inline=False)
    return embedded

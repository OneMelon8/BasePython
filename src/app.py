import os
import sys

import discord

# Stabilize imports
current_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(current_dir, ".."))  # two directories above

from src.bot import BotClient
from src.commands import utility_cmd, nlp_cmd, genshin_cmd
from src.utils.chat_handler import ChatHandler
from src.data.environment import DISCORD_TOKEN

print("Hello (happy) world!")
# Create intent
intent = discord.Intents.default()
intent.members = True

# Create and start the client
bot = BotClient(intents=intent)

# Register commands & intents
nlp_cmd.register_all(bot)
utility_cmd.register_all(bot)
genshin_cmd.register_all(bot)

# Register NLP chat handler
bot.register_chat_handler(ChatHandler(bot))

bot.run(DISCORD_TOKEN)

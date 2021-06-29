# Built-in imports
import time
from typing import *

# External imports
import discord


class ReactionHandler:
    """ Dynamic reaction handler, create a new instance and register every time ON_REACT is needed """

    def __init__(self, author, message, emotes, react_callback, timeout_callback=None, timeout=30, user_lock=False):
        """
        Constructs a dynamic reaction handler, times out automatically after a set duration

        Args:
            author (discord.Member): intended target member
            message (discord.Message): message that the reaction is on
            emotes (List[Union[discord.Emoji, str]]): list of target reaction emotes
            react_callback (function): callback function when the reaction is triggered
            timeout_callback (function): callback function when the reaction timed out
            timeout (int): how long will this reaction be valid for in seconds, default = 30
            user_lock (bool): can anyone use this reaction or can only the author, default = false (everyone)
        """
        self.author = author
        self.message = message
        self.emojis = emotes

        self.react_callback = react_callback
        self.timeout_callback = timeout_callback

        self.expire_time = time.time() + timeout
        self.user_lock = user_lock

        # Extra data that can be attached to this handler manually
        self.data = None

    def has_data(self):
        return bool(self.data)

    def set_data(self, data):
        self.data = data

    async def on_react(self, user, emote):
        """
        Called automatically when the emote is added

        Args:
            user (discord.Member): person who added the reaction
            emote (Union[discord.Emoji, str]): emote that was added

        Returns:
            bool: whether the reaction was successful
        """
        if self.react_callback is None or (user != self.author and self.user_lock):
            return False

        await self.react_callback(self.author, user, emote, self.message, self.message.channel, self.message.guild)
        return True

    async def on_timeout(self):
        """ Called automatically when the reaction times out """
        # Not really sure about what parameters to put here...?
        if self.timeout_callback is None:
            return
        await self.timeout_callback(self.author, self.message, self.message.channel, self.message.guild)

    def __str__(self):
        return f"Reaction handler for \"{self.emojis}\""

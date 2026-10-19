import logging

from bot_instance import bot
from config import DISCORD_TOKEN
import commands
import events
import cringe


handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='w'
)

bot.run(DISCORD_TOKEN, log_handler=handler, log_level=logging.DEBUG)

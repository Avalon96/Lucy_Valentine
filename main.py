import logging
import os

from dotenv import load_dotenv

from bot_instance import bot
import commands
import events
import cringe


load_dotenv()
token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='w'
)

bot.run(token, log_handler=handler, log_level=logging.DEBUG)

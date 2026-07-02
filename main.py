import logging
import os

from dotenv import load_dotenv

from bot_instance import bot
import commands   # noqa: F401  (registers !cmd, !batch, !del, !allcmd, !export, !json, !cringe, !uncringe, !allcringe)
import events     # noqa: F401  (registers on_message, on_raw_reaction_add, on_ready, auto_export)

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='w'
)

bot.run(token, log_handler=handler, log_level=logging.DEBUG)

import hashlib
import os
import random
import discord
from discord.ext import tasks
from datetime import time
from zoneinfo import ZoneInfo

from bot_instance import bot
from cringe import expire_cringe
from storage import cringe_list, custom_commands
from config import (
    COMMANDS_FILE,
    EXPORT_HASH_FILE,
    BOT_PAT,
    HEART,
    EXPORT_CHANNEL_ID,
    COMMAND_PREFIX,
    CRINGE_REACTION_EMOJIS
)

triggered_reactions = set()


# Reaction Event
@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id:
        return
    channel = bot.get_channel(payload.channel_id)
    if channel is None:
        return

    if payload.user_id in cringe_list:
        # A partial message and user ID are enough to remove a reaction, no fetching needed
        message = channel.get_partial_message(payload.message_id)
        try:
            await message.remove_reaction(payload.emoji, discord.Object(id=payload.user_id))
        except (discord.Forbidden, discord.NotFound):
            pass
        return

    if str(payload.emoji) != BOT_PAT:
        return
    key = (payload.user_id, payload.message_id)
    if key in triggered_reactions:
        return

    # Only fetch once we know it's a new pat, to check it's on one of Lucy's messages
    message = await channel.fetch_message(payload.message_id)
    if message.author.id != bot.user.id:
        return
    triggered_reactions.add(key)

    await channel.send(f"<@{payload.user_id}> {HEART}")


# Send command
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.author.id in cringe_list and message.channel.id != EXPORT_CHANNEL_ID:
        await message.add_reaction(random.choice(CRINGE_REACTION_EMOJIS))
        return

    if BOT_PAT in message.content:
        await message.add_reaction(HEART)
        return

    if not message.content.startswith(COMMAND_PREFIX):
        return

    content = message.content[len(COMMAND_PREFIX):].lower()
    if content in custom_commands:
        await message.channel.send(custom_commands[content])
        return

    await bot.process_commands(message)


tz = ZoneInfo("UTC")
# Auto Export JSON
@tasks.loop(time=time(hour=0, minute=0, tzinfo=tz))
async def auto_export():
    channel = bot.get_channel(EXPORT_CHANNEL_ID)
    if channel is None:
        print("Auto-export channel not found.")
        return

    if not os.path.exists(COMMANDS_FILE):
        return

    with open(COMMANDS_FILE, "rb") as f:
        current_hash = hashlib.sha256(f.read()).hexdigest()

    last_hash = None
    if os.path.exists(EXPORT_HASH_FILE):
        with open(EXPORT_HASH_FILE, "r") as f:
            last_hash = f.read().strip()

    if current_hash == last_hash:
        return

    await channel.send("Here is your JSON file master ❤️")
    await channel.send(file=discord.File(COMMANDS_FILE))

    with open(EXPORT_HASH_FILE, "w") as f:
        f.write(current_hash)


# Check bot online
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    if not auto_export.is_running():
        auto_export.start()
    if not expire_cringe.is_running():
        expire_cringe.start()

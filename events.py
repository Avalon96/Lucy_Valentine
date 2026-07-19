import os
import random
import discord
from discord.ext import tasks
from datetime import time
from zoneinfo import ZoneInfo

from bot_instance import bot
from storage import cringe_list, custom_commands
from config import (
    COMMANDS_FILE,
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
    message = await channel.fetch_message(payload.message_id)

    if payload.user_id in cringe_list:
        member = payload.member or (message.guild.get_member(payload.user_id) if message.guild else None)
        if member is None:
            member = await bot.fetch_user(payload.user_id)

        try:
            await message.remove_reaction(payload.emoji, member)
        except (discord.Forbidden, discord.NotFound):
            pass
        return

    if str(payload.emoji) != BOT_PAT:
        return
    if message.author.id != bot.user.id:
        return
    key = (payload.user_id, payload.message_id)
    if key in triggered_reactions:
        return
    triggered_reactions.add(key)

    user = payload.member
    if user is None:
        user = await bot.fetch_user(payload.user_id)

    await channel.send(f"{user.mention} {HEART}")


# Send command
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.author.id in cringe_list:
        await message.add_reaction(random.choice(CRINGE_REACTION_EMOJIS))
        return

    if BOT_PAT in message.content:
        await message.add_reaction(HEART)
        return

    if not message.content.startswith(COMMAND_PREFIX):
        return

    if message.content.startswith(COMMAND_PREFIX):
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

    await channel.send("Here is your JSON file master ❤️")
    await channel.send(file=discord.File(COMMANDS_FILE))


# Check bot online
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    auto_export.start()

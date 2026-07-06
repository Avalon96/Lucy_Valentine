import os
import discord
from discord.ext import tasks

from bot_instance import bot
from storage import cringe_list, custom_commands
from config import (
    COMMANDS_FILE,
    BOT_PAT,
    HEART,
    DISGUST_MELU,
    SORA_UNAMUSED,
    EXPORT_CHANNEL_ID,
    COMMAND_PREFIX
)

triggered_reactions = set()


# Reaction Event
@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id:
        return

    if str(payload.emoji) != BOT_PAT:
        return

    channel = bot.get_channel(payload.channel_id)
    if channel is None:
        return

    message = await channel.fetch_message(payload.message_id)
    if message.author.id != bot.user.id:
        return

    key = (payload.user_id, payload.message_id)
    if key in triggered_reactions:
        return

    triggered_reactions.add(key)

    user = payload.member

    if payload.user_id in cringe_list:
        await channel.send(f"{user.mention} Don't touch me!")
        if "soraslap" in custom_commands:
            await channel.send(custom_commands["soraslap"])
        return

    if user is None:
        user = await bot.fetch_user(payload.user_id)

    await channel.send(f"{user.mention} {HEART}")


# Send command
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if BOT_PAT in message.content:
        if message.author.id in cringe_list:
            await message.add_reaction(DISGUST_MELU)
        else:
            await message.add_reaction(HEART)
        return

    if not message.content.startswith(COMMAND_PREFIX):
        return
    else:
        content = message.content[len(COMMAND_PREFIX):]

        if content in custom_commands:
            if message.author.id in cringe_list:
                await message.add_reaction(SORA_UNAMUSED)
            else:
                await message.channel.send(custom_commands[content])
            return

        await bot.process_commands(message)


# Auto Export JSON
@tasks.loop(hours=24)
async def auto_export():
    channel = bot.get_channel(EXPORT_CHANNEL_ID)
    if channel is None:
        print("Auto-export channel not found.")
        return
    if not os.path.exists(COMMANDS_FILE):
        return
    await channel.send("Here is your JSON file master ❤️")
    await channel.send(file=discord.File(COMMANDS_FILE))


@auto_export.before_loop
async def before_auto_export():
    await bot.wait_until_ready()


# Check bot online
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    if not auto_export.is_running():
        auto_export.start()

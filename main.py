import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

custom_commands = {}

@bot.command()
async def command(ctx, name: str, *, response: str):
    custom_commands[name] = response
    await ctx.send(f"Saved command `{name}` → `{response}`")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content

    # If message matches stored command
    if content in custom_commands:
        await message.channel.send(custom_commands[content])
        return

    # Still allow normal commands like !command to work
    await bot.process_commands(message)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)

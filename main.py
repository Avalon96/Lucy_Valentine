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
ALLOWED_ROLES = ("Uma Musume Vice Pope", "The Island Owner")

@bot.command()
async def command(ctx, name: str, *, response: str):

    if not any(role.name in ALLOWED_ROLES for role in ctx.author.roles):
        sent_message = await ctx.send("Only Uma Musume Vice Popes and The Island Owner can use this command.")
        await sent_message.add_reaction("<:LucyPat:1521635572907774072>")
        return

    custom_commands[name] = response
    await ctx.send(f"Saved command `{name}` → `{response}`")

@bot.command(name="del")
async def delete_command(ctx, name: str):
    if not any(role.name in ALLOWED_ROLES for role in ctx.author.roles):
        sent_message = await ctx.send("Only Uma Musume Vice Popes and The Island Owner can use this command.")
        await sent_message.add_reaction("<:LucyPat:1521635572907774072>")
        return

    if name in custom_commands:
        del custom_commands[name]
        await ctx.send(f"Removed command `{name}`")
    else:
        await ctx.send(f"Command `{name}` not found")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content

    if content in custom_commands:
        sent_message = await message.channel.send(custom_commands[content])
        await sent_message.add_reaction("<a:LucyPat:1521201578474737754>")
        return

    await bot.process_commands(message)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)

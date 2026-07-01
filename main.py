import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import json

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='w'
)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

COMMANDS_FILE = "custom_commands.json"


# JSON
def load_commands():
    if os.path.exists(COMMANDS_FILE):
        with open(COMMANDS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_commands():
    with open(COMMANDS_FILE, "w") as f:
        json.dump(custom_commands, f, indent=4)


custom_commands = load_commands()
ALLOWED_ROLES = ("The Island Owner", "Uma Musume Vice Pope")


# Export JSON
@bot.command()
async def export(ctx):
    if not any(role.name in ALLOWED_ROLES for role in ctx.author.roles):
        sent_message = await ctx.send(
            f"Only {' and '.join(ALLOWED_ROLES)}s can use this command."
        )
        await sent_message.add_reaction("<:LucyPat:1521635572907774072>")
        return
    if not os.path.exists(COMMANDS_FILE):
        await ctx.send("No commands file found yet.")
        return
    await ctx.send(file=discord.File(COMMANDS_FILE))


# !command
@bot.command()
async def command(ctx, name: str, *, response: str):

    if not any(role.name in ALLOWED_ROLES for role in ctx.author.roles):
        sent_message = await ctx.send(
            f"Only {' and '.join(ALLOWED_ROLES)}s can use this command."
        )
        await sent_message.add_reaction("<:LucyPat:1521635572907774072>")
        return
    if not name.startswith("!"):
        await ctx.send("Command name must start with `!`")
        return
    if (name.startswith("!")):
        if name in custom_commands:
            await ctx.send(f"Command `{name}` already exists.")
            return
        custom_commands[name] = response
        save_commands()
        await ctx.send(f"Saved command `{name}` → `{response}`")


# !del
@bot.command(name="del")
async def delete_command(ctx, name: str):
    if not any(role.name in ALLOWED_ROLES for role in ctx.author.roles):
        sent_message = await ctx.send(
            f"Only {' and '.join(ALLOWED_ROLES)}s can use this command."
        )
        await sent_message.add_reaction("<:LucyPat:1521635572907774072>")
        return

    if not name.startswith("!"):
        await ctx.send("Command name must start with `!`")
        return
    if name in custom_commands:
        del custom_commands[name]
        save_commands()
        await ctx.send(f"Removed command `{name}`")
    else:
        await ctx.send(f"Command `{name}` not found")


# !allcmd
@bot.command()
async def allcmd(ctx):
    sorted_commands = sorted(custom_commands.keys())
    embed = discord.Embed(
        title="All Commands",
        description="\n".join(sorted_commands),
        colour=discord.Color.blue()
    )
    await ctx.send(embed=embed)


# Send command
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


# Check bot online
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)

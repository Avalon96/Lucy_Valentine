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
@bot.command(name="export")
async def export_command_json(ctx):
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
        title=f"All Commands ({len(sorted_commands)})",
        colour=discord.Color.blue()
    )

    columns = 3
    chunk_size = -(-len(sorted_commands) // columns)  # ceiling division
    chunks = [sorted_commands[i:i + chunk_size] for i in range(0, len(sorted_commands), chunk_size)]

    for chunk in chunks:
        embed.add_field(name="\u200b", value="\n".join(chunk), inline=True)

    await ctx.send(embed=embed)


# !batch
@bot.command(name="batch")
async def batch_add_commands(ctx, *, bulk_input: str):
    if not any(role.name in ALLOWED_ROLES for role in ctx.author.roles):
        sent_message = await ctx.send(
            f"Only {' and '.join(ALLOWED_ROLES)}s can use this command."
        )
        await sent_message.add_reaction("<:LucyPat:1521635572907774072>")
        return

    lines = bulk_input.strip().splitlines()
    added = []
    skipped = []
    invalid = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            invalid.append(line)
            continue
        name, response = parts
        if not name.startswith("!"):
            invalid.append(line)
            continue
        if name in custom_commands:
            skipped.append(name)
            continue
        custom_commands[name] = response
        added.append(name)

    if added:
        save_commands()

    result = []
    if added:
        result.append(f"Added ({len(added)}): {', '.join(added)}")
    if skipped:
        result.append(f"Skipped, already exist ({len(skipped)}): {', '.join(skipped)}")
    if invalid:
        result.append(f"Invalid lines ({len(invalid)}): {', '.join(invalid)}")

    await ctx.send("\n".join(result) if result else "Nothing to add.")


# !json
@bot.command(name="json")
async def import_commands(ctx, *, json_input: str = None):
    if not any(role.name in ALLOWED_ROLES for role in ctx.author.roles):
        sent_message = await ctx.send(
            f"Only {' and '.join(ALLOWED_ROLES)}s can use this command."
        )
        await sent_message.add_reaction("<:LucyPat:1521635572907774072>")
        return

    # Support either a pasted JSON string or an attached .json file
    raw_data = None
    if ctx.message.attachments:
        attachment = ctx.message.attachments[0]
        if not attachment.filename.endswith(".json"):
            await ctx.send("Attached file must be a `.json` file.")
            return
        raw_data = (await attachment.read()).decode("utf-8")
    elif json_input:
        raw_data = json_input
    else:
        await ctx.send("Provide JSON as text after the command, or attach a `.json` file.")
        return

    try:
        imported = json.loads(raw_data)
    except json.JSONDecodeError as e:
        await ctx.send(f"Invalid JSON: {e}")
        return

    if not isinstance(imported, dict):
        await ctx.send("JSON must be an object of `\"!name\": \"response\"` pairs.")
        return

    added = []
    skipped = []
    invalid = []

    for name, response in imported.items():
        if not isinstance(name, str) or not isinstance(response, str):
            invalid.append(str(name))
            continue
        if not name.startswith("!"):
            invalid.append(name)
            continue
        if name in custom_commands:
            skipped.append(name)
            continue
        custom_commands[name] = response
        added.append(name)

    if added:
        save_commands()

    result = []
    if added:
        result.append(f"Added ({len(added)}): {', '.join(added)}")
    if skipped:
        result.append(f"Skipped, already exist ({len(skipped)}): {', '.join(skipped)}")
    if invalid:
        result.append(f"Invalid entries ({len(invalid)}): {', '.join(invalid)}")

    await ctx.send("\n".join(result) if result else "Nothing to import.")


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

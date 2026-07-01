import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import json
from discord.ext import tasks


load_dotenv()
token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='w'
)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

OVERLORD_ROLE = "The Island Owner"
ALLOWED_ROLES = ("The Island Owner", "Uma Musume Vice Pope")
RESERVED_COMMANDS = {
    "!cmd",
    "!batch",
    "!del",
    "!allcmd",
    "!export",
    "!json",
    "!cringe",
    "!uncringe",
    "!allcringe"
}
COMMANDS_FILE = "custom_commands.json"
CRINGE_FILE = "cringe_list.json"
PAT_LUCY = "<a:LucyPat:1521201578474737754>"
HEART = "❤️"

DISGUST_MELU = "<:MelusineDisgust:1521196798046109769>"
SORA_UNAMUSED = "<a:SoraUnamused:1521201633961181405>"


# # DEBUG
# @bot.event
# async def on_command_error(ctx, error):
#     await ctx.send(f"Error: {error}")


# Reaction Event
triggered_reactions = set()

@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id:
        return

    if str(payload.emoji) != PAT_LUCY:
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
        await channel.send(f"{user.mention}")
        if "!soraslap" in custom_commands:
            await channel.send(custom_commands["!soraslap"])
        return

    if user is None:
        user = await bot.fetch_user(payload.user_id)

    await channel.send(f"{user.mention} {HEART}")


# Command JSON
def load_commands():
    if os.path.exists(COMMANDS_FILE):
        with open(COMMANDS_FILE, "r") as f:
            return json.load(f)
    with open(COMMANDS_FILE, "w") as f:
        json.dump({}, f)
    return {}


def save_commands():
    with open(COMMANDS_FILE, "w") as f:
        json.dump(custom_commands, f, indent=4)

custom_commands = load_commands()


# Cringe List JSON
def load_cringe_list():
    if os.path.exists(CRINGE_FILE):
        with open(CRINGE_FILE, "r") as f:
            return json.load(f)
    with open(CRINGE_FILE, "w") as f:
        json.dump([], f)
    return []

def save_cringe_list():
    with open(CRINGE_FILE, "w") as f:
        json.dump(cringe_list, f, indent=4)

cringe_list = load_cringe_list()


# !cmd
@bot.command(name="cmd")
async def add_command(ctx, name: str, *, response: str):
    if not any(role.name in ALLOWED_ROLES for role in ctx.author.roles):
        sent_message = await ctx.send(
            f"Only {' and '.join(ALLOWED_ROLES)}s can use this command."
        )
        return
    if not name.startswith("!"):
        await ctx.send("Command name must start with `!`")
        return
    if (name.startswith("!")):
        if name in RESERVED_COMMANDS:
            await ctx.send(f"`{name}` is a reserved command name.")
            return
        if name in custom_commands:
            await ctx.send(f"Command `{name}` already exists.")
            return
        custom_commands[name] = response
        save_commands()
        await ctx.send(f"Saved command `{name}` → `{response}`")


# !batch
@bot.command(name="batch")
async def batch_add_commands(ctx, *, bulk_input: str):
    if not any(role.name in ALLOWED_ROLES for role in ctx.author.roles):
        sent_message = await ctx.send(
            f"Only {' and '.join(ALLOWED_ROLES)}s can use this command."
        )
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
        if name in RESERVED_COMMANDS:
            await ctx.send(f"`{name}` is a reserved command name.")
            return
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


# !del
@bot.command(name="del")
async def delete_command(ctx, name: str):
    if not any(role.name in ALLOWED_ROLES for role in ctx.author.roles):
        sent_message = await ctx.send(
            f"Only {' and '.join(ALLOWED_ROLES)}s can use this command."
        )
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
@bot.command(name="allcmd")
async def show_commands(ctx):
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


# !export
@bot.command(name="export")
async def export_command_json(ctx):
    if not any(role.name in ALLOWED_ROLES for role in ctx.author.roles):
        sent_message = await ctx.send(
            f"Only {' and '.join(ALLOWED_ROLES)}s can use this command."
        )
        return
    if not os.path.exists(COMMANDS_FILE):
        await ctx.send("No commands file found yet.")
        return
    await ctx.send("Here is your JSON file master ❤️")
    await ctx.send(file=discord.File(COMMANDS_FILE))


# !json
@bot.command(name="json")
async def import_commands(ctx, *, json_input: str = None):
    if not any(role.name in ALLOWED_ROLES for role in ctx.author.roles):
        sent_message = await ctx.send(
            f"Only {' and '.join(ALLOWED_ROLES)}s can use this command."
        )
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
        if name in RESERVED_COMMANDS:
            await ctx.send(f"`{name}` is a reserved command name.")
            return
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


# !cringe
@bot.command(name="cringe")
async def add_to_cringe_list(ctx, *, member: discord.Member):
    if not any(role.name == OVERLORD_ROLE for role in ctx.author.roles):
        await ctx.send(f"Only {OVERLORD_ROLE} can declare someone as cringe.")
        return
    if member.id not in cringe_list:
        cringe_list.append(member.id)
        save_cringe_list()
        await ctx.send(f"{member.display_name} added to cringe list.",
                       allowed_mentions=discord.AllowedMentions(users=False))
    else:
        await ctx.send(f"{member.display_name} is already in the cringe list.",
                       allowed_mentions=discord.AllowedMentions(users=False))


# !uncringe
@bot.command(name="uncringe")
async def remove_from_cringe_list(ctx, *, member: discord.Member):
    if not any(role.name == OVERLORD_ROLE for role in ctx.author.roles):
        await ctx.send(f"Only {OVERLORD_ROLE} can declare someone as not cringe anymore.")
        return
    if member.id in cringe_list:
        cringe_list.remove(member.id)
        save_cringe_list()
        await ctx.send(f"{member.display_name} removed from cringe list.",
                       allowed_mentions=discord.AllowedMentions(users=False))
    else:
        await ctx.send(f"{member.display_name} is not in the cringe list.",
                       allowed_mentions=discord.AllowedMentions(users=False))


# !allcringe
@bot.command(name="allcringe")
async def show_cringe_list(ctx):
    names = []
    for user_id in cringe_list:
        user = await bot.fetch_user(user_id)
        names.append(user.display_name)

    sorted_names = sorted(names)

    embed = discord.Embed(
        title=f"Cringe List ({len(sorted_names)})",
        description="\n".join(sorted_names) if sorted_names else "No one yet.",
        colour=discord.Color.blue()
    )

    await ctx.send(embed=embed)


# Send command
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content

    if PAT_LUCY in content:
        if message.author.id in cringe_list:
            await message.add_reaction(DISGUST_MELU)
        else:
            await message.add_reaction(HEART)
        return

    if content in custom_commands:
        if message.author.id in cringe_list:
            await message.add_reaction(SORA_UNAMUSED)
        else:
            sent_message = await message.channel.send(custom_commands[content])
        return

    await bot.process_commands(message)


# Auto Export JSON
EXPORT_CHANNEL_ID = 1521643823644803234

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


bot.run(token, log_handler=handler, log_level=logging.DEBUG)

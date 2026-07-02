import json
import os

import discord

from bot_instance import bot
import storage
from config import ALLOWED_ROLES, RESERVED_COMMANDS, OVERLORD_ROLE, COMMANDS_FILE


# !cmd
@bot.command(name="cmd")
async def add_command(ctx, name: str, *, response: str):
    if not any(role.name in ALLOWED_ROLES for role in ctx.author.roles):
        await ctx.send(f"Only {' and '.join(ALLOWED_ROLES)}s can use this command.")
        return
    if not name.startswith("!"):
        await ctx.send("Command name must start with `!`")
        return
    if (name.startswith("!")):
        if name in RESERVED_COMMANDS:
            await ctx.send(f"`{name}` is a reserved command name.")
            return
        if name in storage.custom_commands:
            await ctx.send(f"Command `{name}` already exists.")
            return
        storage.custom_commands[name] = response
        storage.save_commands()
        await ctx.send(f"Saved command `{name}` → `{response}`")


# !batch
@bot.command(name="batch")
async def batch_add_commands(ctx, *, bulk_input: str):
    if not any(role.name in ALLOWED_ROLES for role in ctx.author.roles):
        await ctx.send(f"Only {' and '.join(ALLOWED_ROLES)}s can use this command.")
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
        if name in storage.custom_commands:
            skipped.append(name)
            continue
        storage.custom_commands[name] = response
        added.append(name)

    if added:
        storage.save_commands()

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
        await ctx.send(f"Only {' and '.join(ALLOWED_ROLES)}s can use this command.")
        return

    if not name.startswith("!"):
        await ctx.send("Command name must start with `!`")
        return
    if name in storage.custom_commands:
        del storage.custom_commands[name]
        storage.save_commands()
        await ctx.send(f"Removed command `{name}`")
    else:
        await ctx.send(f"Command `{name}` not found")


# !allcmd
@bot.command(name="allcmd")
async def show_commands(ctx):
    sorted_commands = sorted(storage.custom_commands.keys())
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
        await ctx.send(f"Only {' and '.join(ALLOWED_ROLES)}s can use this command.")
        return
    if not os.path.exists(COMMANDS_FILE):
        await ctx.send("No commands file found yet.")
        return
    await ctx.send("Here is your JSON file master ❤️")
    await ctx.send(file=discord.File(COMMANDS_FILE))


# !import
@bot.command(name="import")
async def import_commands(ctx, *, json_input: str = None):
    if not any(role.name in ALLOWED_ROLES for role in ctx.author.roles):
        await ctx.send(f"Only {' and '.join(ALLOWED_ROLES)}s can use this command.")
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
        if name in storage.custom_commands:
            skipped.append(name)
            continue
        storage.custom_commands[name] = response
        added.append(name)

    if added:
        storage.save_commands()

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
        await ctx.send(f"Only {OVERLORD_ROLE} can decide whether someone is cringe or not.")
        return
    if member.id not in storage.cringe_list:
        storage.cringe_list.append(member.id)
        storage.save_cringe_list()
        await ctx.send(f"{member.display_name} added to cringe list.",
                       allowed_mentions=discord.AllowedMentions(users=False))
    else:
        await ctx.send(f"{member.display_name} is already in the cringe list.",
                       allowed_mentions=discord.AllowedMentions(users=False))


# !uncringe
@bot.command(name="uncringe")
async def remove_from_cringe_list(ctx, *, member: discord.Member):
    if not any(role.name == OVERLORD_ROLE for role in ctx.author.roles):
        await ctx.send(f"Only {OVERLORD_ROLE} can decide whether someone is cringe or not.")
        return
    if member.id in storage.cringe_list:
        storage.cringe_list.remove(member.id)
        storage.save_cringe_list()
        await ctx.send(f"{member.display_name} removed from cringe list.",
                       allowed_mentions=discord.AllowedMentions(users=False))
    else:
        await ctx.send(f"{member.display_name} is not in the cringe list.",
                       allowed_mentions=discord.AllowedMentions(users=False))


# !allcringe
@bot.command(name="allcringe")
async def show_cringe_list(ctx):
    names = []
    for user_id in storage.cringe_list:
        user = await bot.fetch_user(user_id)
        names.append(user.display_name)

    sorted_names = sorted(names)

    embed = discord.Embed(
        title=f"Cringe List ({len(sorted_names)})",
        description="\n".join(sorted_names) if sorted_names else "No one yet.",
        colour=discord.Color.blue()
    )

    await ctx.send(embed=embed)


# # DEBUG
# @bot.event
# async def on_command_error(ctx, error):
#     await ctx.send(f"Error: {error}")

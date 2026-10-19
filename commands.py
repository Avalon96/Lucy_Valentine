import io
import json
import os
import discord
from discord.ext.commands import Bot, CheckFailure, check

from bot_instance import bot
from storage import (
    save_commands,
    save_cringe_list,
    custom_commands,
    cringe_list
)
from config import (
    ALLOWED_ROLES,
    COMMAND_PREFIX,
    RESERVED_COMMANDS,
    OVERLORD_ROLE,
    COMMANDS_FILE,
    ENV
)


def has_any_role(member, *role_names):
    return any(role.name in role_names for role in member.roles)


def requires_roles(*role_names):
    """Only let members with one of these roles run the command, telling everyone else who can."""
    async def predicate(ctx):
        if has_any_role(ctx.author, *role_names):
            return True
        who = f"{' and '.join(role_names)}s" if len(role_names) > 1 else role_names[0]
        await ctx.send(f"Only {who} can use this command.")
        return False
    return check(predicate)


# !cmd
@bot.command(name="cmd")
@requires_roles(*ALLOWED_ROLES)
async def add_command(ctx, name: str, *, response: str):
    name = name.lstrip(COMMAND_PREFIX).lower()
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
@requires_roles(*ALLOWED_ROLES)
async def batch_add_commands(ctx, *, bulk_input: str):
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
        name = name.lstrip(COMMAND_PREFIX).lower()
        if name in RESERVED_COMMANDS:
            await ctx.send(f"`{name}` is a reserved command name and cannot be added.")
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
        result.append(f"Invalid lines ({len(invalid)}): {', '.join(invalid)}")

    await ctx.send("\n".join(result) if result else "Nothing to add.")


# !del
@bot.command(name="del")
@requires_roles(*ALLOWED_ROLES)
async def delete_command(ctx, name: str):
    name = name.lstrip(COMMAND_PREFIX).lower()
    if name in RESERVED_COMMANDS:
        await ctx.send(f"`{name}` is a reserved command name and cannot be deleted.")
        return
    if name in custom_commands:
        del custom_commands[name]
        save_commands()
        await ctx.send(f"Removed command `{name}`")
    else:
        await ctx.send(f"Command `{name}` not found")


# !batchdel
@bot.command(name="batchdel")
@requires_roles(OVERLORD_ROLE)
async def batch_delete_commands(ctx, *, bulk_input: str):
    
    lines = bulk_input.strip().splitlines()
    deleted = []
    not_found = []
    invalid = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        name = line.lstrip(COMMAND_PREFIX).lower()
        if name in RESERVED_COMMANDS:
            await ctx.send(f"`{name}` is a reserved command name and cannot be deleted.")
            invalid.append(name)
            continue
        if name not in custom_commands:
            not_found.append(name)
        else:
            del custom_commands[name]
            deleted.append(name)

    if deleted:
        save_commands()

    result = []
    if deleted:
        result.append(f"Deleted ({len(deleted)}): {', '.join(deleted)}")
    if not_found:
        result.append(f"Not found ({len(not_found)}): {', '.join(not_found)}")
    if invalid:
        result.append(f"Invalid lines ({len(invalid)}): {', '.join(invalid)}")

    await ctx.send("\n".join(result) if result else "Nothing to delete.")


# !allcmd
@bot.command(name="allcmd")
async def show_commands(ctx):
    sorted_commands = sorted(custom_commands.keys())
    if not sorted_commands:
        await ctx.send("No commands yet.")
        return

    # Split into 3 columns, starting extra columns if one would pass Discord's 1024-char field limit
    per_column = -(-len(sorted_commands) // 3)
    columns = [[]]
    column_length = 0
    for name in sorted_commands:
        if columns[-1] and (len(columns[-1]) >= per_column or column_length + len(name) + 1 > 1024):
            columns.append([])
            column_length = 0
        columns[-1].append(name)
        column_length += len(name) + 1

    # 3 columns per embed keeps each message under Discord's 6000-char embed limit
    for i in range(0, len(columns), 3):
        embed = discord.Embed(
            title=f"All Commands ({len(sorted_commands)})" if i == 0 else None,
            colour=discord.Color(0xAD9FF0)
        )
        for column in columns[i:i + 3]:
            embed.add_field(name="\u200b", value="\n".join(column), inline=True)
        await ctx.send(embed=embed)


# !export
@bot.command(name="export")
@requires_roles(*ALLOWED_ROLES)
async def export_command_json(ctx, *, flag: str = None):
    if not os.path.exists(COMMANDS_FILE):
        await ctx.send("No commands file found yet.")
        return

    if flag and flag.strip().lower() == "--key":
        if not custom_commands:
            await ctx.send("No commands to export.")
            return
        keys_text = "\n".join(custom_commands.keys())
        buffer = io.BytesIO(keys_text.encode("utf-8"))
        await ctx.send("Here are your command names master ❤️", file=discord.File(buffer, filename="commands.txt"))
        return

    await ctx.send("Here is your JSON file master ❤️")
    await ctx.send(file=discord.File(COMMANDS_FILE))


# !import
@bot.command(name="import")
@requires_roles(*ALLOWED_ROLES)
async def import_commands(ctx, *, json_input: str = None):
    overwrite = False
    if json_input and json_input.strip().lower().startswith("--overwrite"):
        if not has_any_role(ctx.author, OVERLORD_ROLE):
            await ctx.send(f"Only the {OVERLORD_ROLE} can use --overwrite.")
            return
        overwrite = True
        json_input = json_input.strip()[len("--overwrite"):].strip() or None

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
        await ctx.send("Provide JSON as text after the command, or attach a `.json` file."
                       "Use `--overwrite` to replace all existing commands.")
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
    invalid = []
    valid_entries = {}
    for name, response in imported.items():
        name = name.lstrip(COMMAND_PREFIX).lower()
        if name in RESERVED_COMMANDS:
            invalid.append(name)
            continue
        valid_entries[name] = response
        added.append(name)

    if overwrite:
        custom_commands.clear()
        custom_commands.update(valid_entries)
    else:
        skipped = []
        added = []
        for name, response in valid_entries.items():
            if name in custom_commands:
                skipped.append(name)
                continue
            custom_commands[name] = response
            added.append(name)

    if added or overwrite:
        save_commands()

    result = []
    if overwrite:
        result.append(f"Cleared existing commands and imported {len(added)}: {', '.join(added)}")
    else:
        if added:
            result.append(f"Added ({len(added)}): {', '.join(added)}")
        if skipped:
            result.append(f"Skipped, already exist ({len(skipped)}): {', '.join(skipped)}")
    if invalid:
        result.append(f"Invalid entries ({len(invalid)}): {', '.join(invalid)}")
    await ctx.send("\n".join(result) if result else "Nothing to import.")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CheckFailure):
        return  # requires_roles already replied
    if ENV == "development":
        await ctx.send(f"Error: {error}")
    else:
        await Bot.on_command_error(bot, ctx, error)  # discord.py's default: log the error

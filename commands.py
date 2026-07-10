import io
import json
import os
import discord
import asyncio
from dotenv import load_dotenv

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
    OVERLORD_ID,
    RESERVED_COMMANDS,
    OVERLORD_ROLE,
    COMMANDS_FILE,
    TIMEOUT
)

# !cmd
@bot.command(name="cmd")
async def add_command(ctx, name: str, *, response: str):
    if not any(role.name in ALLOWED_ROLES for role in ctx.author.roles):
        await ctx.send(f"Only {' and '.join(ALLOWED_ROLES)}s can use this command.")
        return
    name = name.lstrip(COMMAND_PREFIX)
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
        name = name.lstrip(COMMAND_PREFIX)
        if name in RESERVED_COMMANDS:
            await ctx.send(f"`{name}` is a reserved command name and cannot be deleted.")
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
async def delete_command(ctx, name: str):
    if not any(role.name in ALLOWED_ROLES for role in ctx.author.roles):
        await ctx.send(f"Only {' and '.join(ALLOWED_ROLES)}s can use this command.")
        return

    name = name.lstrip(COMMAND_PREFIX)
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
async def batch_delete_commands(ctx, *, bulk_input: str):
    if not any(role.name == OVERLORD_ROLE for role in ctx.author.roles):
        await ctx.send(f"Only {OVERLORD_ROLE} can use this command.")
        return
    
    lines = bulk_input.strip().splitlines()
    deleted = []
    not_found = []
    invalid = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        name = line.lstrip(COMMAND_PREFIX)
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
async def export_command_json(ctx, *, flag: str = None):
    if not any(role.name in ALLOWED_ROLES for role in ctx.author.roles):
        await ctx.send(f"Only {' and '.join(ALLOWED_ROLES)}s can use this command.")
        return
    if not os.path.exists(COMMANDS_FILE):
        await ctx.send("No commands file found yet.")
        return

    if flag and flag.strip() == "--key":
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
async def import_commands(ctx, *, json_input: str = None):
    if not any(role.name in ALLOWED_ROLES for role in ctx.author.roles):
        await ctx.send(f"Only {' and '.join(ALLOWED_ROLES)}s can use this command.")
        return

    overwrite = False
    if not any(role.name == OVERLORD_ROLE for role in ctx.author.roles):
        await ctx.send(f"Only the {OVERLORD_ROLE} can use --overwrite.")
        return
    else:
        if json_input and json_input.strip().startswith("--overwrite"):
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


# !cringe
@bot.command(name="cringe")
async def add_to_cringe_list(ctx, *, member: discord.Member):
    if not any(role.name == OVERLORD_ROLE for role in ctx.author.roles):
        if member.id == OVERLORD_ID:
            await ctx.send("My master cannot be cringe.")
            cringe_list.append(ctx.author.id)
            save_cringe_list()
            await ctx.send(f"You are cringe {ctx.author.display_name}.")
            asyncio.create_task(cringe_list_timeout(ctx.author.id, TIMEOUT, ctx.channel))
            await show_cringe_list(ctx)
            return
        else:
            await ctx.send(f"Only {OVERLORD_ROLE} can decide whether someone is cringe or not.")
            return
    if member.id not in cringe_list:
        cringe_list.append(member.id)
        save_cringe_list()
        await ctx.send(f"{member.display_name} is cringe.",
                       allowed_mentions=discord.AllowedMentions(users=False)
        )
        asyncio.create_task(cringe_list_timeout(member.id, TIMEOUT, ctx.channel))
    else:
        await ctx.send(f"{member.display_name} is already in the cringe list.",
                       allowed_mentions=discord.AllowedMentions(users=False)
        )


# !cringe timeout handler
async def cringe_list_timeout(user_id, timeout, channel):
    await asyncio.sleep(timeout)
    if user_id in cringe_list:
        cringe_list.remove(user_id)
        save_cringe_list()
        member = channel.guild.get_member(user_id)
        name = member.display_name if member else f"<@{user_id}>"
        await channel.send(
            f"{name} isn't cringe anymore.", 
            allowed_mentions=discord.AllowedMentions(users=False)
        )


# !uncringe
@bot.command(name="uncringe")
async def remove_from_cringe_list(ctx, *, member: discord.Member):
    if not any(role.name == OVERLORD_ROLE for role in ctx.author.roles):
        await ctx.send(f"Only {OVERLORD_ROLE} can decide whether someone is cringe or not.")
        return
    if member.id in cringe_list:
        cringe_list.remove(member.id)
        save_cringe_list()
        await ctx.send(f"{member.display_name} isn't cringe anymore.",
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


load_dotenv()
ENV = os.getenv("ENV", "production")
if ENV.lower() == "development":
    @bot.event
    async def on_command_error(ctx, error):
        await ctx.send(f"Error: {error}")

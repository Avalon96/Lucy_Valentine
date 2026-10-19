import time
import discord
from discord.ext import tasks

from bot_instance import bot
from commands import has_any_role
from storage import cringe_list, save_cringe_list
from config import ENV, EXPORT_CHANNEL_ID, OVERLORD_ROLE, OVERLORD_ID, TIMEOUT


def add_to_cringe(user_id, channel):
    """Add a user to the cringe list for TIMEOUT seconds. Returns False if they were already in it."""
    if user_id in cringe_list:
        return False
    cringe_list[user_id] = {
        "expires_at": time.time() + TIMEOUT,
        "channel_id": channel.id if channel else None,
    }
    save_cringe_list()
    return True


# !cringe
@bot.command(name="cringe")
async def add_to_cringe_list(ctx, *, member: discord.Member):
    if not has_any_role(ctx.author, OVERLORD_ROLE):
        if member.id == OVERLORD_ID:
            await ctx.send("My master cannot be cringe.")
            add_to_cringe(ctx.author.id, ctx.channel)
            await ctx.send(f"You are cringe {ctx.author.display_name}.")
            await show_cringe_list(ctx)
            return
        else:
            await ctx.send(f"Only {OVERLORD_ROLE} can decide whether someone is cringe or not.")
            return

    if add_to_cringe(member.id, ctx.channel):
        await ctx.send(f"{member.display_name} is cringe.",
                       allowed_mentions=discord.AllowedMentions(users=False)
        )
    else:
        await ctx.send(f"{member.display_name} is already in the cringe list.",
                       allowed_mentions=discord.AllowedMentions(users=False)
        )


# Cringe expiry, stored on disk so it survives restarts
@tasks.loop(seconds=60)
async def expire_cringe():
    now = time.time()
    expired = [user_id for user_id, entry in cringe_list.items() if entry["expires_at"] <= now]
    if not expired:
        return

    entries = {user_id: cringe_list.pop(user_id) for user_id in expired}
    save_cringe_list()

    for user_id, entry in entries.items():
        channel = bot.get_channel(entry["channel_id"]) if entry["channel_id"] else None
        if channel is None:
            continue
        member = channel.guild.get_member(user_id)
        name = member.display_name if member else f"<@{user_id}>"
        try:
            await channel.send(
                f"{name} isn't cringe anymore.",
                allowed_mentions=discord.AllowedMentions(users=False)
            )
        except discord.HTTPException:
            pass


# !uncringe
@bot.command(name="uncringe")
async def remove_from_cringe_list(ctx, *, member: discord.Member):
    if not has_any_role(ctx.author, OVERLORD_ROLE):
        await ctx.send(f"Only {OVERLORD_ROLE} can decide whether someone is cringe or not.")
        return
    if member.id in cringe_list:
        del cringe_list[member.id]
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

# Block Ping

@bot.event
async def on_automod_action(execution: discord.AutoModAction):
    # Fetch the actual channel object using the ID
    export_channel = bot.get_channel(EXPORT_CHANNEL_ID)
    if ENV == "development":
        await export_channel.send("AutoMod action detected.")

    if execution.action.type == discord.AutoModRuleActionType.block_message:
        if ENV == "development":
            await export_channel.send("Message blocked due to ping.")

        author_id = execution.user_id
        channel = execution.channel

        if author_id not in cringe_list:
            if ENV == "development":
                await export_channel.send("Adding user to cringe list.")

            add_to_cringe(author_id, channel)
            member = execution.member

            if channel and member:
                if ENV == "development":
                    await export_channel.send("Sending cringe message to channel.")

                await channel.send(
                    f"{member.display_name} is cringe.",
                    allowed_mentions=discord.AllowedMentions(users=False)
                )

    if ENV == "development":
        await export_channel.send("End of Block Ping rule triggered.")

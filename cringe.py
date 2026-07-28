import discord
import asyncio
import os
from dotenv import load_dotenv

from bot_instance import bot
from storage import cringe_list, save_cringe_list
from config import EXPORT_CHANNEL_ID, OVERLORD_ROLE, OVERLORD_ID, TIMEOUT

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

# Block Ping
load_dotenv()
ENV = os.getenv("ENV", "production")

@bot.event
async def on_automod_action(execution: discord.AutoModAction):
    # Fetch the actual channel object using the ID
    export_channel = bot.get_channel(EXPORT_CHANNEL_ID)
    if ENV.lower() == "development":
        await export_channel.send("AutoMod action detected.")

    if execution.action.type == discord.AutoModRuleActionType.block_message:
        if ENV.lower() == "development":
            await export_channel.send("Message blocked due to ping.")
            
        author_id = execution.user_id

        if author_id not in cringe_list:
            if ENV.lower() == "development":
                await export_channel.send("Adding user to cringe list.")

            cringe_list.append(author_id)
            save_cringe_list()

            channel = execution.channel
            member = execution.member

            if channel and member:
                if ENV.lower() == "development":
                    await export_channel.send("Sending cringe message to channel.")

                await channel.send(
                    f"{member.display_name} is cringe.",
                    allowed_mentions=discord.AllowedMentions(users=False)
                )
                asyncio.create_task(cringe_list_timeout(author_id, TIMEOUT, channel))
                
    if ENV.lower() == "development":
        await export_channel.send("End of Block Ping rule triggered.")

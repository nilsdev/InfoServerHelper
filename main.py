#!/usr/bin/env python3

import discord
from discord.ext import commands
import asyncio
from enum import Enum

token_file = open("token", "r")
TOKEN = token_file.read()
token_file.close()

bot = commands.Bot(command_prefix='+')

allowed = {
    # leon's testserver
    "791355869580361769": [
        "tester",
    ],
    # host hauptserver
    "772795652458938388": [
        "smib",
        "smsb",
        "eti_fachschaft",
        "elektrotechnik",
        "maschinenbau",
        "regenerative_energien",
        "wirtschaftsinfo",
        "motorsport_engineering",
        "campus",
        "games",
        "linux",
        "sund-xplosion",
        "mathe_lernen",
    ]
}

class Status(Enum):
    RUN = 1
    NOT_FOUND = 2
    FORBIDDEN = 3

mod_text = "Schreibe einem der Mods, falls du dies für einen Fehler hälst."

async def dm(to, text):
    await to.create_dm()
    await to.dm_channel.send(text)

async def prepare(ctx):
    # get guild
    opt_guild = ctx.guild
    if opt_guild == None:
        print("no guild")
        return None

    # get allowed roles
    guild_id = str(opt_guild.id)
    allowed_here = allowed.get(guild_id)
    if allowed_here == None:
        print("no allowed roles")
        return None

    return (opt_guild, allowed_here)

@bot.command(name="list")
async def _list(ctx):
    # prepare
    res = await prepare(ctx)
    if res == None:
        await dm(ctx.author, "Ein Fehler ist aufgetreten 🙁")
        return None
    (_, allowed_here) = res

    res = "Erlaubte Rollen:\n```\n"
    for r in allowed_here:
        res += r + '\n'
    res += "```"
    await dm(ctx.author, res)

@bot.command(name='rollen')
async def _role(ctx, mode, role_name):
    # prepare
    res = await prepare(ctx)
    if res == None:
        await dm(ctx.author, "Ein Fehler ist aufgetreten 🙁")
        return
    (guild, allowed_here) = res

    # make role_name lowercase
    role_name = role_name.lower()

    # get role by name (case-insensitive, check allowed list)
    status = Status.NOT_FOUND
    roles = guild.roles
    for r in roles:
        if r.name.lower() != role_name:
            continue
        if role_name in allowed_here:
                role = r
                status = Status.RUN
        else:
            status = Status.FORBIDDEN
        break

    # do the thing
    if status == Status.RUN:
        if mode == 'remove':
            await ctx.author.remove_roles(role)
            print("%s hat %s nicht mehr" % (ctx.author, role))
            await ctx.author.create_dm()
            await ctx.author.dm_channel.send(
                'Du hast nicht mehr die Rolle `%s`\nDu kannst sie mit `+rollen add %s` wieder hinzufügen' % (role, role)
            )
        elif mode == 'add':
            await ctx.author.add_roles(role)
            print("%s hat jetzt %s" % (ctx.author, role))
            await ctx.author.create_dm()
            await ctx.author.dm_channel.send(
                'Du hast jetzt die Rolle `%s`\nDu kannst sie mit `+rollen remove %s` entfernen' % (role, role)
            )
        await ctx.message.add_reaction("✅")
    elif status == Status.NOT_FOUND:
        await ctx.author.create_dm()
        await ctx.author.dm_channel.send(
            f'Die Rolle `%s` gibt es nicht. %s' % (role_name, mod_text)
        )
        await ctx.message.add_reaction("❓")
    elif status == Status.FORBIDDEN:
        await ctx.author.create_dm()
        await ctx.author.dm_channel.send(
            f'Die Rolle `%s` darf nicht vergeben werden. %s' % (role_name, mod_text)
        )
        await ctx.message.add_reaction("❌")

bot.run(TOKEN)

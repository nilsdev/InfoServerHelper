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

async def dm(ctx, text):
    await ctx.author.create_dm()
    await ctx.author.dm_channel.send(text)

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
        await dm(ctx, "Du kannst diesen Befehl nur von einem Server aus nutzen 🙁")
        await ctx.message.add_reaction("❌")
        return None
    (_, allowed_here) = res

    res = "Erlaubte Rollen:\n```\n"
    for r in allowed_here:
        res += r + '\n'
    res += "```"
    await dm(ctx, res)
    await ctx.message.add_reaction("✅")

@bot.command(name='role')
async def _role(ctx, *args):
    # check invocation
    if len(args) < 2:
        await dm(ctx, "Syntax: +role <add|remove> <name>")
        await ctx.message.add_reaction("❌")
        return
    (mode, role_name) = args[0:2]

    if mode not in ["add", "remove"]:
        await dm(ctx, f"Unbekannter Modus `%s`" % mode)
        await ctx.message.add_reaction("❌")
        return

    # prepare
    res = await prepare(ctx)
    if res == None:
        await dm(ctx, "Du kannst diesen Befehl nur von einem Server aus nutzen 🙁")
        await ctx.message.add_reaction("❌")
        return
    (guild, allowed_here) = res

    # make args lowercase
    mode = mode.lower()
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
            await dm(ctx,
                f'Du hast nicht mehr die Rolle `%s`\nDu kannst sie mit `+role add %s` wieder hinzufügen' % (role, role)
            )

        elif mode == 'add':
            await ctx.author.add_roles(role)
            print("%s hat jetzt %s" % (ctx.author, role))
            await dm(ctx,
                f'Du hast jetzt die Rolle `%s`\nDu kannst sie mit `+role remove %s` entfernen' % (role, role)
            )
        await ctx.message.add_reaction("✅")

    elif status == Status.NOT_FOUND:
        print(f"%s hat %s nicht gefunden" % (ctx.author, role_name))
        await dm(ctx,
            f'Die Rolle `%s` gibt es nicht. %s' % (role_name, mod_text)
        )
        await ctx.message.add_reaction("❓")

    elif status == Status.FORBIDDEN:
        if role_name in ["mod", "admin"]:
            await dm(ctx,
                f'Bruh du bekommst doch kein %s' % role_name
            )
        print(f"%s darf %s nicht bekommen" % (ctx.author, role_name))
        await dm(ctx,
            f'die rolle `%s` darf nicht vergeben werden. %s' % (role_name, mod_text)
        )
        await ctx.message.add_reaction("❌")

bot.run(TOKEN)

#!/usr/bin/env python3

import os
import discord
from discord.utils import get
from discord.ext import commands
import asyncio

TOKEN = 'NjU1NDI0MTczMjMzMTQzODA5.XfT5VA.nR3-oRlVbyGjOdmobNWRH6tv81k'
GUILD = '772795652458938388'

bot = commands.Bot(command_prefix='+')

rollen = [
        "smib", 
        "smsb",
        "eti_fachschaft",
        "elektrotechnik", 
        "maschinenbau",
        "regenerative_energien",
        "wirtschaftsinfo",
        "motorsport_engineering"
        "campus",
        "games",
        "linux",
        "sund-xplosion",
        "mathe_lernen"
        ] 

@bot.command(name='rollen')

async def _role(ctx, mode, role: discord.Role):

    mode = mode.lower()
    role = role.lower()
    

    run = 0
    for x in rollen:
        if str(role).lower() in str(x).lower(): 
            run = 1

    if run == 1: 

        if mode == 'remove': 
            await ctx.author.remove_roles(role)
            print("%s hat kein %s mehr" % (ctx.author, role))

            await ctx.author.create_dm()
            await ctx.author.dm_channel.send(
                'Du hast nicht mehr die Rolle `%s` \nDu kannst sie mit `+rollen add %s` wieder hinzufügen' % (role, role)
            )

        if mode == 'add': 
            await ctx.author.add_roles(role)
            print("%s hat jetzt %s" % (ctx.author, role))

            await ctx.author.create_dm()
            await ctx.author.dm_channel.send(
                'Du hast jetzt die Rolle `%s` \nDu kannst sie mit `+rollen remove %s` entfernen' % (role, role)
            )

        run = 0

    else:
        await ctx.author.create_dm()
        if str(role) == 'mod' or str(role) == "admin":
            await ctx.author.dm_channel.send(
                f'Bruh aber guter Versuch haha'
            )
        await ctx.author.dm_channel.send(
            f'Die Rolle `%s` gibt es nicht, oder der Bot kann sie nicht vergeben. Schreibe einem der Mods, falls du dies für einen Fehler hälst.' % role
        )

bot.run(TOKEN)

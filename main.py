#!/usr/bin/env python3

import discord
from discord.ext import commands
import asyncio

token_file = open("token", "r")
TOKEN = token_file.read()

bot = commands.Bot(command_prefix='+')

@bot.command(name='rollen')
async def _role(ctx, mode, role):
    opt_guild = ctx.guild
    if opt_guild == None:
        print("no guild")
        return

    roles = opt_guild.roles
    run = 0
    for r in roles:
        if r.name.lower() == role.lower():
            role = r
            run = 1
            break

    if run == 1:
        if mode == 'remove':
            await ctx.author.remove_roles(role)
            print("%s hat kein %s mehr" % (ctx.author, role))

            await ctx.author.create_dm()
            await ctx.author.dm_channel.send(
                'Du hast nicht mehr die Rolle `%s` \nDu kannst sie mit `+rollen add %s` wieder hinzufügen' % (role, role)
            )
        elif mode == 'add':
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

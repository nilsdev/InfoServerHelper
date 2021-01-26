#!/usr/bin/env python3

from discord.ext import commands

token_file = open("token", "r")
TOKEN = token_file.read()
token_file.close()

class MyBot(commands.Bot):
    pass

async def dm(ctx, text):
    await ctx.author.create_dm()
    await ctx.author.dm_channel.send(text)

bot = MyBot(command_prefix='+')

with open("role_commands.py", "r") as source_file:
    exec(source_file.read())
with open("stat_commands.py", "r") as source_file:
    exec(source_file.read())

bot.run(TOKEN)

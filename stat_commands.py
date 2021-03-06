#!/usr/bin/env python3

import discord
import json
import atexit
from   time    import time, strftime, localtime
from   math    import floor

class VoiceUpdate():
    joined = False
    channel_id = 0
    channel_name = ""
    user_id = 0
    user_name = ""

    def make(member, before, after):
        vu = VoiceUpdate()
        vu.user_id   = str(member.id)
        vu.user_name = member.name
        if before.channel == None and after.channel != None:
            vu.joined       = True
            vu.channel_id   = str(after.channel.id)
            vu.channel_name = after.channel.name
        else:
            vu.joined       = False
            vu.channel_id   = str(before.channel.id)
            vu.channel_name = before.channel.name
        return vu

    def verb(self):
        return "joined" if self.joined else "left"

    def __str__(self):
        return f"{self.user_name} {self.verb()} {self.channel_name}"

# create userdata if not found, else load it
userdata_path = "userdata.json"
try:
    userdata_file = open(userdata_path, "r+")
except FileNotFoundError:
    userdata_file = open(userdata_path, "w+")
    userdata_file.write("{}")
    userdata_file.seek(0)
    print(f"created {userdata_path}")

userdata = json.load(userdata_file)

def save_userdata():
    userdata_file.seek(0)
    json.dump(userdata, userdata_file)
    userdata_file.truncate()

def exit_handler():
    save_userdata()
    userdata_file.close()

atexit.register(exit_handler)

def einf(json, key):
    if key not in json.keys():
        json[key] = {}

def voice_timer_start(vu):
    if "afk" in vu.channel_name:
        print("Wird nicht gezählt wegen AFK")
    else: 
        einf(userdata, vu.user_id)
        userdata[vu.user_id]["started"] = floor(time())

def voice_timer_stop(vu):
    einf(userdata, vu.user_id)
    if "started" not in userdata[vu.user_id].keys():
        return
    started      = userdata[vu.user_id].pop("started")
    diff         = floor(time()) - started
    channel_val  = userdata[vu.user_id].setdefault(vu.channel_id, 0)
    channel_val += diff
    userdata[vu.user_id][vu.channel_id] = channel_val

ranks = {
    "18000": ":brown_circle: Bronze IV",
    "54000": ":brown_circle: Bronze III",
    "90000": ":brown_circle: Bronze II",
    "144000": ":brown_circle: Bronze I",
    "198000": ":white_circle: Silber IV",
    "252000": ":white_circle: Silber III",
    "306000": ":white_circle: Silber II",
    "432000": ":yellow_circle: Gold IV",
    "504000": ":yellow_circle: Gold III",
    "576000": ":yellow_circle: Gold II",
    "900000": ":small_blue_diamond: klein-Diamant IV",
    "1080000": ":small_blue_diamond: klein-Diamant III",
    "1260000": ":small_blue_diamond: klein-Diamant II",
    "1440000": ":small_blue_diamond: klein-Diamant I",
    "1620000": ":large_blue_diamond: Diamant IV",
    "1800000": ":large_blue_diamond: Diamant III",
    "1980000": ":large_blue_diamond: Diamant II",
    "2160000": ":large_blue_diamond: Diamant I",
    "2520000": ":black_square_button: klein-Titan IV",
    "2880000": ":black_square_button: klein-Titan III",
    "3240000": ":black_square_button: klein-Titan II",
    "3600000": ":black_square_button: klein-Titan I",
    "4140000": ":white_square_button: Titan IV",
    "5220000": ":white_square_button: Titan III",
    "6300000": ":white_square_button: Titan II",
    "7200000": ":white_square_button: Titan I",
}

def find_rank(time):
    for k in ranks.keys():
        if int(k) >= time:
            return ranks[k]
    return ":diamonds: Meister"

# TODO this sometimes doesn't work
async def get_nick(uid, guild):
    user = await guild.fetch_member(uid)
    name = user.nick
    if name == None:
        user = await bot.fetch_user(uid)
        name = user.name
    return name

def tally(data):
    total = 0
    for s in data:
        if s == "started":
            total += floor(time()) - data[s]
        else:
            total += data[s]
    return total

def format_seconds(sec):
    (hours, sec) = divmod(sec, 3600)
    (mins , sec) = divmod(sec,   60)
    return f"{hours} Stunden, {mins} Minuten, {sec} Sekunden"

@bot.command(name="top")
async def _top(ctx, *args):
    # check invocation
    if len(args) < 1:
        await dm(ctx, "Syntax: `+top <anzahl>`")
        await ctx.message.delete()
        return

    # indicate working
    await ctx.channel.trigger_typing()

    embed = await make_top_embed(ctx.guild, int(args[0]))
    await ctx.channel.send(embed=embed)

async def make_top_embed(guild, topn):
    data = []
    for u in userdata:
        total = tally(userdata[u])
        data.append((u, total))

    # sort descending by total time
    data  = sorted(data, key=lambda x: x[1], reverse=True)
    data  = data[0 : topn] if topn > 0 else data
    pfx   = f"Top {topn}"  if topn > 0 else "All"
    embed = discord.Embed(title=f"{pfx} Voice Users", url="https://http.cat/509")
    ctr = 0

    # build embed fields
    for d in data:
        ctr   += 1
        name = await get_nick(int(d[0]), guild)
        rank  = find_rank(d[1])
        indic = ":green_circle:" if "started" in userdata[d[0]].keys() else ""
        name  = f"{ctr}. {name}"
        value = f"{indic} {find_rank(d[1])}\n{format_seconds(d[1])}"
        embed.add_field(name=name, value=value, inline=False)

    return embed

async def refresh_master_message():
    if bot.master_channel == None:
        bot.master_channel = await bot.fetch_channel(803555338389291029)
        print("got master channel")

    # indicate working
    await bot.master_channel.trigger_typing()

    embed    = await make_top_embed(bot.master_channel.guild, bot.master_topn)
    content  = strftime("%Y-%m-%d %H:%M:%S", localtime())
    if bot.master_message == None:
        bot.master_message = await bot.master_channel.send(content, embed=embed)
        print("send master message")
    else:
        try:
            await bot.master_message.edit(content=content, embed=embed)
            print("edit master message")
        except Exception as e:
            print(e)
            bot.master_message = None
            await refresh_master_message()

def safe_int(text, default):
    try:
        default = int(text)
    except Exception:
        pass
    return default

@bot.command(name="settopn")
async def _settopn(ctx, *args):
    # check invocation
    if len(args) < 1:
        await dm(ctx, "Syntax: `+top <anzahl>`")
        await ctx.message.delete()
        return

    bot.master_topn = safe_int(args[0], bot.master_topn)
    await refresh_master_message()
    await ctx.message.delete()

async def on_voice_state_update(self, member, before, after):
    vu = VoiceUpdate.make(member, before, after)
    if vu.joined:
        voice_timer_start(vu)
    else:
        voice_timer_stop(vu)
        if before.channel != None and after.channel != None:
            # a user has switched to a different channel
            voice_timer_start(vu)

    print(f"{str(floor(time()))}: {vu}")
    save_userdata()
    await refresh_master_message()

# inject the method
MyBot.on_voice_state_update = on_voice_state_update

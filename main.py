import discord
import json
import emojis
import string
import typing
import random
import wordle
import os
import gen
import wgame
from PIL import Image as PILI, ImageDraw, ImageFont
from discord.ext import commands, tasks
from discord import app_commands
import private

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(
    command_prefix=("!"), intents=intents,
    allowed_installs=app_commands.AppInstallationType(guild=True, user=True),
    allowed_contexts=app_commands.AppCommandContext(guild=True, private_channel=True, dm_channel=True))

with open("streaks.json") as streaksfile:
    streaks = json.load(streaksfile)
with open('words.json') as wordsfile:
    words = json.load(wordsfile)

@bot.event
async def on_ready():
    print("syncing commands...")
    await bot.tree.sync()
    print(f'Logged in as {bot.user.name}\n')
    # await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Heat Abwaanormal"), status=discord.Status.online)
    await bot.change_presence(activity=discord.CustomActivity(name="DAY 100"), status=discord.Status.online)
    # await bot.change_presence(status=discord.Status.invisible)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("`Command doesn't exist.`")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send('`You do not have the required permissions to run this command.`')

@bot.event
async def on_message(message):
    await private.log(bot, message)
    await private.chop(bot, message)


    # if message.author.id != 1170381506460536905: return

    if message.content.startswith('!^ ') and message.author.id == 1170381506460536905:
        await message.delete()
        
        if " -ds " in message.content:
            split = message.content.split(" -ds ")
            user = await bot.fetch_user(int(split[1]))
            await user.send(split[0].replace('!^ ', ''))
        elif message.reference: 
            reply_to = await message.channel.fetch_message(message.reference.message_id)
            if message.content.endswith(' -d'): await reply_to.author.send(message.content.replace('!^ ', '').replace(' -d', ''))
            else: await reply_to.reply(message.content.replace('!^ ', ''))
        else: await message.channel.send(message.content.replace('!^ ', ''))
        return

    global words, streaks
    if message.author.bot or message.guild is not None:
        if not message.author.bot: await bot.process_commands(message)
        return
    if not message.author.bot and message.content.startswith("!"):
        await bot.process_commands(message)
        return
    content = message.content.lower()
    day = words[2]
    word = str(words[1][0 if day == 13 else (day-1)%len(words[1])])
    letters = len(word)
    gametext = f"# {'OSAGE WORDLE' if message.author.id != 699418679963811870 else 'OSAGE WORLDE'} #{day}\n{''.join(emojis.letters[0][:10])}\n{''.join(emojis.letters[0][10:20])}\n{''.join(emojis.letters[0][20:])}\n{'-'*15}\n{emojis.blank*letters}"

    if content == "start":
        output = await wgame.start(message.author, words, streaks)
        if output != False:
            streaks = output
            with open("streaks.json", "w") as streaksfile: json.dump(streaks, streaksfile, indent=4)
            return

    if streaks[str(message.author.id)]["playing"] != -1:
        output = await wgame.guess(message, words, streaks)
        if output != False:
            streaks = output

    with open("streaks.json", "w") as streaksfile:
        json.dump(streaks, streaksfile, indent=4)

    await bot.process_commands(message)

@bot.hybrid_command(brief="Start a game of osage wordle")
async def start(ctx):
    global streaks
    output = await wgame.start(ctx.author, words, streaks)
    if output == False:
        await ctx.reply("You have already started a game today.", ephemeral=True)
    else:
        streaks = output
        with open("streaks.json", "w") as streaksfile: json.dump(streaks, streaksfile, indent=4)
        await ctx.reply("A game has started, check your dms.", ephemeral=True)

@bot.group()
@commands.is_owner()
async def admin(ctx):
    return

@admin.command()
async def reset(ctx):
    async with ctx.typing():
        global words, streaks
        words[2] += 1
        words[5] = []
        if (words[2]-1)%len(words[1]) == 0: random.shuffle(words[1])
        for user in streaks.keys():
            if streaks[user]["playing"] != -1: streaks[user]["streak"] = 0
            streaks[user]["playing"] = 0
            if user == 1155305615757946991:
                streaks.pop(str(user.id))
        
        with open("words.json", "w") as wordsfile:
            json.dump(words, wordsfile, indent=4)
        with open("streaks.json", "w") as streaksfile:
            json.dump(streaks, streaksfile, indent=4)
        
        await ctx.reply("daily word has been reset")

@admin.command()
async def shuffle(ctx):
    global words
    random.shuffle(words[1])
    with open("words.json", "w") as wordsfile:
        json.dump(words, wordsfile, indent=4)

@admin.command()
async def rmstreak(ctx, user: discord.user = None):
    global streaks
    if user == None:
        for userid in streaks.keys(): streaks[userid]["streak"] = 0
    else:
        streaks[str(user.id)]["streak"] = 0
    with open("streaks.json", "w") as streaksfile:
        json.dump(streaks, streaksfile, indent=4)

@admin.command()
async def append(ctx, word, sauce = ""):
    global words
    words[1].append(word)
    words[4][word] = sauce
    await ctx.reply("added.")
    with open("words.json", "w") as wordsfile:
        json.dump(words, wordsfile, indent=4)

@bot.hybrid_command(brief="get osage wordle streak")
async def getstreak(ctx, user: discord.User = None):
    async with ctx.typing():
        if user == None: user = ctx.author
        if str(user.id) not in streaks.keys():
            await ctx.reply("user has never played osage wordle.")
            return
        await ctx.reply(f"{user.name} has an osage wordle streak of {streaks[str(user.id)]['streak']} days.")

def streakvalue(user, day):
    if str(day) in user.keys():
        if user[str(day)][2] == []:
            return 8
        elif user[str(day)][2][len(user[str(day)][2])-1] == list("11111"):
            return len(user[str(day)][2])
        else:
            return 8 - 0.1*len(user[str(day)][2])
    return 8

@bot.hybrid_command(aliases=["lb"], brief="get osage wordle leaderboard")
async def leaderboard(ctx, day: typing.Optional[int] = None, theme: typing.Literal["dark", "light", "osagle", "bwaa", "inaba"] = "dark"):
    async with ctx.typing():
        if day == None: day = words[2]
        if day < 1: day = 1
        lb = dict(sorted(streaks.items(), key=lambda item: streakvalue(item[1], day)))
        user_ids = list(lb.keys())
        users = []
        for i in range(len(user_ids)):
            user = await bot.fetch_user(int(user_ids[i]))
            users.append(user.name)
            if user.display_name != user.name:
                users[i] += f" ({user.display_name})"
        
        message = f"**OSAGE WORDLE LEADERBOARD #{day}**"
        for i in range(len(users[:3])):
            value = str(streakvalue(streaks[user_ids[i]], day))
            if value != "8":
                message += f"\n\n{i+1}. **{users[i]}** - {value if float(value) < 7 else 'X'}/6"
                game = gen.gentext(streaks[str(user_ids[i])][str(day)][2], gen.textthemes[theme])
                game = game.split("\n")
                for guess in game: message += f"\n> {guess}"
        for i in range(len(users[3:20])):
            value = str(streakvalue(streaks[user_ids[i+3]], day))
            if value != "8": message += f"\n{i+4}. **{users[i+3]}** - {value if float(value) < 7 else 'X'}/6"
        
        await ctx.reply(message)

@bot.tree.command(name="bwaa")
async def bwaa(interaction: discord.Interaction):
    await interaction.response.send_message("bwaa")

@bot.hybrid_command(name="get", aliases=["g"], brief="generate text representation of a game")
async def get(ctx, user: typing.Optional[discord.User] = None, day: typing.Optional[int] = None, username: typing.Optional[bool] = True,
              theme: typing.Literal["dark", "light", "osagle", "bwaa", "inaba"] = "dark"):
    async with ctx.typing():
        if day == None: day = words[2]
        if user == None: user = ctx.author
        if day < 1: day = 1
        if str(user.id) not in streaks.keys(): await ctx.reply("user has never played osage wordle."); return
        elif str(day) not in streaks[str(user.id)].keys(): await ctx.reply("user has not played that day."); return
        elif len(streaks[str(user.id)][str(day)]) < 3: await ctx.reply("not available."); return
        elif len(streaks[str(user.id)][str(day)][2]) == 0: await ctx.reply("user has started game."); return
        await ctx.reply(f"{'OSAGE WORDLE' if user.id != 699418679963811870 else 'OSAGE WORLDE'} #{day}{f' FOR {user.name.upper()}' if username else ''}\n{gen.gentext(streaks[str(user.id)][str(day)][2], gen.textthemes[theme])}")

@bot.hybrid_command(aliases=["getimg", "gi"], brief="generate image representation of a game")
async def getimage(ctx, user: typing.Optional[discord.User] = None, day: typing.Optional[int] = None,
                   theme: typing.Literal["dark", "light", "gradient"] = "gradient",
                   gametheme: typing.Literal["osagle", "bwaa", "inaba"] = "osagle"):
    async with ctx.typing():
        if day == None: day = words[2]
        if user == None: user = ctx.author
        if day < 1: day = 1
        if str(user.id) not in streaks.keys(): await ctx.reply("user has never played osage wordle."); return
        elif str(day) not in streaks[str(user.id)].keys(): await ctx.reply("user has not played that day."); return
        elif len(streaks[str(user.id)][str(day)]) < 3: await ctx.reply("not available."); return
        elif len(streaks[str(user.id)][str(day)][2]) == 0: await ctx.reply("user has started game."); return
        
        image = await gen.genimg(streaks[str(user.id)][str(day)][2], user, day, gen.imagethemes[theme], gen.gamethemes[gametheme])
        image.save(f"exports\{ctx.message.id}.png")
        await ctx.reply(file=discord.File(f"exports\{ctx.message.id}.png"))
        os.remove(f"exports\{ctx.message.id}.png")


bot.run(private.token)
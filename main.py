import discord
import json
import emojis
import string
import typing
import random
import wordle
import os
import gen
from PIL import Image as PILI, ImageDraw, ImageFont
from discord.ext import commands, tasks
from private import token

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=("!"), intents=intents)

with open("streaks.json") as streaksfile:
    streaks = json.load(streaksfile)
with open('words.json') as wordsfile:
    words = json.load(wordsfile)

@bot.event
async def on_ready():
    print("syncing commands...")
    await bot.tree.sync()
    print(f'Logged in as {bot.user.name}\n')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="INABAKUMORI | Hadal Abyss Zone"), status=discord.Status.online)
    # await bot.change_presence(status=discord.Status.invisible)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("`Command doesn't exist.`")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send('`You do not have the required permissions to run this command.`')

@bot.event
async def on_message(message):
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
    
    if str(message.author.id) in streaks.keys():
        if streaks[str(message.author.id)]["playing"] == 0:
            if content != "start":
                await message.channel.send("send `start` to start a game.")
                return
            
            """if len(words[3]) != 0:
                for bug in words[3]:
                    await message.author.send(f"a bug has been reported:\n> {name}\nfix:\n> {fix}\n{'you will still be able to play today.' if pause == 0 else 'you cannot play until this bug is fixed.'}")
            """

            game = await message.channel.send(gametext)
            streaks[str(message.author.id)]["playing"] = 1
            streaks[str(message.author.id)][str(day)] = [[0]*26, game.id, []]
        elif streaks[str(message.author.id)]["playing"] != -1:
            if len(content) != 5 or not content.isalpha():
                await message.channel.send("guesses must be 5 letters.")
                return
            wordlegame = wordle.Wordle(word = 'bwaaa', real_words = True)
            wordleresponse = wordlegame.send_guess(content)

            if content not in words[1] and content not in words[0] and wordleresponse == "That's not a real word.":
                await message.add_reaction("❌")
                return
            
            
            game = await message.channel.fetch_message(streaks[str(message.author.id)][str(day)][1])
            
            guess = ""
            guessval = ""
            word = list(word)
            for i in range(5):
                letter = content[i]
                if streaks[str(message.author.id)][str(day)][0][string.ascii_lowercase.index(letter)] == 0: streaks[str(message.author.id)][str(day)][0][string.ascii_lowercase.index(letter)] = 3
                if letter == word[i]:
                    value = 1
                    word[i] = "1"
                    streaks[str(message.author.id)][str(day)][0][string.ascii_lowercase.index(letter)] = 1
                elif letter in word:
                    value = 3
                    j = 0
                    streaks[str(message.author.id)][str(day)][0][string.ascii_lowercase.index(letter)] = 1
                    while j < 5:
                        if letter == word[j] and content[j] != word[j]:
                            word[j] = "1"
                            value = 2
                            j = 5
                        else:
                            j += 1 
                else: value = 3
                guess += emojis.letters[value][string.ascii_lowercase.index(letter)]
                guessval += str(value)
            word = "".join(word)
            streaks[str(message.author.id)][str(day)][2].append(list(guessval))
            msg = ""
            for letter in list(guessval):
                if letter == "1": msg += "🟩"
                elif letter == "2": msg += "🟨"
                elif letter == "3": msg += "⬛"
            print(f"\n{message.author.name} just guessed: {msg}")

            keyboard = [""]*3
            for i in range(10): keyboard[0] += emojis.letters[int(streaks[str(message.author.id)][str(day)][0][i])][i]
            for i in range(10): keyboard[1] += emojis.letters[int(streaks[str(message.author.id)][str(day)][0][i+10])][i+10]
            for i in range(6): keyboard[2] += emojis.letters[int(streaks[str(message.author.id)][str(day)][0][i+20])][i+20]
            keyboard = "\n".join(keyboard)
            gametext = f"# {'OSAGE WORDLE' if message.author.id != 699418679963811870 else 'OSAGE WORLDE'} #{day}\n{keyboard}\n{'-'*15}\n"
            prev_guesses = game.content.split("\n")[5:]
            if emojis.blank not in prev_guesses[0]: gametext += ("\n".join(prev_guesses) + "\n")
            else: prev_guesses = []
            gametext += guess
            await game.edit(content=gametext)

            if guessval == "11111" or streaks[str(message.author.id)]["playing"] == 6:
                game = await message.channel.fetch_message(streaks[str(message.author.id)][str(day)][1])

                saucestring = words[4][words[1][(day-1)%len(words[1])]]
                if saucestring.startswith("https") or saucestring == "": sauce = saucestring
                else: sauce = f"https://www.youtube.com/watch?v={saucestring}"
                
                gametext = game.content + f"\n\nThe word was `{words[1][0 if day == 13 else (day-1)%len(words[1])]}`" + f"\n{sauce}"
                await game.edit(content=gametext)

                image = await gen.genimg(streaks[str(message.author.id)][str(day)][2], message.author, day, [r"images\backgrounds\gradient.png", "#0000008C", "#FFFFFFFF"], ["emojis/green/green.png", "emojis/yellow/yellow.png", "emojis/grey/greyfull.png"])
                image.save(f"exports\{message.id}.png")
                await message.channel.send(file=discord.File(f"exports\{message.id}.png"))
                await message.channel.send("-# run `!get` to view this as text")
                os.remove(f"exports\{message.id}.png")

                print(f"\n{message.author.name} finished their game:\n{gen.gentext(streaks[str(message.author.id)][str(day)][2], ['🟩', '🟨', '⬛'])}")
                streaks[str(message.author.id)]["playing"] = -1
                streaks[str(message.author.id)]["streak"] += 1
            else:
                streaks[str(message.author.id)]["playing"] += 1
        else:
            await message.channel.send("you have already played today.")
    else:
        if content != "start":
            await message.channel.send("send `start` to start a game.")
            return
        
        game = await message.channel.send(gametext)
        streaks[str(message.author.id)] = {"options": [0], "streak": 0, "playing" : 1, str(day) : [[0]*26, game.id, []]}
    
    with open("streaks.json", "w") as streaksfile:
        json.dump(streaks, streaksfile, indent=4)

    await bot.process_commands(message)

@bot.group()
@commands.is_owner()
async def admin(ctx):
    return

@admin.command()
async def reset(ctx):
    async with ctx.typing():
        global words, streaks
        words[2] += 1
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

@bot.command(hidden=True)
async def getdaily(ctx):
    await ctx.reply("the getdaily command has been replaced with get and getimage.\n\nuse `!get`, `!g` or `/get` for text-based themes\nuse `!getimage`, `!getimg`, `!gi` or `/get` for image-based themes\n\nif the new commands arent working or you dont understand, dm minty")

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
async def leaderboard(ctx, day: typing.Optional[int] = words[2], theme: typing.Literal["dark", "light", "osagle", "bwaa"] = "dark"):
    async with ctx.typing():
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
                for guess in streaks[str(user_ids[i])][str(day)][2]:
                    message += "\n> "
                    for letter in guess:
                        letter = int(letter)
                        themes = {
                            "dark": ["🟩", "🟨", "⬛"],
                            "light": ["🟩", "🟨", "⬜"],
                            "osagle": ["<:green:1401642959782416414>", "<:yellow:1401643202817294388>", "<:grey:1401644438819831828>"],
                            "bwaa": ["<:greenbwaa:1401808521430958120>", "<:yellowbwaa:1401808549679599758>", "<:greybwaa:1401808487830257785>"]
                        }
                        if letter == 1: message += themes[theme][0]
                        elif letter == 2: message += themes[theme][1]
                        elif letter == 3: message += themes[theme][2]
        message += "\n"
        for i in range(len(users[3:20])):
            value = str(streakvalue(streaks[user_ids[i+3]], day))
            if value != "8": message += f"\n{i+4}. **{users[i+3]}** - {value if float(value) < 7 else 'X'}/6"
        
        await ctx.reply(message)

@bot.hybrid_command(aliases=["g"], brief="generate text representation of a game")
async def get(ctx, user: typing.Optional[discord.User] = None, day: typing.Optional[int] = words[2], username: typing.Optional[bool] = True,
              theme: typing.Literal["dark", "light", "osagle", "bwaa", "inaba"] = "dark"):
    async with ctx.typing():
        themes = {
            "dark": ["🟩", "🟨", "⬛"],
            "light": ["🟩", "🟨", "⬜"],
            "osagle": ["<:green:1401642959782416414>", "<:yellow:1401643202817294388>", "<:grey:1401644438819831828>"],
            "bwaa": ["<:greenbwaa:1401808521430958120>", "<:yellowbwaa:1401808549679599758>", "<:greybwaa:1401808487830257785>"],
            "inaba": ["<:greeninaba:1407789263340179476>", "<:yellowinaba:1407789238098984980>", "<:greyinaba:1407789205299396921>"]
        }
        if user == None: user = ctx.author
        if day < 1: day = 1
        if str(user.id) not in streaks.keys(): await ctx.reply("user has never played osage wordle."); return
        elif str(day) not in streaks[str(user.id)].keys(): await ctx.reply("user has not played that day."); return
        elif len(streaks[str(user.id)][str(day)]) < 3: await ctx.reply("not available."); return
        elif len(streaks[str(user.id)][str(day)][2]) == 0: await ctx.reply("user has started game."); return
        await ctx.reply(f"{'OSAGE WORDLE' if user.id != 699418679963811870 else 'OSAGE WORLDE'} #{day}{f' FOR {user.name.upper()}' if username else ''}\n{gen.gentext(streaks[str(user.id)][str(day)][2], themes[theme])}")

@bot.hybrid_command(aliases=["getimg", "gi"], brief="generate image representation of a game")
async def getimage(ctx, user: typing.Optional[discord.User] = None, day: typing.Optional[int] = words[2],
                   theme: typing.Literal["dark", "light", "gradient"] = "gradient",
                   guesstheme: typing.Literal["osagle", "bwaa", "inaba"] = "osagle"):
    async with ctx.typing():
        themes = {
            "dark": [r"images\backgrounds\dark.png", "#FFFFFFDC", "#000000FF"],
            "light": [r"images\backgrounds\light.png", "#0000008C", "#FFFFFFFF"],
            "gradient": [r"images\backgrounds\gradient.png", "#0000008C", "#FFFFFFFF"]
        }
        guessthemes = {
            "osagle": ["emojis/green/green.png", "emojis/yellow/yellow.png", "emojis/grey/greyfull.png"],
            "bwaa": ["emojis/green/greenbwaa.png", "emojis/yellow/yellowbwaa.png", "emojis/grey/greybwaa.png"],
            "inaba": ["emojis/green/greeninaba.png", "emojis/yellow/yellowinaba.png", "emojis/grey/greyinaba.png"]
        }
        if user == None: user = ctx.author
        if day < 1: day = 1
        if str(user.id) not in streaks.keys(): await ctx.reply("user has never played osage wordle."); return
        elif str(day) not in streaks[str(user.id)].keys(): await ctx.reply("user has not played that day."); return
        elif len(streaks[str(user.id)][str(day)]) < 3: await ctx.reply("not available."); return
        elif len(streaks[str(user.id)][str(day)][2]) == 0: await ctx.reply("user has started game."); return
        
        image = await gen.genimg(streaks[str(user.id)][str(day)][2], user, day, themes[theme], guessthemes[guesstheme])
        image.save(f"exports\{ctx.message.id}.png")
        await ctx.reply(file=discord.File(f"exports\{ctx.message.id}.png"))
        os.remove(f"exports\{ctx.message.id}.png")


bot.run(token)
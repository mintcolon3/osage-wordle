import discord
import json
import emojis
import string
import typing
import random
import wordle
import datetime
import os
from PIL import Image as PILI, ImageDraw, ImageFont
from discord import app_commands
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
    gametext = f"# OSAGE WORDLE #{day}\n{''.join(emojis.letters[0][:10])}\n{''.join(emojis.letters[0][10:20])}\n{''.join(emojis.letters[0][20:])}\n{'-'*15}\n{emojis.blank*letters}"
    
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
            gametext = f"# OSAGE WORDLE #{day}\n{keyboard}\n{'-'*15}\n"
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

                prev_guesses.append(guess)
                result = [""]*streaks[str(message.author.id)]["playing"]
                for i in range(len(prev_guesses)):
                    for l in prev_guesses[i].split("><:"):
                        if "green" in l: result[i] += "🟩"
                        elif "yellow" in l: result[i] += "🟨"
                        elif "red" in l: result[i] += "⬛"
                result = "\n".join(result)
                await message.channel.send(f"OSAGE WORDLE #{day}\n{result}")
                print(f"\n{message.author.name} finished their game:\n{result}")
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

reminder_time = datetime.time(hour=17, minute=00, tzinfo=datetime.timezone.utc)
@tasks.loop(time=reminder_time)
async def reminder_msg():
    for user in streaks.keys():
        if streaks[user]["streak"] >= 3 and streaks[user]["playing"] == 0 and streaks[user]["options"][0] == 0:
            user_obj = await bot.fetch_user(int(user))
            await user_obj.send(f"last chance to keep your streak of {streaks[user]['streak']} days\n-# send `!reminder` to toggle this reminder")

@bot.command()
async def reminder(ctx):
    streaks[str(ctx.author.id)]["streak"] += 1
    streaks[str(ctx.author.id)]["streak"] %= 2
    await ctx.reply("done")
    with open("streaks.json", "w") as streaksfile:
        json.dump(streaks, streaksfile, indent=4)

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

@bot.hybrid_command(brief="get osage wordle diagram")
async def getdaily(ctx, user: typing.Optional[discord.User] = None, day: typing.Optional[int] = words[2], theme: typing.Literal["dark", "light", "osagle", "bwaa", "image"] = "dark", imagetheme: typing.Literal["white", "black"] = "white"):
    async with ctx.typing():
        if user == None: user = ctx.author
        if day < 1: day = 1
        if str(user.id) not in streaks.keys():
            await ctx.reply("user has never played osage wordle.")
            return
        elif str(day) not in streaks[str(user.id)].keys():
            await ctx.reply("user has not played that day.")
            return
        elif len(streaks[str(user.id)][str(day)]) < 3:
            await ctx.reply("not available.")
            return
        elif len(streaks[str(user.id)][str(day)][2]) == 0:
            await ctx.reply("user has started game.")
            return
        
        if theme == "image":
            imagep = []
            for guess in streaks[str(user.id)][str(day)][2]:
                for letter in guess:
                    letter = int(letter)
                    if letter == 1: imagep.append("emojis/green/green.png")
                    elif letter == 2: imagep.append("emojis/yellow/yellow.png")
                    elif letter == 3: imagep.append("emojis/grey/greyfull.png")

            image = PILI.new('RGB', (32*5 + 16, 32*(len(imagep)//5) + 64), color=("white" if imagetheme == "white" else "black"))
            images = [PILI.open(path).resize((32, 32)) for path in imagep]
            for i, img in enumerate(images): image.paste(img, (i%5*32 + 8, i//5*32 + 56))

            draw = ImageDraw.Draw(image)
            draw.text((5,0), f"#{day}", font=ImageFont.truetype("sdv.ttf", 48), fill=("black" if imagetheme == "white" else "white"))
            draw.text((5*32+8,56), user.name.upper(), font=ImageFont.truetype("sdv.ttf", 20), fill=("black" if imagetheme == "white" else "white"), anchor="rd")

            image.save(f"exports\{ctx.message.id}.png")
            await ctx.reply(file=discord.File(f"exports\{ctx.message.id}.png"))
            os.remove(f"exports\{ctx.message.id}.png")
        else:
            message = f"**OSAGE WORDLE #{day} FOR {user.name.upper()}**"
            for guess in streaks[str(user.id)][str(day)][2]:
                message += "\n"
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
        
            await ctx.reply(message)

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

@bot.group()
@commands.is_owner()
async def bug(ctx):
    return

@bug.command()
async def report(ctx, pause: int, name, fix = "none specified"):
    words[3].append([name, fix, pause])
    await ctx.reply("bug reported.")

    for i in range(len(streaks)):
        if streaks[str(i)]["playing"] != 0:
            user = await bot.fetch_user(int(streaks.keys()[i]))
            await user.send(f"a bug has been reported:\n> {name}\nfix:\n> {fix}\n{'you will still be able to play today.' if pause == 0 else 'you cannot play until this bug is fixed.'}")

    with open("words.json", "w") as wordsfile:
        json.dump(words, wordsfile, indent=4)

@bug.command()
@commands.is_owner()
async def display(ctx):
    bugs = ""
    for i in range(len(words[3])): bugs += f'\n{i}:\n> name="{words[3][i][0]}"\n> fix="{words[3][i][1]}"\n> paused={words[3][i][2]}'
    await ctx.reply(bugs)

@bug.command()
@commands.is_owner()
async def remove(ctx, index: int = -1):
    if index == -1: words[3] = []
    else: words[3].pop(index)
    await ctx.reply(f"bug #{index} removed.")
    with open("words.json", "w") as wordsfile:
        json.dump(words, wordsfile, indent=4)

bot.run(token)
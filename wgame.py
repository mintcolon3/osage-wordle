import discord
import wordle
import string
import os

import emojis
import gen

async def start(user: discord.abc.User, words: dict, streaks: dict):
    day = words[2]
    length = len(str(words[1][(day-1)%len(words[1])]))
    gametitle = "OSAGE WORDLE" if user.id != 699418679963811870 else "OSAGE WORLDE"
    gametext = f"# {gametitle} #{day}\n{''.join(emojis.letters[0][:10])}\n{''.join(emojis.letters[0][10:20])}\n{''.join(emojis.letters[0][20:])}\n{'-'*15}\n{emojis.blank*length}"

    if str(user.id) not in streaks:
        game = await user.send(gametext)
        streaks[str(user.id)] = {"options": [0], "streak": 0, "playing" : 1, str(day) : [[0]*26, game.id, []]}
    elif streaks[str(user.id)]["playing"] == 0:
        game = await user.send(gametext)
        streaks[str(user.id)]["playing"] = 1
        streaks[str(user.id)][str(day)] = [[0]*26, game.id, []]
    else:
        return False

    return streaks

async def guess(message: discord.Message, words: dict, streaks: dict):
    content = message.content.lower()
    day = words[2]
    word = str(words[1][(day-1)%len(words[1])])

    if len(content) != 5 or not content.isalpha():
        await message.channel.send("guesses must be 5 letters.")
        return False
    wordlegame = wordle.Wordle(word = 'bwaaa', real_words = True)
    wordleresponse = wordlegame.send_guess(content)

    if content not in words[1] and content not in words[0] and wordleresponse == "That's not a real word.":
        await message.add_reaction("❌")
        return False
    
    
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
    print(f"\n{message.author.name} just guessed: {gen.gentext([list(guessval)], gen.textthemes['dark'])}")

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

        image = await gen.genimg(streaks[str(message.author.id)][str(day)][2], message.author, day, gen.imagethemes["gradient"], gen.gamethemes["osagle"])
        image.save(f"exports\{message.id}.png")
        await message.channel.send(file=discord.File(f"exports\{message.id}.png"))
        await message.channel.send("-# run `!get` to view this as text")
        os.remove(f"exports\{message.id}.png")

        print(f"\n{message.author.name} finished their game:\n{gen.gentext(streaks[str(message.author.id)][str(day)][2], gen.textthemes['dark'])}")
        streaks[str(message.author.id)]["playing"] = -1
        streaks[str(message.author.id)]["streak"] += 1
    else:
        streaks[str(message.author.id)]["playing"] += 1
    
    return streaks
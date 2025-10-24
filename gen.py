from PIL import Image as PILI, ImageDraw, ImageFont
import discord
import os

textthemes = {
    "dark": ["🟩", "🟨", "⬛"],
    "light": ["🟩", "🟨", "⬜"],
    "osagle": ["<:green:1401642959782416414>", "<:yellow:1401643202817294388>", "<:grey:1401644438819831828>"],
    "bwaa": ["<:greenbwaa:1401808521430958120>", "<:yellowbwaa:1401808549679599758>", "<:greybwaa:1401808487830257785>"],
    "inaba": ["<:greeninaba:1407789263340179476>", "<:yellowinaba:1407789238098984980>", "<:greyinaba:1407789205299396921>"]
}
imagethemes = {
    "dark": [r"images\backgrounds\dark.png", "#FFFFFFDC", "#000000FF"],
    "light": [r"images\backgrounds\light.png", "#0000008C", "#FFFFFFFF"],
    "gradient": [r"images\backgrounds\gradient.png", "#0000008C", "#FFFFFFFF"]
}
gamethemes = {
    "osagle": ["emojis/green/green.png", "emojis/yellow/yellow.png", "emojis/grey/greyfull.png"],
    "bwaa": ["emojis/green/greenbwaa.png", "emojis/yellow/yellowbwaa.png", "emojis/grey/greybwaa.png"],
    "inaba": ["emojis/green/greeninaba.png", "emojis/yellow/yellowinaba.png", "emojis/grey/greyinaba.png"]
}

def gentext(game, theme):
    output = [""]*len(game)
    for i, guess in enumerate(game):
        for letter in guess: output[i] += theme[int(letter)-1]
    return "\n".join(output)

async def genimg(game, user: discord.User, day, imagetheme, guesstheme):
    username = user.name.upper()
    if len(username) > 15: username = f"{username[:15]}..."

    bg = PILI.open(imagetheme[0]).convert("RGBA").resize((32*5 + 16, 32*len(game) + 64))

    l1 = PILI.new("RGBA", bg.size, "#00000000")
    draw = ImageDraw.Draw(l1, "RGBA")
    draw.polygon([(7, 55), (32*5+8, 55), (32*5+8, 32*len(game)+56), (7, 32*len(game)+56)], fill=imagetheme[1])
    draw.text((3,4), f"#{day}", font=ImageFont.truetype("sdv.ttf", 48), fill=imagetheme[2], anchor="lt", stroke_fill=imagetheme[1], stroke_width=1)
    draw.text((5*32+8,56), username, font=ImageFont.truetype("sdv.ttf", 16), fill=imagetheme[2], anchor="rd", stroke_fill=imagetheme[1], stroke_width=1)
    draw.ellipse(((134,3), (167,36)), fill=imagetheme[1])

    l2 = PILI.new("RGBA", bg.size, "#00000000")
    for i, guess in enumerate(game):
        for j, letter in enumerate(guess):
            l2.paste(PILI.open(guesstheme[int(letter)-1]).resize((30, 30)), (j*32 + 9, i*32 + 57))
    
    l3, l3m = PILI.new("RGBA", bg.size, "#00000000"), PILI.new("L", bg.size, 0)
    await user.avatar.save(f"exports\{user.id}.png")
    l3.paste(PILI.open(f"exports\{user.id}.png").resize((32,32)), (135,4))
    draw = ImageDraw.Draw(l3m, "L")
    draw.ellipse(((135,4), (166,35)), fill=255)
    l3.putalpha(l3m)
    
    image = PILI.alpha_composite(bg, l1)
    image = PILI.alpha_composite(image, l2)
    image = PILI.alpha_composite(image, l3)

    os.remove(f"exports\{user.id}.png")
    return image

async def genimglarge(game, user: discord.User, day, imagetheme, guesstheme):
    username = user.name.upper()
    if len(username) > 15: username = f"{username[:15]}..."

    bg = PILI.open(imagetheme[0]).convert("RGBA").resize((32*10 + 32, 64*len(game) + 128))

    l1 = PILI.new("RGBA", bg.size, "#00000000")
    draw = ImageDraw.Draw(l1, "RGBA")
    draw.polygon([(14, 110), (32*10+17, 110), (32*10+17, 64*len(game)+113), (14, 64*len(game)+113)], fill=imagetheme[1])
    draw.text((14,8), str(day), font=ImageFont.truetype("sdv.ttf", 96), fill=imagetheme[2], anchor="lt", stroke_fill=imagetheme[1], stroke_width=2)
    draw.text((10*32+16,112), username, font=ImageFont.truetype("sdv.ttf", 32), fill=imagetheme[2], anchor="rd", stroke_fill=imagetheme[1], stroke_width=2)
    draw.ellipse(((268,6), (334,72)), fill=imagetheme[1])

    l2 = PILI.new("RGBA", bg.size, "#00000000")
    for i, guess in enumerate(game):
        for j, letter in enumerate(guess):
            l2.paste(PILI.open(guesstheme[int(letter)-1]).resize((60, 60)), (j*64 + 18, i*64 + 114))
    
    l3, l3m = PILI.new("RGBA", bg.size, "#00000000"), PILI.new("L", bg.size, 0)
    await user.avatar.save(f"exports\{user.id}.png")
    l3.paste(PILI.open(f"exports\{user.id}.png").resize((64,64)), (270,8))
    draw = ImageDraw.Draw(l3m, "L")
    draw.ellipse(((270,8), (332,70)), fill=255)
    l3.putalpha(l3m)
    
    image = PILI.alpha_composite(bg, l1)
    image = PILI.alpha_composite(image, l2)
    image = PILI.alpha_composite(image, l3)

    os.remove(f"exports\{user.id}.png")
    return image
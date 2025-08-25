from PIL import Image as PILI, ImageDraw, ImageFont
import discord
import os

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
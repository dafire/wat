import os

from PIL import Image, ImageDraw, ImageFont
from django.http import HttpResponse

PATH = os.path.dirname(os.path.abspath(__file__))


def draw_caption(img, text, top=False):
    draw = ImageDraw.Draw(img)
    # Find a suitable font size to fill the entire width:
    w = img.size[0]
    s = 100
    while w >= (img.size[0] - 20):
        font = ImageFont.truetype(os.path.join(PATH, "Subway-Black.ttf"), s)
        w, h = draw.textsize(text, font=font)
        s -= 1
        if s <= 12: break
    # Draw the text multiple times in black to get the outline:
    for x in range(-3, 4):
        for y in range(-3, 4):
            draw_y = y if top else img.size[1] - h + y
            draw.text((10 + x, draw_y), text, font=font, fill='black')
    # Draw the text once more in white:
    draw_y = 0 if top else img.size[1] - h
    draw.text((10, draw_y), text, font=font, fill='white')


def banner(request):
    image = Image.open(os.path.join(PATH, "banner.png"))

    draw_caption(image, "Generol")

    response = HttpResponse(content_type="image/png")
    image.save(response, "PNG")
    return response

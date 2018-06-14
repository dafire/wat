import os

from PIL import Image, ImageDraw, ImageFont
from django.http import HttpResponse

PATH = os.path.dirname(os.path.abspath(__file__))


class Banner():
    def __init__(self):
        self.image = Image.open(os.path.join(PATH, "banner.png"))

    def draw_caption(self, text, size=20, outline=2, x_offset=2, y_offset=2):
        draw = ImageDraw.Draw(self.image)

        font = ImageFont.truetype(os.path.join(PATH, "Subway-Black.ttf"), size)

        # Draw the text multiple times in black to get the outline:
        for x in range(1 - outline, outline):
            for y in range(1 - outline, outline):
                draw.text((x + x_offset, y + y_offset), text, font=font, fill='black')
        # Draw the text once more in white:

        draw.text((x_offset, y_offset), text, font=font, fill='white')
        size = draw.textsize(text, font=font)
        return size[0] + x_offset, size[1] + y_offset

    def response(self):
        response = HttpResponse(content_type="image/png")
        self.image.save(response, "PNG")
        return response


def banner(request):
    img = Banner()
    x, y = img.draw_caption("Generol ")
    print(img.draw_caption("[aim-j]", x_offset=x))
    return img.response()

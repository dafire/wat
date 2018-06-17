import os
import time
from collections import defaultdict

from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.cache import cache_control

from wot_web_wtr.models import WebWtrRating

PATH = os.path.dirname(os.path.abspath(__file__))


class Banner():
    def __init__(self):
        self.image = Image.open(os.path.join(PATH, "banner.png"))

    def draw_caption(self, text, headline=False, color='white', size=None, outline=3, x_offset=2, y_offset=2):
        draw = ImageDraw.Draw(self.image)
        text = str(text)
        if headline:
            font = ImageFont.truetype(os.path.join(PATH, "Subway-Black.ttf"), size or 20)
        else:
            font = ImageFont.truetype(os.path.join(PATH, "VeraMono.ttf"), size or 14)
        # Draw the text multiple times in black to get the outline:
        for x in range(1 - outline, outline):
            for y in range(1 - outline, outline):
                draw.text((x + x_offset, y + y_offset), text, font=font, fill='black')
        # Draw the text once more in white:

        draw.text((x_offset, y_offset), text, font=font, fill=color)
        size = draw.textsize(text, font=font)
        return size[0] + x_offset, size[1] + y_offset

    def response(self):
        response = HttpResponse(content_type="image/jpeg")
        self.image.save(response, "JPEG", quality=90, progression=True, optimize=True, dpi=(72, 72))
        return response

    def save(self, filename):
        self.image.save(filename, "JPEG", quality=90, progression=True, optimize=True, dpi=(72, 72))


LABEL = {"day": "Gestern", "overall": "seit Dez.14"}

OFFSET = 100
WTR_X = OFFSET + 170
WINRATE_X = OFFSET + 260
GEFECHTE_X = OFFSET + 110


def create_image():
    img = Banner()
    ratings = WebWtrRating.objects.values('date', 'time_slice', 'personal') \
        .filter(time_slice__in=['day', 'overall', '2018-06']) \
        .filter(account_id="500447063", tier_group=0) \
        .distinct('time_slice') \
        .order_by('time_slice', '-date') \
        .values_list('date', 'time_slice', 'personal', named=True)

    nickname = ""
    clan = ""
    rat = defaultdict(lambda: (0, 0, 0, 0, 0))
    for r in ratings:
        rat[r.time_slice] = (
            r.personal.get("sbr"), r.personal.get("sbr_delta"), r.personal.get("battles_count"),
            r.personal.get("win_rate"),
            r.personal.get("win_rate_delta"))
        nickname = r.personal.get("nickname", '')
        clan = r.personal.get("clan_info", {}).get('tag', '')
    x, y = img.draw_caption(nickname, headline=True)
    if clan:
        img.draw_caption("[%s]" % clan, x_offset=x + 5, headline=True)

    line = y + 10
    img.draw_caption("WTR", x_offset=WTR_X, y_offset=line)
    img.draw_caption("WinRate", x_offset=WINRATE_X, y_offset=line)
    img.draw_caption("Gef.", x_offset=GEFECHTE_X, y_offset=line)

    for l in ['day', '2018-06', 'overall']:
        line = line + 16
        img.draw_caption(LABEL.get(l, l) + ":", y_offset=line)

        x, _ = img.draw_caption(rat[l][2], x_offset=GEFECHTE_X, y_offset=line)

        x, _ = img.draw_caption(rat[l][0], x_offset=WTR_X, y_offset=line)
        if rat[l][1]:
            if rat[l][1] > 0:
                color = 'lightgreen'
            else:
                color = 'red'
            img.draw_caption("({0:+})".format(rat[l][1]), color=color, x_offset=x + 1, y_offset=line)

        x, _ = img.draw_caption(rat[l][3], x_offset=WINRATE_X, y_offset=line)
        if rat[l][4]:
            if rat[l][4] > 0:
                color = 'lightgreen'
            else:
                color = 'red'
            img.draw_caption("({0:+})".format(rat[l][4]), color=color, x_offset=x + 1, y_offset=line)

    return img


@cache_control(max_age=7200)
def banner(request):
    img = create_image()
    return img.response()


@cache_control(max_age=7200)
def banner_x_accel(request):
    if not settings.MEDIA_ROOT:
        return HttpResponse("missing media root", status=500)
    file_name = "generol.jpg"
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)
    try:
        ftime = os.path.getctime(file_path)
    except FileNotFoundError:
        ftime = 0
        pass

    if time.time() - ftime > 7200:
        img = create_image()
        img.save(file_path)

    response = HttpResponse(content_type="image/jpeg")
    response['X-Accel-Redirect'] = "/media/" + file_name
    return response

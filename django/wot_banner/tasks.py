import os
from collections import defaultdict

from PIL import Image, ImageDraw, ImageFont
from celery import shared_task, chord
from django.conf import settings
from django.http import HttpResponse

from wot_api.tasks import get_xvm_scale
from wot_web_wtr.models import WebWtrRating
from wot_web_wtr.tasks import update_user

PATH = os.path.dirname(os.path.abspath(__file__))


class Banner():
    def __init__(self, userid=None):
        self.userid = userid
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

    def save_png(self):
        if not settings.MEDIA_ROOT:
            raise ("MEDIAROOT NOT SET")
        if not self.userid:
            raise ("userid NOT SET")
        file_path = os.path.join(settings.MEDIA_ROOT, "%s.png" % str(self.userid))

        self.image.save(file_path, "PNG", optimize=True)


LABEL = {"day": "Gestern", "overall": "seit Dez.14"}

OFFSET = 100
WTR_X = OFFSET + 170
WINRATE_X = OFFSET + 260
GEFECHTE_X = OFFSET + 110


def color_value(typ, value):
    arr = get_xvm_scale(typ)
    if arr:
        l = len(arr)
        i = 0
        while i < l and value > arr[i]:
            i += 1
        if i < 17:
            return "#FE0E00"
        elif i < 34:
            return "#FE7903"
        elif i < 53:
            return "#F8F400"
        elif i < 76:
            return "#459300"
        elif i < 93:
            return "#02C9B3"
        else:
            return "#D042F3"

    return "white"


def create_image(userid):
    img = Banner(userid=userid)
    ratings = WebWtrRating.objects.values('date', 'time_slice', 'personal') \
        .filter(time_slice__in=['day', 'overall', '2018-06']) \
        .filter(account_id=userid, tier_group=0) \
        .distinct('time_slice') \
        .order_by('time_slice', '-date') \
        .values_list('date', 'time_slice', 'personal', named=True)

    nickname = ""
    clan = ""
    color = "white"
    rat = defaultdict(lambda: (0, 0, 0, 0, 0))
    for r in ratings:
        rat[r.time_slice] = (
            r.personal.get("sbr"), r.personal.get("sbr_delta"), r.personal.get("battles_count"),
            r.personal.get("win_rate"),
            r.personal.get("win_rate_delta"))
        nickname = r.personal.get("nickname", '')
        clan = r.personal.get("clan_info", {}).get('tag', '')
        color = r.personal.get("clan_info", {}).get("color", "white")
    x, y = img.draw_caption(nickname, x_offset=8, headline=True)
    if clan:
        img.draw_caption("[%s]" % clan, x_offset=x + 6, headline=True, color=color)

    line = y + 10
    img.draw_caption("WTR", x_offset=WTR_X, y_offset=line)
    img.draw_caption("WinRate", x_offset=WINRATE_X, y_offset=line)
    img.draw_caption("Gef.", x_offset=GEFECHTE_X, y_offset=line)

    for l in ['day', '2018-06', 'overall']:
        line = line + 16
        img.draw_caption(LABEL.get(l, l) + ":", x_offset=8, y_offset=line)

        x, _ = img.draw_caption(rat[l][2], x_offset=GEFECHTE_X, y_offset=line)

        x, _ = img.draw_caption(rat[l][0], x_offset=WTR_X, y_offset=line, color=color_value('xwtr', rat[l][0]))
        if rat[l][1]:
            if rat[l][1] > 0:
                color = 'lightgreen'
            else:
                color = 'red'
            img.draw_caption("({0:+})".format(rat[l][1]), color=color, x_offset=x + 1, y_offset=line)

        x, _ = img.draw_caption(rat[l][3], x_offset=WINRATE_X, y_offset=line, color=color_value('xwin', rat[l][3]))
        if rat[l][4]:
            if rat[l][4] > 0:
                color = 'lightgreen'
            else:
                color = 'red'
            img.draw_caption("({0:+})".format(rat[l][4]), color=color, x_offset=x + 1, y_offset=line)

    return img


@shared_task
def create_banner_asset(result, userid):
    if not settings.MEDIA_ROOT:
        raise ("MEDIAROOT NOT SET")

    img = create_image(userid)
    img.save_png()


@shared_task
def update_banner(userid):
    res = chord((update_user.s(userid, day=True),
                 update_user.s(userid, month=True),
                 update_user.s(userid, overall=True)),
                create_banner_asset.s(userid))()
    print(res.get())

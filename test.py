import os

from django.core.wsgi import get_wsgi_application
from pprint import pprint

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wat.settings")
os.environ.setdefault("SECRET_KEY", "wat.settings")

application = get_wsgi_application()

from wot_api.models import ExpectedWN8Values, VehicleStatisticItem


def calculate_wn8(stats: VehicleStatisticItem, expected: ExpectedWN8Values):
    battles = stats.all.get("battles")
    winrate = stats.all.get("wins") / battles * 100

    rWIN = winrate / expected.exp_win_rate
    rDAMAGE = stats.all.get("damage_dealt") / expected.exp_damage
    rSPOT = stats.all.get("spotted") / expected.exp_spot
    rFRAG = stats.all.get("frags") / expected.exp_frag
    rDEF = stats.all.get("dropped_capture_points") / expected.exp_def


    rWINc = max(0, (rWIN - 0.71) / (1 - 0.71))
    rDAMAGEc = max(0, (rDAMAGE - 0.22) / (1 - 0.22))
    rFRAGc = max(0, min(rDAMAGEc + 0.2, (rFRAG - 0.12) / (1 - 0.12)))
    rSPOTc = max(0, min(rDAMAGEc + 0.1, (rSPOT - 0.38) / (1 - 0.38)))
    rDEFc = max(0, min(rDAMAGEc + 0.1, (rDEF - 0.10) / (1 - 0.10)))

    wn8 = 980 * rDAMAGEc \
          + 210 * rDAMAGEc * rFRAGc \
          + 155 * rFRAGc * rSPOTc \
          + rSPOTc \
          + 75 * rDEFc * rFRAGc \
          + 145 * min( 1.8, rWINc)

    return wn8

stats = VehicleStatisticItem(
    all={
        "battles": 100,
        "damage_dealt": 3665,
        "spotted": 1.84,
        "frags": 1.88,
        "dropped_capture_points": 1.51,
        "wins": 70.5
    }
)

expected = ExpectedWN8Values(
    exp_damage=1840.29,
    exp_spot=1.41,
    exp_frag=0.93,
    exp_def=0.76,
    exp_win_rate=48.73
)

calculate_wn8(stats, expected)

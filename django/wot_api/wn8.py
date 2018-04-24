from wot_api.models import VehicleStatisticItem, ExpectedWN8Values


def calculate_wn8(stats: VehicleStatisticItem, expected: ExpectedWN8Values = None):
    battles = stats.all.get("battles")
    winrate = stats.all.get("wins") / battles * 100

    if not expected:
        expected = stats.vehicle.expected

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
          + 145 * min(1.8, rWINc)

    return wn8

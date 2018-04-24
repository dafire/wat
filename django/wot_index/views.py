from django.views.generic import TemplateView, DetailView

from wot_api import models
from wot_api.models import VehicleStatistic, VehicleStatisticItem
from wot_api.wn8 import calculate_wn8
from wot_user.models import User


class ClanView(TemplateView):
    template_name = "index/clan.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        data['object_list'] = models.ClanInfo.objects \
            .select_related("account") \
            .order_by("account__nickname") \
            .all()

        return data


class PlayerView(DetailView):
    template_name = "index/player.html"
    context_object_name = "account"
    model = User

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        data['user_info_list'] = models.UserInfo.objects \
            .filter(account_id=self.object.account_id) \
            .order_by("created") \
            .all()

        return data


class WN8View(DetailView):
    context_object_name = "account"
    model = User
    template_name = "index/wn8.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        account_id = self.object.account_id

        vehiclestatistics = VehicleStatistic.objects.filter(account_id=account_id).order_by("created").last()

        data["created"] = vehiclestatistics.created

        expDamage = expSpot = expDEF = expFRAG = expWIN = 0
        sBattles = sDamage = sSpot = sDEF = sFRAG = sWIN = 0

        stats = VehicleStatisticItem.objects \
            .filter(statistic_call=vehiclestatistics) \
            .select_related("vehicle", "vehicle__expected") \
            .order_by("vehicle__name").all()

        for s in stats:
            # print(s.vehicle_id)
            battles = s.all.get("battles")
            sBattles += battles
            expDamage += s.vehicle.expected.exp_damage * battles
            sDamage += s.all.get("damage_dealt")
            s.damage = s.all.get("damage_dealt") / battles

            expSpot += s.vehicle.expected.exp_spot * battles
            s.spotted = s.all.get("spotted") / battles
            sSpot += s.all.get("spotted")

            expFRAG += s.vehicle.expected.exp_frag * battles
            s.frag = s.all.get("frags") / battles
            sFRAG += s.all.get("frags")

            expDEF += s.vehicle.expected.exp_def * battles
            s.deffed = s.all.get("dropped_capture_points") / battles
            sDEF += s.all.get("dropped_capture_points")

            expWIN += 0.01 * s.vehicle.expected.exp_win_rate * battles
            s.winrate = s.all.get("wins") / battles * 100
            sWIN += s.all.get("wins")

            s.wn8 = calculate_wn8(s)

        rDAMAGE = sDamage / expDamage
        rSPOT = sSpot / expSpot
        rFRAG = sFRAG / expFRAG
        rDEF = sDEF / expDEF
        rWIN = sWIN / expWIN

        rWINc = max(0, (rWIN - 0.71) / (1 - 0.71))
        rDAMAGEc = max(0, (rDAMAGE - 0.22) / (1 - 0.22))
        rFRAGc = max(0, min(rDAMAGEc + 0.2, (rFRAG - 0.12) / (1 - 0.12)))
        rSPOTc = max(0, min(rDAMAGEc + 0.1, (rSPOT - 0.38) / (1 - 0.38)))
        rDEFc = max(0, min(rDAMAGEc + 0.1, (rDEF - 0.10) / (1 - 0.10)))

        data["wn8"] = 980 * rDAMAGEc \
                      + 210 * rDAMAGEc * rFRAGc \
                      + 155 * rFRAGc * rSPOTc \
                      + rSPOTc \
                      + 75 * rDEFc * rFRAGc \
                      + 145 * min(1.8, rWINc)

        data["vehicles_stats"] = stats

        return data


class UserInfoView(DetailView):
    model = models.UserInfo
    template_name = "index/userinfo.html"

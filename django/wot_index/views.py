from django.views.generic import TemplateView, DetailView

from wot_api import models
from wot_api.models import UserInfo, VehicleStatistic, VehicleStatisticItem
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

        userinfo = UserInfo.objects.filter(account_id=account_id).order_by("created").last()
        data["summary"] = userinfo.data.get("statistics").get("all")

        vehiclestatistics = VehicleStatistic.objects.filter(account_id=account_id).order_by("created").last()

        expDamage = expSpot = expDEF = expWIN = 0

        stats = VehicleStatisticItem.objects \
            .filter(statistic_call=vehiclestatistics) \
            .select_related("vehicle", "vehicle__expected") \
            .all()

        for s in stats:
            # print(s.vehicle_id)
            battles = s.all.get("battles")
            expDamage += s.vehicle.expected.exp_damage * battles
            s.damage = s.all.get("damage_dealt") / battles
            expSpot += s.vehicle.expected.exp_spot * battles
            s.spotted = s.all.get("spotted") / battles
            expDEF += s.vehicle.expected.exp_def * battles
            s.deffed = s.all.get("dropped_capture_points") / battles
            expWIN += s.vehicle.expected.exp_win_rate * battles
            s.winrate = s.all.get("wins") / battles * 100
            # pprint(s.all)

        data["vehicles_stats"] = stats

        return data


class UserInfoView(DetailView):
    model = models.UserInfo
    template_name = "index/userinfo.html"

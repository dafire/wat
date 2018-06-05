from django.db.models import Prefetch
from django.views.generic import TemplateView, DetailView

from wot_api import models
from wot_api.models import VehicleStatistic, VehicleStatisticItem
from wot_api.wn8 import WN8Calculation
from wot_user.models import User


class IndexView(TemplateView):
    template_name = "index/index.html"

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

        prefetch = Prefetch("vehiclestatisticitem_set",
                            queryset=VehicleStatisticItem.objects
                            .select_related("vehicle", "vehicle__expected")
                            .only("id", "all", "statistic_call_id",
                                  "vehicle__name",
                                  "vehicle__expected__exp_damage",
                                  "vehicle__expected__exp_def",
                                  "vehicle__expected__exp_frag",
                                  "vehicle__expected__exp_spot",
                                  "vehicle__expected__exp_win_rate"))

        out_stats = []

        stats = models.VehicleStatistic.objects \
            .filter(account_id=self.object.account_id) \
            .prefetch_related(prefetch) \
            .only("pk", "first_of_day", "account", "created") \
            .order_by("-created") \
            .all()[:5]

        last_stat = None
        for stat in stats:
            stat.wn8 = WN8Calculation(stat)
            if last_stat:
                last_stat.wn8.subtract_wn8(stat.wn8)
                if last_stat.wn8.battles > 0:
                    out_stats.append(last_stat)
            last_stat = stat

        if last_stat and last_stat.wn8.battles > 0:
            out_stats.append(last_stat)

        data['stats'] = out_stats
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

        # TODO: FIXME: nur felder abrufen die auch gebraucht werden... das sind eine menge daten!
        stats = VehicleStatisticItem.objects \
            .filter(statistic_call=vehiclestatistics) \
            .select_related("vehicle", "vehicle__expected") \
            .order_by("vehicle__name").all()

        wn8calc = WN8Calculation()

        for s in stats:
            wn8calc.add_vehicle(s)

        data["wn8"] = wn8calc

        return data


class UserInfoView(DetailView):
    model = models.UserInfo
    template_name = "index/userinfo.html"

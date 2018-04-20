from datetime import datetime, timedelta

import celery
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from wot_api.models import ClanInfo, UserInfo, VehicleStatistic, VehicleStatisticItem, Vehicle
from wot_user.models import User
from . import wot_api


@celery.task()
def update_vehicles():
    data = wot_api.vehicles()

    with transaction.atomic():
        Vehicle.objects.all().delete()

        for tankid, v_data in data.items():
            vehicle = Vehicle()
            for d in ['tank_id', 'name', 'short_name', 'type', 'nation', 'tier', 'description', 'tag', 'is_premium',
                      'is_gift', 'images', 'price_gold', 'price_credit']:
                setattr(vehicle, d, v_data.get(d))
            vehicle.save()


#    with transaction.atomic():
#        stats = VehicleStatistic.objects.create(account_id=account_id)

#        for tank in data:
#            vehicle = VehicleStatisticItem(statistic_call=stats)
#            for s in ['clan', 'stronghold_skirmish', 'regular_team', 'account_id', 'max_xp',
#                      'company', 'all', 'stronghold_defense', 'max_frags', 'team', 'globalmap', 'frags',
#                      'mark_of_mastery', 'in_garage', 'tank_id']:
#                setattr(vehicle, s, tank.get(s))
#            vehicle.save()


@celery.task()
def update_vehicle_statistic(account_id):
    data = wot_api.vehicle_statistics(account_id=account_id)

    with transaction.atomic():
        stats = VehicleStatistic.objects.create(account_id=account_id)

        for tank in data:
            vehicle = VehicleStatisticItem(statistic_call=stats)
            for s in ['clan', 'stronghold_skirmish', 'regular_team', 'account_id', 'max_xp',
                      'company', 'all', 'stronghold_defense', 'max_frags', 'team', 'globalmap', 'frags',
                      'mark_of_mastery', 'in_garage', 'tank_id']:
                setattr(vehicle, s, tank.get(s))
            vehicle.save()


@celery.task()
def update_userinfo(account_id, min_age=10800):
    last_data = UserInfo.objects.filter(account_id=account_id).order_by("created").last()
    if last_data and last_data.created + timedelta(seconds=min_age) > timezone.now():
        return

    update_vehicle_statistic.delay(account_id)

    data = wot_api.players_personal_data(account_id)

    UserInfo.objects.create(account_id=account_id, data=data)

    try:
        dirty = []
        user = User.objects.get(account_id=account_id)
        for check in ['nickname']:
            value = data.get(check)
            if getattr(user, check) != value:
                setattr(user, check, value)
                dirty.append(check)

        if len(dirty):
            user.save(update_fields=dirty)
    except User.DoesNotExist:
        User.objects.create_wot_user(wot_account_id=account_id, wot_nickname=data.get("nickname"))


@celery.task()
def update_clan(clan_id, do_update_userinfo=False):
    data = wot_api.get_clan_details(clan_id=clan_id)
    updated = timezone.now()
    members = data.get("members")
    with transaction.atomic():
        for member in members:
            obj, _ = ClanInfo.objects.update_or_create(account_id=member.get("account_id"), defaults={
                "clan_id": clan_id,
                "role": member.get("role"),
                "role_i18n": member.get("role_i18n"),
                "joined": datetime.fromtimestamp(member.get("joined_at")).replace(tzinfo=timezone.utc),
                "updated": updated
            })
            if do_update_userinfo:
                update_userinfo.delay(obj.account_id)

        for model in ClanInfo.objects.filter(clan_id=clan_id, updated__lt=updated).all():
            model.delete()


@celery.task()
def update_default_clan():
    print("update default clan")
    update_clan(settings.WOT_CLAN, do_update_userinfo=True)

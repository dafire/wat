from datetime import datetime, timedelta

import celery
from celery.utils.log import get_logger
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from requests import get

from wot_user.models import User
from . import wot_api
from .models import ClanInfo, UserInfo, VehicleStatistic, VehicleStatisticItem, Vehicle, ExpectedWN8Values, KVStore

logger = get_logger(__name__)

RATE_LIMIT = 18


class TaskType:
    VEHICLE_STATISTIC = "vehicle"
    USERINFO = "userinfo"
    CLAN = "clan"


def update_vehicle_statistic(account_id, userinfo_id=None):
    _wot_api_update.delay(task_type=TaskType.VEHICLE_STATISTIC, account_id=account_id, userinfo_id=userinfo_id)


def update_userinfo(account_id):
    _wot_api_update.delay(task_type=TaskType.USERINFO, account_id=account_id)


def update_clan(clan_id):
    _wot_api_update.delay(task_type=TaskType.CLAN, clan_id=clan_id)


@celery.task(ignore_result=True)
def update_known_users():
    user_ids = User.objects \
        .order_by("account_id", "-userinfo__created") \
        .distinct("account_id") \
        .exclude(userinfo__updated__gte=timezone.now() - timedelta(minutes=60)) \
        .values_list("account_id", "userinfo__updated", named=True)
    for u in user_ids:
        logger.info("update_known_users account: %d (last_update:%r)", u.account_id, u.userinfo__updated)
        update_userinfo(u.account_id)


def convert_timestamp(time: int):
    return datetime.fromtimestamp(time).replace(tzinfo=timezone.utc)


@celery.task(rate_limit=RATE_LIMIT, ignore_result=True)
def _wot_api_update(task_type: TaskType, **kwargs):
    if task_type == TaskType.VEHICLE_STATISTIC:
        _update_vehicle_statistic(**kwargs)
    elif task_type == TaskType.USERINFO:
        _update_userinfo(**kwargs)
    elif task_type == TaskType.CLAN:
        _update_clan(**kwargs)


@celery.task()
def update_vehicles(ignore_result=True):
    data = wot_api.vehicles()

    with transaction.atomic():
        Vehicle.objects.all().delete()

        for tankid, v_data in data.items():
            vehicle = Vehicle()
            for d in ['tank_id', 'name', 'short_name', 'type', 'nation', 'tier', 'description', 'tag', 'is_premium',
                      'is_gift', 'images', 'price_gold', 'price_credit']:
                setattr(vehicle, d, v_data.get(d))
            vehicle.save()


@celery.task(ignore_result=True)
def update_default_clan():
    print("update default clan")
    update_clan(settings.WOT_CLAN)


@celery.task(ignore_result=True)
def update_expected_values_wn8():
    data = get("https://static.modxvm.com/wn8-data-exp/json/wn8exp.json").json()

    with transaction.atomic():
        ExpectedWN8Values.objects.all().delete()
        for row in data.get("data"):
            ExpectedWN8Values.objects.create(vehicle_id=row.get("IDNum"),
                                             exp_damage=row.get("expDamage"),
                                             exp_def=row.get("expDef"),
                                             exp_frag=row.get("expFrag"),
                                             exp_spot=row.get("expSpot"),
                                             exp_win_rate=row.get("expWinRate"))
        KVStore.objects.update_or_create(key="expected_values_wn8",
                                         defaults={"value": data.get("header").get("version")})


@celery.task()
def update_xvm_scales():
    data = get("https://static.modxvm.com/xvmscales.json").json()


def _update_vehicle_statistic(account_id, userinfo_id):
    last_data = VehicleStatistic.objects.filter(account_id=account_id).order_by("created").last()

    first_of_day = False
    if not last_data or last_data.created < _last_start_of_day():
        first_of_day = True

    logger.info("update_vehicle_statistic account: %d (first_of_day:%r)", account_id, first_of_day)

    data = wot_api.vehicle_statistics(account_id=account_id)

    with transaction.atomic():
        stats = VehicleStatistic.objects.create(account_id=account_id, first_of_day=first_of_day,
                                                userinfo_id=userinfo_id, data=data)

        for tank in data:
            vehicle = VehicleStatisticItem(statistic_call=stats)
            for s in ['clan', 'stronghold_skirmish', 'regular_team', 'account_id', 'max_xp',
                      'company', 'all', 'stronghold_defense', 'max_frags', 'team', 'globalmap', 'frags',
                      'mark_of_mastery', 'in_garage']:
                setattr(vehicle, s, tank.get(s))
            vehicle.vehicle_id = tank.get("tank_id")
            vehicle.save()


def _last_start_of_day(point=None):
    if not point:
        point = timezone.now()
    if point.hour < 5:
        point -= timedelta(days=1)

    return point.replace(hour=5, minute=0, second=0, microsecond=0)


def _update_userinfo(account_id):
    last_data = UserInfo.objects.filter(account_id=account_id).order_by("created").last()

    do_vehicle_stats_update = False
    first_of_day = False
    if not last_data or last_data.created < _last_start_of_day():
        first_of_day = True

    logger.info("update_userinfo account: %d (first_of_day:%r)", account_id, first_of_day)

    data = wot_api.players_personal_data(account_id)

    if first_of_day:
        do_vehicle_stats_update = True
    else:
        if last_data.data.get("updated_at") == data.get("updated_at"):
            last_data.updated = timezone.now()
            last_data.save(update_fields=["updated"])
            logger.info("update_userinfo account: %d : DATA NOT CHANGED", account_id)
            return
        if last_data.data.get("last_battle_time") != data.get("last_battle_time"):
            do_vehicle_stats_update = True

    userinfo = UserInfo.objects.create(account_id=account_id, data=data, first_of_day=first_of_day)

    if do_vehicle_stats_update:
        update_vehicle_statistic(account_id, userinfo.pk)
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


def _update_clan(clan_id):
    logger.info("update_clan clan_id: %d", clan_id)
    data = wot_api.get_clan_details(clan_id=clan_id)
    updated = timezone.now()
    members = data.get("members")
    with transaction.atomic():
        for member in members:
            obj, _ = ClanInfo.objects.update_or_create(account_id=member.get("account_id"), defaults={
                "clan_id": clan_id,
                "role": member.get("role"),
                "role_i18n": member.get("role_i18n"),
                "joined": convert_timestamp(member.get("joined_at")),
                "updated": updated
            })

        for model in ClanInfo.objects.filter(clan_id=clan_id, updated__lt=updated).all():
            model.delete()

from datetime import datetime, timedelta

import celery
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from wot_api.models import ClanInfo, UserInfo
from wot_user.models import User
from . import wot_api


@celery.task()
def update_userinfo(account_id, min_age=3600):
    print("update", account_id)
    last_data = UserInfo.objects.filter(account_id=account_id).order_by("created").last()
    if last_data and last_data.created + timedelta(seconds=3000) > timezone.now():
        print(account_id, "data recent enough")
        return

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
        pass


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

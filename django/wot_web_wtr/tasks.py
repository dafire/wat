from datetime import datetime
from pprint import pprint

import requests
from celery import shared_task
from django.utils.timezone import now

from wot_web_wtr.models import WebWtrRating

SEARCH_URL = "https://worldoftanks.eu/wgris/hof/achievements/search/by_user/"


def update_user(account_id, high_tier=False, day=None, month=None, overall=None, time_slice=None):
    if high_tier:
        tier_group = "1"
    else:
        tier_group = "0"

    if day:
        slice = "day"
        battles = 10
    elif time_slice:
        slice = time_slice
        battles = 100
    elif month:
        slice = now().strftime("%Y-%m")
        battles = 100
    elif overall:
        slice = "overall"
        battles = 1000

    else:
        return

    params = {
        "lang": "de",
        "page": "1",
        "page_size": "20",
        "battles_count": str(battles),
        "tier_group": str(tier_group),
        "time_slice": str(slice),
        "stat_type": "sbr",
        "spa_id": str(account_id),
    }

    try:
        response = requests.get(url=SEARCH_URL, params=params)
        json = response.json()
        errors = json.get("errors")
        meta = json.get("meta")
        personal = json.get("data", {}).get("personal")
        pprint(params)
        pprint(errors)
        pprint(meta),
        pprint(personal)
        WebWtrRating.objects.create(
            account_id=account_id,
            battles_count=battles,
            tier_group=tier_group,
            time_slice=slice,
            date=datetime.utcfromtimestamp(meta.get("date", 0)),
            personal=personal,
            errors=errors
        )
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


@shared_task
def update_web_wtr():
    update_user(500447063, day=True)
    update_user(500447063, month=True)
    update_user(500447063, overall=True)

import hashlib
from pprint import pprint

from django.conf import settings
from django.core.cache import cache
from requests import post

if settings.DEBUG:
    CACHE_TIME = 900
else:
    CACHE_TIME = 30


def get_request(section, endpoint, data=None, game='wot', disable_cache=False):
    url = "https://api.worldoftanks.eu/%s/%s/%s/" % (game, section, endpoint)

    if not data:
        data = {}

    cache_key = hashlib.md5(url.encode("utf-8") + bytes(str(frozenset(data.items())), "utf-8")).hexdigest()

    print("h", url + str(frozenset(data.items())), cache_key)

    if not disable_cache:
        cached_data = cache.get(cache_key)
        if cached_data:
            print("CACHED")
            return cached_data

        print("NOT CACHED")
    token = settings.WARGAMING_TOKEN
    if token:
        data["application_id"] = token
    else:
        raise Exception("WARGAMING_TOKEN empty")

    data["language"] = "de"

    data_request = post(url, data=data)
    data_request.raise_for_status()

    data = data_request.json()

    if data.get("status") == "ok":
        if not disable_cache:
            cache.set(cache_key, data["data"], CACHE_TIME)
        return data["data"]

    pprint(data)
    raise Exception("wot not ok :(")


def players_personal_data(account_id, access_token=None):
    data = get_request("account", "info", {"account_id": account_id}).get(str(account_id))
    return data


def get_clan_details(clan_id, access_token=None):
    data = get_request("clans", "info", {"clan_id": clan_id}, game="wgn").get(str(clan_id))
    return data


def vehicle_statistics(account_id):
    data = get_request("tanks", "stats", {"account_id": account_id}).get(str(account_id))
    return data

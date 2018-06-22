import hashlib
import time
from pprint import pprint

from django.conf import settings
from django.core.cache import cache
from requests import post

CACHE_TIME = 60

connect_timeout, read_timeout = 5.0, 30.0


class WOTApiException(Exception):
    def __init__(self, details=None):
        self.details = details

    def __str__(self):
        return repr(self.details)


class WOTInvalidIPAddressException(WOTApiException):
    def __init__(self, ipaddress):
        self.ipaddress = ipaddress

    def __str__(self):
        return "IP: " + repr(self.ipaddress)


def get_request(section, endpoint, data=None, game='wot', disable_cache=False):
    url = "https://api.worldoftanks.eu/%s/%s/%s/" % (game, section, endpoint)

    if not data:
        data = {}

    cache_key = "api_" + hashlib.md5(url.encode("utf-8") + bytes(str(frozenset(data.items())), "utf-8")).hexdigest()

    if not disable_cache:
        cached_data = cache.get(cache_key)
        if cached_data:
            print("CACHED DATA FROM WGAPI")
            return cached_data

    token = settings.WARGAMING_TOKEN
    if token:
        data["application_id"] = token
    else:
        raise Exception("WARGAMING_TOKEN empty")

    data["language"] = "de"

    data_request = post(url, data=data, timeout=(connect_timeout, read_timeout))
    data_request.raise_for_status()

    data = data_request.json()

    if data.get("status") == "ok":
        if not disable_cache:
            cache.set(cache_key, data, CACHE_TIME)
        return data

    if data.get("status") == "error":
        error = data.get("error", {})
        if error.get("code") == 407:
            raise WOTInvalidIPAddressException(ipaddress=error.get("value"))

        raise WOTApiException(error)

    pprint(data)
    raise WOTApiException("wot not ok :(")


def players(search):
    data = get_request("account", "list", {"search": search})
    return data.get("data")


def players_personal_data(account_id, access_token=None):
    data = get_request("account", "info", {"account_id": account_id})
    return data.get("data").get(str(account_id))


def get_clan_details(clan_id, access_token=None):
    if not clan_id:
        raise Exception("NO CLAN ID")
    data = get_request("clans", "info", {"clan_id": clan_id}, game="wgn")
    return data.get("data").get(str(clan_id))


def vehicle_statistics(account_id):
    data = get_request("tanks", "stats", {"account_id": account_id})
    return data.get("data").get(str(account_id))


def account2bydate(account_id, last_data=None):
    if not last_data:
        last_data = int(time.time() - 3600 * 24 * 31)
    else:
        last_data = int(last_data.timestamp()) + 1
    data = get_request("stats", "account2bydate", {
        "account_id": account_id,
        "from_date": last_data,
        "to_date": int(time.time()),
        "language": "de",
        "interval": 1
    })
    return data.get("data"), data.get("meta")


def vehicles():
    data = get_request("encyclopedia", "vehicles")
    return data.get("data")
    # looks like the api always returns all fields for now
    #
    # vehicles_data = data.get("data")
    # meta = data.get("meta", {})
    # pages = meta.get("page_total", 0)
    # if meta.get("page_total", 0 > 1):
    #     for page in range(2, pages):
    #         data = get_request("encyclopedia", "vehicles", {"page_no": page})
    #         vehicles_data.update(data.get("data"))
    #         print(len(vehicles_data))
    # print(len(vehicles_data))
    # return vehicles_data

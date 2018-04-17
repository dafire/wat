import re

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseForbidden
from requests import get, post

from .models import AuthToken
from .auth import Authentication, Verification, check_nonce


def simple_login(request):
    auth = Authentication(return_to=request.build_absolute_uri("/auth/callback"))  # FIXME: url nicht hardcoden
    url = auth.authenticate('https://eu.wargaming.net/id/openid/')
    return HttpResponseRedirect(url)


def simple_callback(request):
    current_url = request.build_absolute_uri()

    verify = Verification(current_url)
    identities = verify.verify()

    regex = r'https://eu.wargaming.net/id/([0-9]+)-(\w+)/'
    match = re.search(regex, identities['identity'])
    account_id = match.group(1)
    nickname = match.group(2)

    user = authenticate(request, account_id=account_id, wot_username=nickname)
    if user:
        login(request, user)
        return HttpResponseRedirect("/")
    else:
        return JsonResponse({"error": True, "acc": account_id, "nick": nickname})


def ext_login(request):
    redirect_url = request.build_absolute_uri("/auth/callback2")  # FIXME: url nicht hardcoden
    login_link_request = get("https://api.worldoftanks.eu/wot/auth/login/", params={
        "application_id": settings.WARGAMING_TOKEN,
        "nofollow": "1",
        "redirect_uri": redirect_url,
        "expires_at": 3600
    })
    login_link_request.raise_for_status()
    login_link_data = login_link_request.json()
    if login_link_data.get("status") != "ok":
        return JsonResponse({"error": True})
    openid = login_link_data.get("data", {}).get("location")
    return HttpResponseRedirect(openid)


def ext_callback(request):
    access_token = request.GET.get("access_token")
    if not access_token:
        return HttpResponseForbidden()

    if not check_nonce(access_token):
        return HttpResponseForbidden()

    token_request = post("https://api.worldoftanks.eu/wot/auth/prolongate/", data={
        "application_id": settings.WARGAMING_TOKEN,
        "access_token": access_token,
        "expires_at": 1123200  # 13 days
    })

    auth_token_data = token_request.json()

    account_id = request.GET.get("account_id")
    nickname = request.GET.get("nickname")

    if not account_id or not nickname or not auth_token_data.get("status") == "ok":
        return HttpResponseForbidden()

    user = authenticate(request, account_id=account_id, wot_username=nickname)
    if user:
        login(request, user)

        AuthToken.objects.update_or_create(user=user, access_token=1, expire=1)

        return HttpResponseRedirect("/")
    else:
        return JsonResponse({"error": True, "acc": account_id, "nick": nickname})


def logoutView(request):
    logout(request)
    return HttpResponseRedirect("/")

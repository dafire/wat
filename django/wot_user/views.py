import re
from datetime import timedelta
from pprint import pprint

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseForbidden
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from requests import get, post

from .auth import Authentication, Verification, check_nonce
from .models import AuthToken


def login_response(request):
    auth = Authentication(return_to=request.build_absolute_uri(reverse("wot_user:callback")))
    url = auth.authenticate('https://eu.wargaming.net/id/openid/')
    return HttpResponseRedirect(url)


def simple_login(request):
    pprint(request.COOKIES)
    if 'fast_login' not in request.COOKIES:
        return HttpResponseRedirect(reverse("wot_user:login-ext"))
    return login_response(request)


def login_view(request):
    if request.GET.get("login"):
        return login_response(request)
    return render(request, "wot_user/login.html", context={"login_url": reverse("wot_user:login-ext") + "?login=1"})


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
        response = HttpResponseRedirect("/")
        response.set_cookie("fast_login", "1", expires=timezone.now() + timedelta(days=7))
        return response
    else:
        return JsonResponse({"error": True, "acc": account_id, "nick": nickname})


def ext_login(request):
    redirect_url = request.build_absolute_uri(reverse("wot_user:callback2"))
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


def logout_view(request):
    logout(request)
    return HttpResponseRedirect("/")

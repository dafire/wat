import os
import time

from django.conf import settings
from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.utils.timezone import now
from django.views.decorators.cache import cache_control

from wot_api.wot_api import players
from wot_banner.tasks import create_image, update_banner
from wot_web_wtr.models import WebWtrRating
from . import forms


@cache_control(max_age=3600)
def banner_view(request, userid):
    if not settings.MEDIA_ROOT:
        return HttpResponse("missing media root", status=500)
    file_name = "%s.png" % str(userid)
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)
    try:
        ftime = os.path.getctime(file_path)
    except FileNotFoundError:
        raise Http404()

    response = HttpResponse(content_type="image/png")
    response['X-Accel-Redirect'] = "/media/" + file_name
    return response


@cache_control(max_age=7200)
def banner(request):
    img = create_image(500447063)
    return img.response()


@cache_control(max_age=7200)
def banner_x_accel(request):
    if not settings.MEDIA_ROOT:
        return HttpResponse("missing media root", status=500)
    file_name = "generol.jpg"
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)
    try:
        ftime = os.path.getctime(file_path)
    except FileNotFoundError:
        ftime = 0
        pass

    if time.time() - ftime > 7200:
        img = create_image(500447063)
        img.save(file_path)

    response = HttpResponse(content_type="image/jpeg")
    response['X-Accel-Redirect'] = "/media/" + file_name
    return response


def banner_search_view(request):
    form = forms.SearchForm(data=request.POST)
    pl = None
    if request.method == "POST" and form.is_valid():
        pl = players(search=form.cleaned_data['name'])
    return render(request, "wot_banner/search.html", context={"form": form, "pl": pl})


def banner_view_adhoc(request, userid):
    update_needed = not WebWtrRating.objects.filter(account_id=userid,
                                                    date__gte=now().replace(hour=1, minute=0)).exists()
    if update_needed:
        update_banner.delay(userid)

    return render(request, "wot_banner/adhoc.html", context={"userid": userid})

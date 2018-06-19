import os
import time

from django.conf import settings
from django.http import HttpResponse, Http404
from django.views.decorators.cache import cache_control

from wot_banner.tasks import create_image


@cache_control(max_age=3600)
def banner_view(request, userid):
    if not settings.MEDIA_ROOT:
        return HttpResponse("missing media root", status=500)
    file_name = "%s.png" % str(userid)
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)
    try:
        ftime = os.path.getctime(file_path)
    except FileNotFoundError:
        return Http404()

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

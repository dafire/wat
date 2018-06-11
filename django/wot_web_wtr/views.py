from django.http import HttpResponse

# Create your views here.
from wot_web_wtr.tasks import update_user


def test(request):
    update_user(500447063, day=True)
    update_user(500447063, month=True)
    update_user(500447063, overall=True)

    # update_user(500447063, day="2018-05")
    # update_user(500447063, day="2018-04")
    return HttpResponse("!")

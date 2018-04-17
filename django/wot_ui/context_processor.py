from django.conf import settings


def const_processor(request):
    return {
        "PROJECT_TITLE": settings.PROJECT_TITLE
    }

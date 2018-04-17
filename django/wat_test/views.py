from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.template import TemplateDoesNotExist


def index(request):
    return render(request, "test/index.html")


def component(request, template_name):
    try:
        return render(request, "test/components/%s.html" % template_name)
    except TemplateDoesNotExist:
        return HttpResponse("<h3>NotFound</h3>")

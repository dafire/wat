from celery.result import EagerResult, AsyncResult
from celery.exceptions import TimeoutError
from django.conf import settings
from django.contrib.auth.mixins import AccessMixin
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView

from wot_api import tasks
from wot_api.models import KVStore
from .tasks import test_task


class SuperUserRequiredMixin(AccessMixin):
    """Verify that the current user is a superuser."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(self.request.get_full_path(), self.get_login_url(), self.get_redirect_field_name())
        if not request.user.is_superuser:
            raise PermissionDenied(self.get_permission_denied_message())
        return super().dispatch(request, *args, **kwargs)


class IndexView(SuperUserRequiredMixin, TemplateView):
    template_name = "admin_tools/index.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["wn8_exp_date"] = KVStore.objects.value("expected_values_wn8")
        return data


class TaskViewClass(SuperUserRequiredMixin, View):
    def post(self, request):
        task_type = request.POST.get("type")

        if task_type == "button":
            task = "button_%s" % request.POST.get("task", "_unknown")
            func = getattr(self, task, None)
            if not func:
                text = " ERROR"
                if settings.DEBUG:
                    text += " (function '%s' not found)" % task
                response = {"status": "error", "append_text": text}  # TODO: FIXME: sentry event
            else:
                response = {"status": "ok"}
                result = func(request)  # TODO: FIXME: exception handling für fehler
                if isinstance(result, EagerResult):
                    result = result.result
                if isinstance(result, AsyncResult):
                    wait = request.POST.get("wait", None)
                    if wait:
                        try:
                            result = result.get(timeout=0.5)
                        except TimeoutError:
                            result = {
                                "status": "async",
                                "taskid": result.task_id,
                                "append_text": "ASYNC"
                            }
                    else:
                        result = {
                            "status": "async",
                            "taskid": result.task_id,
                            "append_text": "ASYNC"
                        }

                if isinstance(result, dict):
                    response.update(result)
        else:
            text = " ERROR"
            if settings.DEBUG:
                text += " (unbekannter type: '%s')" % task_type
            response = {"status": "error", "append_text": text}  # TODO: FIXME: sentry event

        return JsonResponse(response)


class TaskView(TaskViewClass):

    def button_update_known_users(self, request):
        tasks.update_known_users()
        return {}

    def button_update_expected_values(self, request):
        tasks.update_expected_values_wn8()
        return {}

    def button_update_clan(self, request):
        tasks.update_default_clan()
        return {}

    def button_update_vehicles(self, request):
        tasks.update_vehicles()
        return {}

    def button_test_task(self, request):
        return test_task.delay()

from django.contrib.auth.mixins import AccessMixin
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.views.generic import TemplateView

from wot_api import tasks


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

    def get(self, request, *args, **kwargs):
        if request.GET.get("update_default_clan"):
            tasks.update_default_clan()
            return redirect("wot_admin_tools:index")

        return super().get(request, *args, **kwargs)

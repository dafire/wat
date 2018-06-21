import uuid

from django.forms.widgets import Textarea


class SimpleMDETextarea(Textarea):
    template_name = 'simplemde/textarea.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['uuid'] = str(uuid.uuid4())
        return context



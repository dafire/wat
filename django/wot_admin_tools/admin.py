# Register your models here.
from django_celery_beat.admin import PeriodicTaskAdmin

PeriodicTaskAdmin.list_display = ('__str__', 'last_run_at', 'total_run_count', 'enabled')

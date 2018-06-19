# Generated by Django 2.0.6 on 2018-06-15 15:11

from django.db import migrations
from django.utils.timezone import now


def create_update_wtr_task(apps, schema_editor):
    periodic_task_model = apps.get_model("django_celery_beat", "PeriodicTask")
    crontab_schedule_model = apps.get_model("django_celery_beat", "CrontabSchedule")

    daily_crontab, _ = crontab_schedule_model.objects.get_or_create(minute=30,
                                                                    hour=6,
                                                                    day_of_week="*",
                                                                    day_of_month="*",
                                                                    month_of_year="*")

    periodic_task_model.objects.get_or_create(name="update web wtr",
                                              task="wot_web_wtr.tasks.update_web_wtr",
                                              crontab=daily_crontab)

    # mark schedule as changed
    periodics_task_model = apps.get_model("django_celery_beat", "PeriodicTasks")
    periodics_task_model.objects.update_or_create(ident=1, defaults={'last_update': now()})


class Migration(migrations.Migration):
    dependencies = [
        ('wot_web_wtr', '0002_webwtrrating_errors'),
    ]

    operations = [
        migrations.RunPython(create_update_wtr_task, migrations.RunPython.noop),
    ]

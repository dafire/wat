# Generated by Django 2.0.4 on 2018-04-20 13:45

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('wot_api', '0006_auto_20180420_1343'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='VehicleStatistics',
            new_name='VehicleStatistic',
        ),
        migrations.RenameModel(
            old_name='VehicleStatisticsItem',
            new_name='VehicleStatisticItem',
        ),
    ]

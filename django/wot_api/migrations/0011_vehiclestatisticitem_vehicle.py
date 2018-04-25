# Generated by Django 2.0.4 on 2018-04-22 09:52

import django.db.models.deletion
from django.db import migrations, models


def move_data(apps, schema_editor):
    vehicle_statistic_item_model = apps.get_model("wot_api", "VehicleStatisticItem")

    objects = vehicle_statistic_item_model.objects.all()
    for object in objects:
        object.vehicle_id = object.tank_id
        object.save()


class Migration(migrations.Migration):
    dependencies = [
        ('wot_api', '0010_expectedwn8values_kvstore'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehiclestatisticitem',
            name='vehicle',
            field=models.ForeignKey(db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING,
                                    to='wot_api.Vehicle'),
            preserve_default=False,
        ),

        migrations.RunPython(move_data, migrations.RunPython.noop),

        migrations.AlterField(
            model_name='vehiclestatisticitem',
            name='vehicle',
            field=models.ForeignKey(db_constraint=False,
                                    null=False,
                                    on_delete=django.db.models.deletion.DO_NOTHING,
                                    to='wot_api.Vehicle'),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='vehiclestatisticitem',
            name='tank_id',
        ),
    ]
# Generated by Django 2.0.4 on 2018-04-22 08:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wot_api', '0009_auto_20180420_1447'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExpectedWN8Values',
            fields=[
                ('vehicle', models.OneToOneField(db_constraint=False, on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to='wot_api.Vehicle')),
                ('exp_damage', models.FloatField()),
                ('exp_def', models.FloatField()),
                ('exp_frag', models.FloatField()),
                ('exp_spot', models.FloatField()),
                ('exp_win_rate', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='KVStore',
            fields=[
                ('key', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('value', models.CharField(max_length=255)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]

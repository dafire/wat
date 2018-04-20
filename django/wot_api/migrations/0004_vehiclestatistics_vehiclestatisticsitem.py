# Generated by Django 2.0.4 on 2018-04-20 13:23

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wot_api', '0003_auto_20180418_1737'),
    ]

    operations = [
        migrations.CreateModel(
            name='VehicleStatistics',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_id', models.IntegerField()),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='VehicleStatisticsItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tank_id', models.IntegerField()),
                ('max_xp', models.IntegerField()),
                ('max_frags', models.IntegerField()),
                ('mark_of_mastery', models.SmallIntegerField()),
                ('clan', django.contrib.postgres.fields.jsonb.JSONField()),
                ('stronghold_skirmish', django.contrib.postgres.fields.jsonb.JSONField()),
                ('regular_team', django.contrib.postgres.fields.jsonb.JSONField()),
                ('team', django.contrib.postgres.fields.jsonb.JSONField()),
                ('globalmap', django.contrib.postgres.fields.jsonb.JSONField()),
                ('company', django.contrib.postgres.fields.jsonb.JSONField()),
                ('stronghold_defense', django.contrib.postgres.fields.jsonb.JSONField()),
                ('all', django.contrib.postgres.fields.jsonb.JSONField()),
                ('statistic_call', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wot_api.VehicleStatistics')),
            ],
        ),
    ]

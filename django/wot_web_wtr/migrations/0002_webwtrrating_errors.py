# Generated by Django 2.0.6 on 2018-06-11 15:26

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wot_web_wtr', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='webwtrrating',
            name='errors',
            field=django.contrib.postgres.fields.jsonb.JSONField(null=True),
        ),
    ]

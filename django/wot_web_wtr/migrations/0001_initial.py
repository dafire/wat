# Generated by Django 2.0.6 on 2018-06-11 15:24

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='WebWtrRating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('battles_count', models.IntegerField()),
                ('tier_group', models.CharField(choices=[('1', 'VIII-X'), ('0', 'All tiers')], max_length=2)),
                ('time_slice', models.CharField(max_length=20)),
                ('date', models.DateTimeField(db_index=True)),
                ('personal', django.contrib.postgres.fields.jsonb.JSONField()),
                ('account', models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL, to_field='account_id')),
            ],
            options={
                'ordering': ['-date'],
                'get_latest_by': 'date',
            },
        ),
    ]
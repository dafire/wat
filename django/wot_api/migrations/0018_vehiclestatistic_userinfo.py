# Generated by Django 2.0.4 on 2018-04-26 14:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wot_api', '0017_vehiclestatistic_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehiclestatistic',
            name='userinfo',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='wot_api.UserInfo'),
        ),
    ]
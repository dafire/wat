# Generated by Django 2.0.4 on 2018-04-20 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wot_api', '0008_vehicle'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicle',
            name='price_credit',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='price_gold',
            field=models.IntegerField(null=True),
        ),
    ]
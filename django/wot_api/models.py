from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models.signals import post_save

from wot_user.models import User


class UserInfo(models.Model):
    account = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        db_constraint=False,
        to_field="account_id",
        swappable=True
    )
    data = JSONField()
    first_of_day = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "<UserInfo %r (%r)>" % (self.account, str(self.created))

    class Meta:
        get_latest_by = "created"


class Vehicle(models.Model):
    tank_id = models.IntegerField(primary_key=True)

    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=200)
    type = models.CharField(max_length=200)

    nation = models.CharField(max_length=200)
    tier = models.SmallIntegerField()

    description = models.TextField()

    tag = models.CharField(max_length=200)
    is_premium = models.BooleanField()
    is_gift = models.BooleanField()
    images = JSONField()

    price_credit = models.IntegerField(null=True)
    price_gold = models.IntegerField(null=True)

    def __str__(self):
        return "<Vehicle (%d) %s>" % (self.tank_id, self.name)


class VehicleStatistic(models.Model):
    account = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        db_constraint=False,
        to_field="account_id",
        swappable=True
    )
    first_of_day = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)


class VehicleStatisticItem(models.Model):
    id = models.BigAutoField(primary_key=True)

    statistic_call = models.ForeignKey(VehicleStatistic, on_delete=models.CASCADE)

    vehicle = models.ForeignKey(Vehicle,
                                db_constraint=False,
                                on_delete=models.DO_NOTHING)

    max_xp = models.IntegerField()
    max_frags = models.IntegerField()

    mark_of_mastery = models.SmallIntegerField()

    clan = JSONField()
    stronghold_skirmish = JSONField()
    regular_team = JSONField()

    team = JSONField()
    globalmap = JSONField()
    company = JSONField()
    stronghold_defense = JSONField()
    all = JSONField()

    def __str__(self):
        return "<VehicleStatsId (%r)>" % (self.vehicle_id,)


class Clan(models.Model):
    name = models.CharField(max_length=100)
    updated = models.DateTimeField(auto_now=True)


class ClanInfo(models.Model):
    clan = models.ForeignKey(
        Clan,
        db_constraint=False,
        on_delete=models.DO_NOTHING,
        null=False
    )

    account = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        to_field="account_id",
        db_constraint=False,
        null=False
    )

    role = models.CharField(max_length=100, editable=False)
    role_i18n = models.CharField(max_length=100, editable=False)
    joined = models.DateTimeField(editable=False)
    updated = models.DateTimeField()

    def __str__(self):
        return "<ClanInfo '%r'>" % self.account_id


class KVStore(models.Model):
    key = models.CharField(max_length=50, primary_key=True)
    value = models.CharField(max_length=255)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "<KVStore %r: %r>" % (self.key, self.value)


class ExpectedWN8Values(models.Model):
    vehicle = models.OneToOneField(Vehicle,
                                   db_constraint=False,
                                   primary_key=True,
                                   on_delete=models.DO_NOTHING,
                                   related_name="expected")
    exp_damage = models.FloatField()
    exp_def = models.FloatField()
    exp_frag = models.FloatField()
    exp_spot = models.FloatField()
    exp_win_rate = models.FloatField()

    def __str__(self):
        return "<ExpectedWN8 Vehicle:%r>" % (self.vehicle_id,)


def create_account_if_needed(sender, instance: ClanInfo, created, **_kwargs):
    if created:
        try:
            instance.account
        except User.DoesNotExist:
            User.objects.create_wot_user(wot_account_id=instance.account_id)


post_save.connect(create_account_if_needed, sender=ClanInfo)

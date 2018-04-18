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
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "<UserInfo %r (%r)>" % (self.account, self.created)

    class Meta:
        get_latest_by = "created"


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


def create_account_if_needed(sender, instance: ClanInfo, created, **_kwargs):
    if created:
        try:
            instance.account
        except User.DoesNotExist:
            User.objects.create_wot_user(wot_account_id=instance.account_id)


post_save.connect(create_account_if_needed, sender=ClanInfo)

import uuid
from django.contrib.auth.base_user import BaseUserManager

from django.contrib.auth.models import AbstractUser
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_wot_user(self, wot_account_id, wot_nickname=""):
        wot_account_id = int(wot_account_id)
        self.create(username="wot_%d" % wot_account_id, account_id=wot_account_id, nickname=wot_nickname)


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account_id = models.IntegerField(null=False, unique=True)
    nickname = models.CharField(max_length=100, null=False, editable=False)

    last_login = models.DateTimeField(null=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    def __str__(self):
        if len(self.nickname):
            return self.nickname
        else:
            return self.username


class AuthToken(models.Model):
    account = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        to_field="account_id",
        swappable=True
    )
    access_token = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    expire = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "<AuthToken '%s'>" % self.account.nickname

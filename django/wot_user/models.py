import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account_id = models.IntegerField(null=False, unique=True)
    nickname = models.CharField(max_length=100, null=False, editable=False)

    last_login = models.DateTimeField(null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "<User '%s'>" % self.nickname


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

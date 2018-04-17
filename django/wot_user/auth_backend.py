from django.contrib.auth import get_user_model
from django.utils import timezone

from wat import settings
from .models import User


class WorldOfTanksSimpleAuth:
    def authenticate(self, request, account_id=None, wot_username=None):
        usermodel: User = get_user_model()
        save_fields = ['last_login']
        if account_id and wot_username:
            try:
                user = usermodel.objects.get(account_id=account_id)
                if user.nickname != wot_username:
                    user.nickname = wot_username
                    save_fields.append("nickname")
            except usermodel.DoesNotExist:
                user = usermodel.objects.create(account_id=account_id,
                                                username="wot_%s" % str(account_id),
                                                nickname=wot_username)
            if str(user.account_id) in settings.WOT_ADMIN_USERS:
                if not user.is_superuser:
                    user.is_staff = True
                    user.is_superuser = True
                    save_fields.append("is_staff")
                    save_fields.append('is_superuser')
            else:
                if user.is_superuser:
                    user.is_staff = False
                    user.is_superuser = False
                    save_fields.append("is_staff")
                    save_fields.append('is_superuser')

            user.last_login = timezone.now()
            user.save(update_fields=save_fields)
            return user

    def get_user(self, user_id):
        try:
            return User.objects.select_related("claninfo").get(pk=user_id)
        except User.DoesNotExist:
            return None

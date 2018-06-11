from django.contrib.postgres.fields import JSONField
from django.db import models

# Create your models here.
from wot_user.models import User


class WebWtrRating(models.Model):
    TIER_GROUPS = (('1', "VIII-X"), ("0", "All tiers"))

    account = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        db_index=True,
        db_constraint=False,
        to_field="account_id",
        swappable=True
    )

    battles_count = models.IntegerField()
    tier_group = models.CharField(max_length=2, choices=TIER_GROUPS)
    time_slice = models.CharField(max_length=20)
    date = models.DateTimeField(db_index=True)
    personal = JSONField()
    errors = JSONField(null=True)

    def __str__(self):
        return "<Stat %r %r>" % (self.account_id, self.date)

    class Meta:
        get_latest_by = "date"
        ordering = ['-date']

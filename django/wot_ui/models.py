from django.db import models


# Create your models here.

class Page(models.Model):
    text = models.TextField()

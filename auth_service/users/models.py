from django.db import models
from django.contrib.auth.hashers import make_password


class User(models.Model):
    first_name = models.CharField()
    last_name = models.CharField(blank=True, null=True)
    patronymic = models.CharField(blank=True, null=True)
    email = models.EmailField(unique=True)
    password = models.CharField()
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        self.password = make_password(self.password)
        super().save(*args, **kwargs)

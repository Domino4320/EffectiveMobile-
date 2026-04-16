from django.db import models
from django.contrib.auth.hashers import make_password
import secrets
from datetime import datetime, timedelta, timezone


class Role(models.Model):
    role_name = models.CharField(unique=True)


class RolePermission(models.Model):
    resourse = models.CharField(unique=True)
    can_update = models.BooleanField(default=True)
    can_delete = models.BooleanField(default=True)
    role_id = models.ForeignKey(Role, on_delete=models.CASCADE)


class User(models.Model):
    first_name = models.CharField()
    last_name = models.CharField(blank=True, null=True)
    patronymic = models.CharField(blank=True, null=True)
    email = models.EmailField(unique=True, db_index=True)
    password = models.CharField()
    is_active = models.BooleanField(default=True)
    role_id = models.ForeignKey(Role, models.SET_DEFAULT, default=1)

    def save(self, *args, **kwargs):
        self.password = make_password(self.password)
        super().save(*args, **kwargs)


class UserToken(models.Model):
    token = models.CharField(unique=True, db_index=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    expire_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        self.expire_at = datetime.now(timezone.utc) + timedelta(days=2)
        self.token = secrets.token_hex(32)
        super().save(*args, **kwargs)

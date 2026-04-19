from django.db import models
import secrets
from datetime import datetime, timedelta, timezone


class AccessLevelChoice(models.IntegerChoices):
    NO_ACCESS = 0, "No access"
    READ = 1, "Read only"
    READ_WRITE = 2, "Read, Write, Update"
    FULL_CRUD = 3, "Read, Write, Update, Delete"
    ADMIN = 4, "Admin access level"


class Role(models.Model):
    role_name = models.CharField(unique=True)
    default_permission_level = models.IntegerField(
        choices=AccessLevelChoice.choices,
        default=AccessLevelChoice.FULL_CRUD,
    )


class Resource(models.Model):
    resource_name = models.CharField(unique=True)


class User(models.Model):
    first_name = models.CharField()
    last_name = models.CharField(blank=True, null=True)
    patronymic = models.CharField(blank=True, null=True)
    email = models.EmailField(unique=True, db_index=True)
    password = models.CharField()
    is_active = models.BooleanField(default=True)
    role = models.ForeignKey(Role, models.SET_DEFAULT, default=1)


class RolePermission(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    access_level = models.IntegerField(
        choices=AccessLevelChoice.choices,
        default=AccessLevelChoice.FULL_CRUD,
    )

    class Meta:
        unique_together = ("resource", "role")


class UserPermission(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    access_level = models.IntegerField(
        choices=AccessLevelChoice.choices,
        default=AccessLevelChoice.FULL_CRUD,
    )

    class Meta:
        unique_together = ("resource", "user")


class UserToken(models.Model):
    token = models.CharField(unique=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expire_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        self.expire_at = datetime.now(timezone.utc) + timedelta(days=2)
        self.token = secrets.token_hex(32)
        super().save(*args, **kwargs)

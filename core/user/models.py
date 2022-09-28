from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class Roles(models.TextChoices):
        USER = 'user'
        MODERATOR = 'moderator'
        ADMIN = 'admin'

    email = models.EmailField(unique=True)
    image_s3_key = models.CharField(max_length=200, null=True, blank=True)
    role = models.CharField(max_length=9, choices=Roles.choices, default=Roles.USER)

    title = models.CharField(max_length=80)
    is_blocked = models.BooleanField(default=False)


# class RefreshToken(models.Model):
#     owner = models.ForeignKey(
#         "user.User", on_delete=models.CASCADE, related_name='refresh')
#     refresh_token = models.CharField(max_length=400)

#     def __str__(self):
#         return self.refresh_token

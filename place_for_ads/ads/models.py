from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


class User(AbstractUser):
    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(_('email address'), unique=True, blank=False)
    REQUIRED_FIELDS = ['email', 'phone']


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

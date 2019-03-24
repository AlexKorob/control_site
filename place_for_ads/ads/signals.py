from .tasks import hide_ad_after_30_days
from django.dispatch import receiver
from django.db.models.signals import post_save
from datetime import datetime
from datetime import timedelta
from celery.task.control import inspect, revoke
from .models import User, Ad
from .utils import prevent_signal_save_recursion


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


@receiver(post_save, sender=Ad)
def create_or_update_ad(sender, instance=None, created=False, **kwargs):
    if not created and not instance.task_id == "":
        revoke(instance.task_id)
    task = hide_ad_after_30_days.apply_async((instance.id, ), eta=datetime.now() + timedelta(days=30))
    Ad.objects.filter(id=instance.id).update(task_id=task.task_id)
    # i = inspect(["celery@worker"])

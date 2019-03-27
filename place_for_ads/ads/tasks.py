from celery import shared_task
from .models import Ad


@shared_task
def hide_ad_after_30_days(id):
    Ad.objects.filter(id=id).update(task_id="", status=Ad.HIDDEN)

# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Article
from .utils import notify_courier

@receiver(post_save, sender=Article)
def article_post_save(sender, instance, **kwargs):
    if kwargs.get('created', False):
        notify_courier(instance)

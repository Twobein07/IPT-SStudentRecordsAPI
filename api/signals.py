import os
import logging
from django.conf import settings
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .encryption import get_or_create_key

logger = logging.getLogger(__name__)


@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    for name in ['Admin', 'Faculty', 'Student']:
        Group.objects.get_or_create(name=name)
    logger.info("Default groups ensured: Admin, Faculty, Student")


@receiver(post_migrate)
def ensure_encryption_key(sender, **kwargs):
    get_or_create_key(settings.SECURE_ENCRYPTION_KEY_FILE)
    logger.info("Encryption key ensured")

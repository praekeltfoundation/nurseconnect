from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from molo.profiles.models import UserProfile as MoloUserProfile


class UserProfile(MoloUserProfile):
    """
    NurseConnect requires a few modifications to the standard way Profiles are
    handled by molo.profiles. This model serves to implement these.
    """
    clinic_code = models.CharField(
        max_length=6,
        blank=True,
        null=True)

    class Meta:
        default_related_name = "for_nurseconnect"


@receiver(post_save, sender=User)
def user_profile_handler(sender, instance, created, **kwargs):
    if created:
        profile = UserProfile(user=instance)
        profile.save()

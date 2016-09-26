from django.db import models

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

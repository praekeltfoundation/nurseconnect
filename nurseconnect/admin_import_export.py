from import_export import resources

from django.contrib.auth.models import User
from import_export.fields import Field
from django.core.exceptions import ObjectDoesNotExist


class FrontendUsersResource(resources.ModelResource):
    """
    Adapted from molo.profiles.
    NurseConnect requires customization of this feature.
    `clinic_code` field also has to be available for export.
    """
    # see dehydrate_ functions below
    clinic_code = Field()

    class Meta:
        model = User

        exclude = ('id', 'password', 'is_superuser', 'groups',
                   'user_permissions', 'is_staff')

        fields = ("username", "clinic_code")

        export_order = ("username", "clinic_code")

    # unfortunately Field's 'attribute' parameter does not work for these
    def dehydrate_clinic_code(self, user):
        try:
            return user.profile.for_nurseconnect.clinic_code
        except ObjectDoesNotExist:
            return None

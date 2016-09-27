from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from phonenumber_field.formfields import PhoneNumberField as \
    ImportedPhoneNumberField
from phonenumber_field.phonenumber import to_python


def validate_international_phonenumber(value):
    phone_number = to_python(value)
    if phone_number and not phone_number.is_valid():
        raise ValidationError(
            _("Please enter a valid South African cellphone number.")
        )


class PhoneNumberField(ImportedPhoneNumberField):
    default_error_messages = {
        "invalid": _("Please enter a valid South African cellphone number."),
    }

    default_validators = [validate_international_phonenumber]

    def to_python(self, value):
        phone_number = to_python(value)
        if phone_number and not phone_number.is_valid():
            raise ValidationError(self.error_messages['invalid'])
        return str(phone_number)

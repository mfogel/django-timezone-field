from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _
from rest_framework.fields import Field

from timezone_field.compat import TimeZoneNotFoundError, to_tzobj
from timezone_field.utils import use_pytz_default


class TimeZoneSerializerField(Field):
    default_error_messages = {
        "invalid": _("A valid timezone is required."),
    }

    def __init__(self, *args, **kwargs):
        self.use_pytz = kwargs.pop("use_pytz", use_pytz_default())
        super().__init__(*args, **kwargs)

    def to_internal_value(self, data):
        data_str = force_str(data)
        try:
            return to_tzobj(data_str, self.use_pytz)
        except TimeZoneNotFoundError:
            self.fail("invalid")

    def to_representation(self, value):
        return str(value)

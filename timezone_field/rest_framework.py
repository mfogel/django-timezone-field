import pytz
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _
from rest_framework.fields import Field

from timezone_field.compat import ZoneInfo, ZoneInfoNotFoundError
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
        if self.use_pytz:
            try:
                return pytz.timezone(data_str)
            except pytz.UnknownTimeZoneError:
                self.fail("invalid")
        else:
            if data_str:
                try:
                    return ZoneInfo(data_str)
                except ZoneInfoNotFoundError:
                    pass
            self.fail("invalid")

    def to_representation(self, value):
        return str(value)

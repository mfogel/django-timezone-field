import zoneinfo

import pytz

import django
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _
from rest_framework.fields import Field

use_tzinfo = django.VERSION >= (4, 0)


class TimeZoneSerializerField(Field):
    default_error_messages = {
        "invalid": _("A valid timezone is required."),
    }

    def __init__(self, *args, **kwargs):
        self.use_pytz = kwargs.pop('use_pytz', not use_tzinfo)
        super().__init__(*args, **kwargs)

    def to_internal_value(self, data):
        if self.use_pytz:
            try:
                return pytz.timezone(force_str(data))
            except pytz.UnknownTimeZoneError:
                self.fail('invalid')
        else:
            try:
                return zoneinfo.ZoneInfo(force_str(data))
            except zoneinfo.ZoneInfoNotFoundError:
                self.fail('invalid')

    def to_representation(self, value):
        return str(value)

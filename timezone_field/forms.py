import django
import pytz
from django import forms
from django.core.exceptions import ValidationError

from timezone_field.choices import standard, with_gmt_offset
from timezone_field.compat import ZoneInfo, ZoneInfoNotFoundError

use_tzinfo = django.VERSION >= (4, 0)


def coerce_to_pytz(val):
    try:
        return pytz.timezone(val)
    except pytz.UnknownTimeZoneError as err:
        raise ValidationError("Unknown time zone: '%s'" % val) from err


def coerce_to_zoneinfo(val):
    try:
        return ZoneInfo(val)
    except ZoneInfoNotFoundError as err:
        raise ValidationError("Unknown time zone: '%s'" % val) from err


class TimeZoneFormField(forms.TypedChoiceField):
    def __init__(self, *args, **kwargs):
        self.use_pytz = kwargs.pop("use_pytz", not use_tzinfo)
        kwargs.setdefault("coerce", coerce_to_pytz if self.use_pytz else coerce_to_zoneinfo)
        kwargs.setdefault("empty_value", None)

        if "choices" in kwargs:
            values, displays = zip(*kwargs["choices"])
        else:
            values = pytz.common_timezones
            displays = None

        choices_display = kwargs.pop("choices_display", None)
        if choices_display == "WITH_GMT_OFFSET":
            choices = with_gmt_offset(values)
        elif choices_display == "STANDARD":
            choices = standard(values)
        elif choices_display is None:
            choices = zip(values, displays) if displays else standard(values)
        else:
            raise ValueError("Unrecognized value for kwarg 'choices_display' of '" + choices_display + "'")

        kwargs["choices"] = choices
        super().__init__(*args, **kwargs)

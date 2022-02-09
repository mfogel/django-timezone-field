import pytz
from django import forms
from django.core.exceptions import ValidationError

from timezone_field.choices import standard, with_gmt_offset
from timezone_field.compat import ZoneInfo, ZoneInfoNotFoundError
from timezone_field.utils import use_pytz_default


def coerce_to_pytz(val):
    try:
        return pytz.timezone(val)
    except pytz.UnknownTimeZoneError as err:
        raise ValidationError(f"Unknown time zone: '{val}'") from err


def coerce_to_zoneinfo(val):
    try:
        return ZoneInfo(val)
    except ZoneInfoNotFoundError as err:
        raise ValidationError(f"Unknown time zone: '{val}'") from err


class TimeZoneFormField(forms.TypedChoiceField):
    def __init__(self, *args, **kwargs):
        self.use_pytz = kwargs.pop("use_pytz", use_pytz_default())
        kwargs.setdefault("coerce", coerce_to_pytz if self.use_pytz else coerce_to_zoneinfo)
        kwargs.setdefault("empty_value", None)

        if "choices" in kwargs:
            values, displays = zip(*kwargs["choices"])
        else:
            values = pytz.common_timezones
            displays = None

        choices_display = kwargs.pop("choices_display", None)
        if choices_display == "WITH_GMT_OFFSET":
            choices = with_gmt_offset(values, use_pytz=self.use_pytz)
        elif choices_display == "STANDARD":
            choices = standard(values)
        elif choices_display is None:
            choices = zip(values, displays) if displays else standard(values)
        else:
            raise ValueError(f"Unrecognized value for kwarg 'choices_display' of '{choices_display}'")

        kwargs["choices"] = choices
        super().__init__(*args, **kwargs)

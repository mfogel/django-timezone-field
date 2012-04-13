from django import forms

from timezones import zones
from timezones.utils import coerce_timezone_value


class TimeZoneField(forms.TypedChoiceField):
    def __init__(self, *args, **kwargs):
        if not "choices" in kwargs:
            kwargs["choices"] = zones.PRETTY_TIMEZONE_CHOICES
        kwargs["coerce"] = coerce_timezone_value
        super(TimeZoneField, self).__init__(*args, **kwargs)

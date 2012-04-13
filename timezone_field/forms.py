from django import forms

from timezone_field import zones
from timezone_field.utils import coerce_timezone_value


class TimeZoneField(forms.TypedChoiceField):
    def __init__(self, *args, **kwargs):
        if not "choices" in kwargs:
            kwargs["choices"] = zones.PRETTY_TIMEZONE_CHOICES
        kwargs["coerce"] = coerce_timezone_value
        super(TimeZoneField, self).__init__(*args, **kwargs)

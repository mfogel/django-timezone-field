import pytz

from django import forms

from timezone_field import zones


class TimeZoneField(forms.TypedChoiceField):
    def __init__(self, *args, **kwargs):
        if not "choices" in kwargs:
            kwargs["choices"] = zones.PRETTY_TIMEZONE_CHOICES
        kwargs["coerce"] = pytz.timezone
        super(TimeZoneField, self).__init__(*args, **kwargs)

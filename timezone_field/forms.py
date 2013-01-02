import pytz
from django import forms


class TimeZoneFormField(forms.TypedChoiceField):
    def __init__(self, *args, **kwargs):
        defaults = {
            'coerce': lambda val: pytz.timezone(val),
            'choices': [(tz, tz) for tz in pytz.all_timezones],
            'empty_value': None,
        }
        defaults.update(kwargs)
        super(TimeZoneFormField, self).__init__(*args, **defaults)


import pytz

from django.conf import settings
from django import newforms as forms

from timezones.utils import adjust_datetime_to_timezone

TIMEZONE_CHOICES = tuple(zip(pytz.all_timezones, pytz.all_timezones))

class TimeZoneField(forms.ChoiceField):
    def __init__(self, choices=None, *args, **kwdargs):
        if choices is not None:
            kwdargs['choices'] = choices
        else:
            kwdargs['choices'] = TIMEZONE_CHOICES
        super(TimeZoneField, self).__init__(*args, **kwdargs)

    def clean(self, value):
        value = super(TimeZoneField, self).clean(value)
        return pytz.timezone(value)

class LocalizedDateTimeField(forms.DateTimeField):
    """
    Converts the datetime from the user timezone to settings.TIME_ZONE.
    """
    def __init__(self, timezone=None, *args, **kwargs):
        super(LocalizedDateTimeField, self).__init__(*args, **kwargs)
        self.timezone = timezone or settings.TIME_ZONE

    def clean(self, value):
        value = super(LocalizedDateTimeField, self).clean(value)
        return adjust_datetime_to_timezone(value, from_tz=self.timezone)

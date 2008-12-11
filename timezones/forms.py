
import pytz
import datetime

from django.conf import settings
from django import forms

from timezones.utils import adjust_datetime_to_timezone

ALL_TIMEZONE_CHOICES = tuple(zip(pytz.all_timezones, pytz.all_timezones))
COMMON_TIMEZONE_CHOICES = tuple(zip(pytz.common_timezones, pytz.common_timezones))
PRETTY_TIMEZONE_CHOICES = []
for tz in pytz.common_timezones:
    now = datetime.datetime.now(pytz.timezone(tz))
    PRETTY_TIMEZONE_CHOICES.append((tz, "(GMT%s) %s" % (now.strftime("%z"), tz)))

class TimeZoneField(forms.ChoiceField):
    def __init__(self, choices=None,  max_length=None, min_length=None,
                 *args, **kwargs):
        self.max_length, self.min_length = max_length, min_length
        if choices is not None:
            kwargs["choices"] = choices
        else:
            kwargs["choices"] = PRETTY_TIMEZONE_CHOICES
        super(TimeZoneField, self).__init__(*args, **kwargs)

    def clean(self, value):
        value = super(TimeZoneField, self).clean(value)
        if value:
            return pytz.timezone(value)
        else:
            return value

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

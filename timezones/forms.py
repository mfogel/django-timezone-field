
import pytz
import datetime

from django.conf import settings
from django import forms

from timezones.utils import adjust_datetime_to_timezone, coerce_timezone_value

ALL_TIMEZONE_CHOICES = tuple(zip(pytz.all_timezones, pytz.all_timezones))
COMMON_TIMEZONE_CHOICES = tuple(zip(pytz.common_timezones, pytz.common_timezones))
PRETTY_TIMEZONE_CHOICES = []
for tz in pytz.common_timezones:
    now = datetime.datetime.now(pytz.timezone(tz))
    PRETTY_TIMEZONE_CHOICES.append((tz, "(GMT%s) %s" % (now.strftime("%z"), tz)))

class TimeZoneField(forms.TypedChoiceField):
    def __init__(self, *args, **kwargs):
        if not "choices" in kwargs:
            kwargs["choices"] = PRETTY_TIMEZONE_CHOICES
        kwargs["coerce"] = coerce_timezone_value
        super(TimeZoneField, self).__init__(*args, **kwargs)


class LocalizedDateTimeField(forms.DateTimeField):
    """
    Converts the datetime from the user timezone to settings.TIME_ZONE.
    """
    def __init__(self, timezone=None, *args, **kwargs):
        super(LocalizedDateTimeField, self).__init__(*args, **kwargs)
        self.timezone = timezone or settings.TIME_ZONE
        
    def clean(self, value):
        value = super(LocalizedDateTimeField, self).clean(value)
        if value is None: # field was likely not required
            return None
        return adjust_datetime_to_timezone(value, from_tz=self.timezone)

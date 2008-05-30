
import pytz

from django.conf import settings
from django import newforms as forms

class LocalizedDateTimeField(forms.DateTimeField):
    """
    Converts the datetime from the user timezone to settings.TIME_ZONE.
    """
    def __init__(self, timezone, *args, **kwargs):
        self.tz = pytz.timezone(timezone)
        super(LocalizedDateTimeField, self).__init__(*args, **kwargs)
        
    def clean(self, value):
        value = super(LocalizedDateTimeField, self).clean(value)
        return self.tz.localize(value).astimezone(pytz.timezone(settings.TIME_ZONE))

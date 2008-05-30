
import pytz

from django.conf import settings
from django import newforms as forms

class LocalizedDateTimeField(forms.DateTimeField):
    """
    Converts the datetime from the user timezone to settings.TIME_ZONE.
    """
    def __init__(self, timezone=None, *args, **kwargs):
        super(LocalizedDateTimeField, self).__init__(*args, **kwargs)
        self.tz = pytz.timezone(timezone or settings.TIME_ZONE)
        
    def clean(self, value):
        value = super(LocalizedDateTimeField, self).clean(value)
        return self.tz.localize(value).astimezone(pytz.timezone(settings.TIME_ZONE))
